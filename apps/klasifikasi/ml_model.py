# apps/klasifikasi/ml_model.py - WITH INDONESIAN PATTERN ADJUSTMENT

"""
RoBERTa Model Integration for Bloom's Taxonomy Classification
Now includes Indonesian pattern-based adjustment
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import sigmoid
from deep_translator import GoogleTranslator
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

# Import Indonesian adjuster if available
try:
    from .indonesian_rules import IndonesianBloomAdjuster
    ADJUSTER_AVAILABLE = True
    logger.info("Indonesian pattern adjuster loaded")
except ImportError:
    ADJUSTER_AVAILABLE = False
    logger.warning("Indonesian adjuster not available")


class BloomClassifier:
    """
    Wrapper class for RoBERTa-based Bloom's Taxonomy classifier
    With Indonesian pattern-based adjustment
    """
    
    # Label mapping
    LABEL_COLUMNS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
    LABEL_TO_CATEGORY = {
        "Remember": "C1",
        "Understand": "C2",
        "Apply": "C3",
        "Analyze": "C4",
        "Evaluate": "C5",
        "Create": "C6"
    }
    
    # Classification threshold
    THRESHOLD = 0.5
    
    def __init__(self, model_path=None, use_indonesian_adjuster=True):
        """
        Initialize the classifier
        
        Args:
            model_path: Path to the model directory (default: settings.MODEL_PATH)
            use_indonesian_adjuster: Whether to use pattern-based adjustment
        """
        self.model_path = model_path or getattr(settings, 'BLOOM_MODEL_PATH', './roberta_multilabel')
        self.tokenizer = None
        self.model = None
        self.translator = GoogleTranslator(source='id', target='en')
        self.is_loaded = False
        
        # Indonesian adjuster
        self.use_adjuster = use_indonesian_adjuster and ADJUSTER_AVAILABLE
        if self.use_adjuster:
            self.adjuster = IndonesianBloomAdjuster()
            logger.info("Indonesian pattern adjuster enabled")
        else:
            self.adjuster = None
            if use_indonesian_adjuster:
                logger.warning("Indonesian adjuster requested but not available")
        
    def load_model(self):
        """Load the model and tokenizer"""
        if self.is_loaded:
            return True
            
        try:
            logger.info(f"Loading model from {self.model_path}")
            
            # Verify model files exist
            model_dir = Path(self.model_path)
            required_files = ['config.json', 'model.safetensors', 'tokenizer.json']
            
            for file in required_files:
                if not (model_dir / file).exists():
                    raise FileNotFoundError(f"Required file not found: {file}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            
            # Set to evaluation mode
            self.model.eval()
            
            self.is_loaded = True
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}", exc_info=True)
            self.is_loaded = False
            return False
    
    def translate_text(self, text, src="id", dest="en"):
        """
        Translate text from Indonesian to English
        
        Args:
            text: Text to translate
            src: Source language (default: Indonesian)
            dest: Destination language (default: English)
            
        Returns:
            Translated text or original if translation fails
        """
        try:
            # Use deep_translator which is more stable
            if src != 'id' or dest != 'en':
                self.translator = GoogleTranslator(source=src, target=dest)
            
            translated = self.translator.translate(text)
            logger.debug(f"Translation: '{text[:50]}...' -> '{translated[:50]}...'")
            return translated
        except Exception as e:
            logger.warning(f"Translation failed: {e}. Using original text.")
            return text
    
    def predict_single(self, text, translate=True, original_text=None):
        """
        Predict Bloom's taxonomy category for a single question
        WITH INDONESIAN PATTERN ADJUSTMENT
        
        Args:
            text: Question text (can be Indonesian or English)
            translate: Whether to translate from Indonesian to English
            original_text: Original Indonesian text (for pattern matching)
            
        Returns:
            dict: {
                'category': 'C1-C6',
                'category_name': 'Remember/Understand/etc',
                'confidence': float (0-1),
                'all_probabilities': dict of all category probabilities,
                'was_adjusted': bool (whether Indonesian patterns adjusted the result)
            }
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        try:
            # Store original for pattern matching
            if original_text is None:
                original_text = text
            
            # Translate if needed
            if translate:
                text = self.translate_text(text, src="id", dest="en")
            
            # Tokenize
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            )
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = sigmoid(outputs.logits).numpy()[0]
            
            # Build results dictionary
            all_probs = {}
            for label, prob in zip(self.LABEL_COLUMNS, probs):
                all_probs[label] = {
                    "probability": float(prob),
                    "predicted": prob >= self.THRESHOLD
                }
            
            # Determine primary category (highest probability)
            max_label = max(all_probs.items(), key=lambda x: x[1]['probability'])[0]
            category = self.LABEL_TO_CATEGORY[max_label]
            confidence = all_probs[max_label]['probability']
            
            # Create ML prediction
            ml_result = {
                'category': category,
                'category_name': max_label,
                'confidence': confidence,
                'all_probabilities': all_probs,
                'translated_text': text if translate else None
            }
            
            # Apply Indonesian pattern adjustment if enabled
            if self.use_adjuster and translate:
                adjusted_result = self.adjuster.adjust_classification(
                    original_text, 
                    ml_result
                )
                
                # Check if adjustment was made
                was_adjusted = (
                    adjusted_result['category'] != ml_result['category'] or
                    abs(adjusted_result['confidence'] - ml_result['confidence']) > 0.05
                )
                
                adjusted_result['was_adjusted'] = was_adjusted
                adjusted_result['ml_category'] = ml_result['category']
                adjusted_result['ml_confidence'] = ml_result['confidence']
                
                if was_adjusted:
                    logger.info(
                        f"Adjusted: {ml_result['category']}({ml_result['confidence']:.2f}) -> "
                        f"{adjusted_result['category']}({adjusted_result['confidence']:.2f})"
                    )
                
                return adjusted_result
            else:
                ml_result['was_adjusted'] = False
                return ml_result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            raise
    
    def predict_batch(self, texts, translate=True, batch_size=8):
        """
        Predict categories for multiple questions
        WITH INDONESIAN PATTERN ADJUSTMENT
        
        Args:
            texts: List of question texts
            translate: Whether to translate from Indonesian to English
            batch_size: Number of texts to process at once
            
        Returns:
            List of prediction dictionaries (same format as predict_single)
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        results = []
        
        try:
            # Store originals for pattern matching
            original_texts = texts.copy()
            
            # Translate all texts if needed
            if translate:
                logger.info(f"Translating {len(texts)} texts...")
                translated_texts = []
                for text in texts:
                    try:
                        translated = self.translate_text(text, src="id", dest="en")
                        translated_texts.append(translated)
                    except Exception as e:
                        logger.warning(f"Translation failed for text, using original: {e}")
                        translated_texts.append(text)
            else:
                translated_texts = texts
            
            # Process in batches
            for i in range(0, len(translated_texts), batch_size):
                batch = translated_texts[i:i + batch_size]
                batch_originals = original_texts[i:i + batch_size]
                
                # Tokenize batch
                inputs = self.tokenizer(
                    batch,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding=True
                )
                
                # Predict
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    probs_batch = sigmoid(outputs.logits).numpy()
                
                # Process each prediction in batch
                for j, (probs, original) in enumerate(zip(probs_batch, batch_originals)):
                    all_probs = {}
                    for label, prob in zip(self.LABEL_COLUMNS, probs):
                        all_probs[label] = {
                            "probability": float(prob),
                            "predicted": prob >= self.THRESHOLD
                        }
                    
                    # Determine primary category
                    max_label = max(all_probs.items(), key=lambda x: x[1]['probability'])[0]
                    category = self.LABEL_TO_CATEGORY[max_label]
                    confidence = all_probs[max_label]['probability']
                    
                    # Create ML prediction
                    ml_result = {
                        'category': category,
                        'category_name': max_label,
                        'confidence': confidence,
                        'all_probabilities': all_probs,
                        'translated_text': batch[j] if translate else None,
                        'original_text': original
                    }
                    
                    # Apply Indonesian pattern adjustment if enabled
                    if self.use_adjuster and translate:
                        adjusted_result = self.adjuster.adjust_classification(
                            original,
                            ml_result
                        )
                        
                        # Check if adjustment was made
                        was_adjusted = (
                            adjusted_result['category'] != ml_result['category'] or
                            abs(adjusted_result['confidence'] - ml_result['confidence']) > 0.05
                        )
                        
                        adjusted_result['was_adjusted'] = was_adjusted
                        adjusted_result['ml_category'] = ml_result['category']
                        adjusted_result['ml_confidence'] = ml_result['confidence']
                        adjusted_result['original_text'] = original
                        
                        results.append(adjusted_result)
                    else:
                        ml_result['was_adjusted'] = False
                        results.append(ml_result)
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            # Log adjustment statistics
            if self.use_adjuster:
                adjusted_count = sum(1 for r in results if r.get('was_adjusted', False))
                logger.info(
                    f"Batch prediction completed: {len(results)} questions classified, "
                    f"{adjusted_count} adjusted by Indonesian patterns"
                )
            else:
                logger.info(f"Batch prediction completed: {len(results)} questions classified")
            
            return results
            
        except Exception as e:
            logger.error(f"Batch prediction error: {str(e)}", exc_info=True)
            raise
    
    def get_model_info(self):
        """Get information about the loaded model"""
        if not self.is_loaded:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_path": str(self.model_path),
            "labels": self.LABEL_COLUMNS,
            "threshold": self.THRESHOLD,
            "model_type": "RoBERTa",
            "max_length": 512,
            "indonesian_adjuster": self.use_adjuster
        }


# Global classifier instance (singleton pattern)
_classifier_instance = None

def get_classifier(use_indonesian_adjuster=True):
    """
    Get or create the global classifier instance
    
    Args:
        use_indonesian_adjuster: Whether to enable Indonesian pattern adjustment
    
    Returns:
        BloomClassifier instance
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = BloomClassifier(use_indonesian_adjuster=use_indonesian_adjuster)
        _classifier_instance.load_model()
    return _classifier_instance


# Convenience functions for direct use

def classify_question(text, translate=True):
    """
    Classify a single question
    
    Args:
        text: Question text
        translate: Whether to translate from Indonesian
        
    Returns:
        Prediction dictionary
    """
    classifier = get_classifier()
    return classifier.predict_single(text, translate=translate)


def classify_questions_batch(texts, translate=True, batch_size=8):
    """
    Classify multiple questions
    
    Args:
        texts: List of question texts
        translate: Whether to translate from Indonesian
        batch_size: Batch size for processing
        
    Returns:
        List of prediction dictionaries
    """
    classifier = get_classifier()
    return classifier.predict_batch(texts, translate=translate, batch_size=batch_size)