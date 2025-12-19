"""
Question Regeneration Utility Module
Handles transformation of questions across Bloom's Taxonomy levels
Using Hybrid Strategy: Rule-Based Templates > AI Model > Fallback
"""

import torch
import logging
from pathlib import Path
from typing import Optional, List, Dict
from transformers import T5ForConditionalGeneration, AutoTokenizer
from peft import PeftModel

# Import Rule-Based System yang baru dibuat
from .regenerate_rules import smart_regenerator

logger = logging.getLogger(__name__)


class QuestionRegenerator:
    """
    Regenerate/Transform questions across Bloom's Taxonomy levels (C1-C6)
    Uses a hybrid approach: Template Injection + T5 LoRA Model
    """
    
    def __init__(self, base_model_name: str = "t5-small", 
                 lora_model_path: Optional[str] = None):
        """
        Initialize the Question Regenerator
        
        Args:
            base_model_name: Base T5 model name (default: t5-small)
            lora_model_path: Path to LoRA adapter weights
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.base_model_name = base_model_name
        self.model = None
        self.tokenizer = None
        self.lora_model_path = lora_model_path
        
        logger.info(f"QuestionRegenerator initialized. Device: {self.device}")
        self._load_model()
    
    def _load_model(self):
        """Load base model and LoRA adapters if available"""
        try:
            logger.info(f"Loading base model: {self.base_model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
            base_model = T5ForConditionalGeneration.from_pretrained(self.base_model_name)
            
            # Load LoRA adapters if path is provided and exists
            if self.lora_model_path and Path(self.lora_model_path).exists():
                try:
                    logger.info(f"Loading LoRA adapters from: {self.lora_model_path}")
                    self.model = PeftModel.from_pretrained(base_model, self.lora_model_path)
                    self.model.eval()
                    logger.info("LoRA model loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load LoRA adapters: {e}. Using base model only.")
                    self.model = base_model
                    self.model.eval()
            else:
                logger.info("No LoRA adapters found/provided. Using base model only.")
                self.model = base_model
                self.model.eval()
            
            self.model.to(self.device)
            logger.info("Model loaded and moved to device successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # We don't raise error here to allow rule-based to work even if AI fails
            self.model = None
    
    def transform_question(self, 
                           question: str, 
                           source_level: str, 
                           target_level: str,
                           max_length: int = 512,
                           num_beams: int = 4,
                           temperature: float = 0.7) -> str:
        """
        Transform a question from one Bloom level to another.
        
        STRATEGY PRIORITY:
        1. Smart Rule-Based (Template Injection) -> Best for grammar & structure.
        2. T5 AI Model -> Best for complex context when rules fail.
        3. Simple Fallback -> Safe failover.
        """
        
        # Validate levels
        valid_levels = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        if source_level not in valid_levels or target_level not in valid_levels:
            raise ValueError(f"Invalid level. Must be one of: {valid_levels}")
        
        # Same level - return original
        if source_level == target_level:
            logger.info(f"Source and target levels same ({source_level}). Returning original.")
            return question
        
        # --- STRATEGY 1: Smart Rule-Based Regeneration ---
        try:
            # Menggunakan sistem ekstraksi topik & template
            rule_based_result = smart_regenerator.generate_question(question, target_level)
            
            if rule_based_result:
                logger.info(f"✅ Rule-Based Success: {source_level}->{target_level}")
                return rule_based_result
            else:
                logger.debug("Rule-based extraction returned None (topic too short/complex).")
                
        except Exception as e:
            logger.warning(f"Rule-based regeneration warning: {e}")

        # --- STRATEGY 2: T5 AI Model (Deep Learning) ---
        if self.model is not None:
            try:
                # Prepare input prompt
                input_text = f"transform {source_level} to {target_level}: {question}"
                
                # Tokenize
                inputs = self.tokenizer(
                    input_text,
                    return_tensors="pt",
                    max_length=512,
                    truncation=True
                ).to(self.device)
                
                # Generate with beam search for quality
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        num_beams=num_beams,
                        temperature=temperature,
                        early_stopping=True,
                        do_sample=False,
                        repetition_penalty=1.2 # Prevent repeating phrases
                    )
                
                # Decode
                transformed = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Validate output (ensure it's not empty or nonsense)
                if transformed and len(transformed.strip()) > 5:
                    logger.info(f"🤖 AI Model Success: {transformed}")
                    return transformed.strip()
                    
            except Exception as e:
                logger.error(f"AI generation failed: {e}")
        else:
            logger.warning("AI Model not loaded, skipping Strategy 2.")

        # --- STRATEGY 3: Fallback (Rule-Based Prefix) ---
        return self._fallback_transform(question, source_level, target_level)
    
    def _fallback_transform(self, question: str, source_level: str, target_level: str) -> str:
        """
        Fallback transformation when both Smart Rules and AI fail.
        Just prepends a relevant verb/prefix.
        """
        logger.info(f"⚠️ Using fallback transformation")
        
        # Simple rule-based transformations as fallback
        prefixes = {
            'C1': 'Definisikan/Sebutkan:',
            'C2': 'Jelaskan/Uraikan:',
            'C3': 'Terapkan/Demonstrasikan:',
            'C4': 'Analisis/Bandingkan:',
            'C5': 'Evaluasi/Nilailah:',
            'C6': 'Rancanglah/Buatlah:',
        }
        
        # Detect simple english (optional enhancement for fallback)
        is_english = any(w in question.lower() for w in ['the', 'what', 'how', 'explain'])
        if is_english:
            prefixes = {
                'C1': 'Define/List:',
                'C2': 'Explain/Describe:',
                'C3': 'Apply/Demonstrate:',
                'C4': 'Analyze/Compare:',
                'C5': 'Evaluate/Assess:',
                'C6': 'Design/Create:',
            }
        
        prefix = prefixes.get(target_level, target_level)
        return f"{prefix} {question}"
    
    def batch_transform(self, 
                        questions: List[str],
                        source_levels: List[str],
                        target_levels: List[str]) -> List[str]:
        """
        Transform multiple questions at once
        """
        if not (len(questions) == len(source_levels) == len(target_levels)):
            raise ValueError("All input lists must have same length")
        
        results = []
        for q, src, tgt in zip(questions, source_levels, target_levels):
            try:
                transformed = self.transform_question(q, src, tgt)
                results.append(transformed)
            except Exception as e:
                logger.error(f"Failed to transform question in batch: {e}")
                results.append(q)  # Return original on error
        
        return results


# Global instance (lazy loaded)
_regenerator_instance: Optional[QuestionRegenerator] = None


def get_regenerator() -> QuestionRegenerator:
    """
    Get or create the global QuestionRegenerator instance
    Implements lazy loading pattern
    """
    global _regenerator_instance
    
    if _regenerator_instance is None:
        # Try to find LoRA model path
        # Assumes the folder 'regenerate_t5_lora' is in the same directory as this file
        lora_path = None
        apps_path = Path(__file__).parent
        potential_lora_path = apps_path / "regenerate_t5_lora"
        
        if potential_lora_path.exists():
            lora_path = str(potential_lora_path)
            logger.info(f"Found LoRA model at: {lora_path}")
        else:
            logger.warning(f"LoRA model folder not found at {potential_lora_path}. Using base T5 only.")
        
        _regenerator_instance = QuestionRegenerator(
            base_model_name="t5-small",
            lora_model_path=lora_path
        )
    
    return _regenerator_instance


def regenerate_question(question: str, source_level: str, target_level: str) -> Dict[str, str]:
    """
    Convenience function to regenerate a single question.
    This is the function called by views.py
    """
    try:
        regenerator = get_regenerator()
        transformed = regenerator.transform_question(question, source_level, target_level)
        
        return {
            'success': True,
            'original': question,
            'transformed': transformed,
            'source_level': source_level,
            'target_level': target_level,
            'error': None
        }
    except Exception as e:
        logger.error(f"Error regenerating question: {e}")
        return {
            'success': False,
            'original': question,
            'transformed': None,
            'source_level': source_level,
            'target_level': target_level,
            'error': str(e)
        }