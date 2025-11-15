"""
RoBERTa Model Integration for Bloom's Taxonomy Classification
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import sigmoid
from deep_translator import GoogleTranslator
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

class BloomClassifier:
    """
    Wrapper class for RoBERTa-based Bloom's Taxonomy classifier
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
    
    def __init__(self, model_path=None):
        """
        Initialize the classifier
        
        Args:
            model_path: Path to the model directory (default: settings.MODEL_PATH)
        """
        self.model_path = model_path or getattr(settings, 'BLOOM_MODEL_PATH', './roberta_multilabel')
        self.tokenizer = None
        self.model = None
        self.translator = GoogleTranslator(source='id', target='en')
        self.is_loaded = False
        
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
    
    def predict_single(self, text, translate=True):
        """
        Predict Bloom's taxonomy category for a single question
        
        Args:
            text: Question text
            translate: Whether to translate from Indonesian to English
            
        Returns:
            dict: {
                'category': 'C1-C6',
                'category_name': 'Remember/Understand/etc',
                'confidence': float (0-1),
                'all_probabilities': dict of all category probabilities
            }
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        try:
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
            
            result = {
                'category': category,
                'category_name': max_label,
                'confidence': confidence,
                'all_probabilities': all_probs,
                'translated_text': text if translate else None
            }
            
            logger.debug(f"Prediction: {category} ({max_label}) with confidence {confidence:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            raise
    
    def predict_batch(self, texts, translate=True, batch_size=8):
        """
        Predict categories for multiple questions
        
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
            # Translate all texts if needed
            if translate:
                logger.info(f"Translating {len(texts)} texts...")
                translated_texts = [self.translate_text(text, src="id", dest="en") for text in texts]
            else:
                translated_texts = texts
            
            # Process in batches
            for i in range(0, len(translated_texts), batch_size):
                batch = translated_texts[i:i + batch_size]
                
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
                for j, probs in enumerate(probs_batch):
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
                    
                    result = {
                        'category': category,
                        'category_name': max_label,
                        'confidence': confidence,
                        'all_probabilities': all_probs,
                        'translated_text': batch[j] if translate else None,
                        'original_text': texts[i + j]
                    }
                    
                    results.append(result)
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
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
            "max_length": 512
        }


# Global classifier instance (singleton pattern)
_classifier_instance = None

def get_classifier():
    """
    Get or create the global classifier instance
    
    Returns:
        BloomClassifier instance
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = BloomClassifier()
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