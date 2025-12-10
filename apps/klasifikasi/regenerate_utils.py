"""
Question Regeneration Utility Module
Handles transformation of questions across Bloom's Taxonomy levels
"""

import torch
import logging
from pathlib import Path
from typing import Optional, List, Dict
from transformers import T5ForConditionalGeneration, AutoTokenizer
from peft import PeftModel

logger = logging.getLogger(__name__)


class QuestionRegenerator:
    """
    Regenerate/Transform questions across Bloom's Taxonomy levels (C1-C6)
    Uses a pre-trained T5 model with LoRA adapters
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
            
            # Load LoRA adapters if path is provided
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
                logger.info("No LoRA adapters found. Using base model only.")
                self.model = base_model
                self.model.eval()
            
            self.model.to(self.device)
            logger.info("Model loaded and moved to device successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Could not load model: {e}")
    
    def transform_question(self, 
                          question: str, 
                          source_level: str, 
                          target_level: str,
                          max_length: int = 512,
                          num_beams: int = 4,
                          temperature: float = 0.7) -> str:
        """
        Transform a question from one Bloom level to another
        
        Args:
            question: The input question text
            source_level: Current Bloom level (C1-C6)
            target_level: Desired Bloom level (C1-C6)
            max_length: Maximum length for generated text
            num_beams: Beam search width
            temperature: Sampling temperature (lower = more deterministic)
            
        Returns:
            Transformed question text
            
        Raises:
            ValueError: If model is not loaded or invalid levels provided
            RuntimeError: If transformation fails
        """
        if self.model is None:
            raise ValueError("Model not loaded. Check model loading logs.")
        
        # Validate levels
        valid_levels = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        if source_level not in valid_levels or target_level not in valid_levels:
            raise ValueError(f"Invalid level. Must be one of: {valid_levels}")
        
        # Same level - return original
        if source_level == target_level:
            logger.info(f"Source and target levels same ({source_level}). Returning original question.")
            return question
        
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
            
            # Generate with beam search
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=num_beams,
                    temperature=temperature,
                    early_stopping=True,
                    do_sample=False,  # Use beam search for consistency
                    repetition_penalty=1.2  # Penalize repetition
                )
            
            # Decode
            transformed = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Validate output
            if not transformed or len(transformed.strip()) < 5:
                logger.warning(f"Generated text too short: {transformed}. Returning modified original.")
                # Fallback: return modified version of original
                return self._fallback_transform(question, source_level, target_level)
            
            logger.info(f"Successfully transformed question from {source_level} to {target_level}")
            return transformed.strip()
            
        except Exception as e:
            logger.error(f"Error during transformation: {e}")
            # Fallback to simple transformation
            return self._fallback_transform(question, source_level, target_level)
    
    def _fallback_transform(self, question: str, source_level: str, target_level: str) -> str:
        """
        Fallback transformation when model fails
        Uses rule-based modifications based on Bloom's levels
        
        Args:
            question: Original question
            source_level: Current level
            target_level: Target level
            
        Returns:
            Modified question
        """
        logger.info(f"Using fallback transformation from {source_level} to {target_level}")
        
        # Simple rule-based transformations as fallback
        prefixes = {
            'C1': 'Define, Identify, List, Recall',
            'C2': 'Explain, Describe, Summarize, Classify',
            'C3': 'Apply, Solve, Demonstrate, Illustrate',
            'C4': 'Analyze, Compare, Contrast, Distinguish',
            'C5': 'Judge, Evaluate, Argue, Defend',
            'C6': 'Create, Design, Synthesize, Develop',
        }
        
        # Just add a prefix indicating the new level
        prefix = prefixes.get(target_level, target_level)
        return f"{prefix}: {question}"
    
    def batch_transform(self, 
                       questions: List[str],
                       source_levels: List[str],
                       target_levels: List[str]) -> List[str]:
        """
        Transform multiple questions at once
        
        Args:
            questions: List of question texts
            source_levels: List of source levels
            target_levels: List of target levels
            
        Returns:
            List of transformed questions
        """
        if not (len(questions) == len(source_levels) == len(target_levels)):
            raise ValueError("All input lists must have same length")
        
        results = []
        for q, src, tgt in zip(questions, source_levels, target_levels):
            try:
                transformed = self.transform_question(q, src, tgt)
                results.append(transformed)
            except Exception as e:
                logger.error(f"Failed to transform question: {e}")
                results.append(q)  # Return original on error
        
        return results


# Global instance (lazy loaded)
_regenerator_instance: Optional[QuestionRegenerator] = None


def get_regenerator() -> QuestionRegenerator:
    """
    Get or create the global QuestionRegenerator instance
    Implements lazy loading pattern
    
    Returns:
        QuestionRegenerator instance
    """
    global _regenerator_instance
    
    if _regenerator_instance is None:
        # Try to find LoRA model path
        lora_path = None
        apps_path = Path(__file__).parent
        potential_lora_path = apps_path / "regenerate_t5_lora"
        
        if potential_lora_path.exists():
            lora_path = str(potential_lora_path)
            logger.info(f"Found LoRA model at: {lora_path}")
        
        _regenerator_instance = QuestionRegenerator(
            base_model_name="t5-small",
            lora_model_path=lora_path
        )
    
    return _regenerator_instance


def regenerate_question(question: str, source_level: str, target_level: str) -> Dict[str, str]:
    """
    Convenience function to regenerate a single question
    
    Args:
        question: Question text to transform
        source_level: Current Bloom level
        target_level: Target Bloom level
        
    Returns:
        Dictionary with 'original', 'transformed', 'source_level', 'target_level'
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
