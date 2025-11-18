# apps/klasifikasi/ml_model.py - COMPLETE WITH CONSISTENCY IMPROVEMENTS

"""
RoBERTa Model Integration for Bloom's Taxonomy Classification
WITH Indonesian and English pattern-based adjustment
WITH Consistency improvements and confidence boosting
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import sigmoid
from deep_translator import GoogleTranslator
import logging
from pathlib import Path
from django.conf import settings
import re

logger = logging.getLogger(__name__)

# Import BOTH pattern adjusters
try:
    from .indonesian_rules import IndonesianBloomAdjuster
    INDONESIAN_ADJUSTER_AVAILABLE = True
    logger.info("✓ Indonesian pattern adjuster loaded")
except ImportError:
    INDONESIAN_ADJUSTER_AVAILABLE = False
    logger.warning("Indonesian adjuster not available")

try:
    from .english_rules import EnglishBloomAdjuster
    ENGLISH_ADJUSTER_AVAILABLE = True
    logger.info("✓ English pattern adjuster loaded")
except ImportError:
    ENGLISH_ADJUSTER_AVAILABLE = False
    logger.warning("English adjuster not available")


class BloomClassifier:
    """
    Wrapper class for RoBERTa-based Bloom's Taxonomy classifier
    WITH BOTH Indonesian and English pattern-based adjustment
    WITH Consistency improvements
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
    
    def __init__(self, model_path=None, use_pattern_adjusters=True):
        """
        Initialize the classifier
        
        Args:
            model_path: Path to the model directory
            use_pattern_adjusters: Whether to use pattern-based adjustment
        """
        self.model_path = model_path or getattr(settings, 'BLOOM_MODEL_PATH', './roberta_multilabel')
        self.tokenizer = None
        self.model = None
        self.translator = GoogleTranslator(source='id', target='en')
        self.is_loaded = False
        
        # Pattern adjusters - BOTH languages
        self.use_adjusters = use_pattern_adjusters
        
        # Indonesian adjuster
        if self.use_adjusters and INDONESIAN_ADJUSTER_AVAILABLE:
            self.indonesian_adjuster = IndonesianBloomAdjuster()
            logger.info("✓ Indonesian pattern adjuster enabled")
        else:
            self.indonesian_adjuster = None
        
        # English adjuster
        if self.use_adjusters and ENGLISH_ADJUSTER_AVAILABLE:
            self.english_adjuster = EnglishBloomAdjuster()
            logger.info("✓ English pattern adjuster enabled")
        else:
            self.english_adjuster = None
    
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
            logger.info("✓ Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}", exc_info=True)
            self.is_loaded = False
            return False
    
    def _detect_language(self, text):
        """
        Detect if text is Indonesian or English
        
        Returns: 'id' for Indonesian, 'en' for English
        """
        text_lower = text.lower().strip()
        
        # Indonesian indicators
        indonesian_words = [
            'yang', 'adalah', 'dari', 'untuk', 'dengan', 'pada', 'dalam',
            'atau', 'dan', 'ini', 'itu', 'akan', 'dapat', 'tersebut',
            'sebagai', 'oleh', 'karena', 'apakah', 'dimaksud', 'merupakan',
            'termasuk', 'pengertian', 'definisi', 'bagaimana', 'mengapa',
            'jelaskan', 'sebutkan', 'uraikan'
        ]
        
        # English indicators
        english_words = [
            'the', 'is', 'are', 'was', 'were', 'what', 'which', 'who',
            'how', 'why', 'when', 'where', 'this', 'that', 'these', 'those',
            'would', 'should', 'could', 'define', 'explain', 'describe',
            'analyze', 'evaluate', 'create', 'does', 'do'
        ]
        
        # Count matches
        indonesian_count = sum(1 for word in indonesian_words if f' {word} ' in f' {text_lower} ' or text_lower.startswith(f'{word} '))
        english_count = sum(1 for word in english_words if f' {word} ' in f' {text_lower} ' or text_lower.startswith(f'{word} '))
        
        # Decision
        if indonesian_count > english_count:
            logger.debug(f"Language: Indonesian (ID:{indonesian_count} vs EN:{english_count})")
            return 'id'
        elif english_count > indonesian_count:
            logger.debug(f"Language: English (EN:{english_count} vs ID:{indonesian_count})")
            return 'en'
        else:
            # Fallback: Indonesian often has repeated vowels
            if re.search(r'[aiueo]{2,}', text_lower):
                return 'id'
            else:
                return 'en'
    
    def translate_text(self, text, src="id", dest="en"):
        """
        Translate text from Indonesian to English
        """
        try:
            if src != 'id' or dest != 'en':
                self.translator = GoogleTranslator(source=src, target=dest)
            
            translated = self.translator.translate(text)
            logger.debug(f"Translated: '{text[:50]}...' -> '{translated[:50]}...'")
            return translated
        except Exception as e:
            logger.warning(f"Translation failed: {e}. Using original text.")
            return text
    
    def _apply_consistency_rules(self, predictions, confidence, detected_lang):
        """
        Apply consistency rules to improve accuracy
        
        Rules:
        1. If confidence < 0.55, patterns will likely override
        2. C1/C2 with medium+ confidence are usually correct
        3. C5/C6 with low confidence are uncertain
        4. Boost C1/C2 confidence if high (they're easier to detect)
        """
        category = predictions['category']
        
        # Rule 1: Very low confidence - let patterns decide
        if confidence < 0.55:
            predictions['uncertain'] = True
            logger.debug(f"Low ML confidence ({confidence:.2f}), patterns may override")
            return predictions
        
        # Rule 2: C1/C2 with medium+ confidence - boost slightly
        if category in ['C1', 'C2'] and confidence > 0.65:
            boosted = min(0.95, confidence + 0.08)
            logger.debug(f"Boosted {category}: {confidence:.2f} -> {boosted:.2f} (easier to detect)")
            predictions['confidence'] = boosted
            predictions['confidence_boosted'] = True
        
        # Rule 3: High levels (C5/C6) need high confidence
        if category in ['C5', 'C6'] and confidence < 0.70:
            logger.debug(f"{category} with low confidence ({confidence:.2f}), marked uncertain")
            predictions['uncertain'] = True
        
        # Rule 4: C4 is often over-predicted, be cautious
        if category == 'C4' and confidence < 0.75:
            logger.debug(f"C4 with medium confidence, patterns may adjust")
            predictions['uncertain'] = True
        
        return predictions
    
    def predict_single(self, text, translate=True, original_text=None):
        """
        Predict Bloom's taxonomy category for a single question
        WITH INTELLIGENT PATTERN ADJUSTMENT AND CONSISTENCY RULES
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        try:
            # Store original for pattern matching
            if original_text is None:
                original_text = text
            
            # Detect language BEFORE translation
            detected_lang = self._detect_language(original_text)
            logger.debug(f"Detected language: {detected_lang.upper()}")
            
            # Translate if needed
            if translate and detected_lang == 'id':
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
                'translated_text': text if translate else None,
                'detected_language': detected_lang
            }
            
            # === APPLY CONSISTENCY RULES ===
            ml_result = self._apply_consistency_rules(ml_result, confidence, detected_lang)
            
            # === APPLY APPROPRIATE PATTERN ADJUSTER ===
            adjuster_used = None
            
            if self.use_adjusters:
                # Use Indonesian adjuster for Indonesian text
                if detected_lang == 'id' and self.indonesian_adjuster:
                    adjusted_result = self.indonesian_adjuster.adjust_classification(
                        original_text, 
                        ml_result
                    )
                    adjuster_used = 'indonesian'
                
                # Use English adjuster for English text
                elif detected_lang == 'en' and self.english_adjuster:
                    adjusted_result = self.english_adjuster.adjust_classification(
                        original_text,
                        ml_result
                    )
                    adjuster_used = 'english'
                
                else:
                    adjusted_result = ml_result
                
                # Check if adjustment was made
                if adjuster_used:
                    was_adjusted = (
                        adjusted_result.get('category') != ml_result['category'] or
                        abs(adjusted_result.get('confidence', 0) - ml_result['confidence']) > 0.05
                    )
                    
                    adjusted_result['was_adjusted'] = was_adjusted
                    adjusted_result['adjuster_used'] = adjuster_used
                    adjusted_result['detected_language'] = detected_lang
                    adjusted_result['ml_category'] = ml_result['category']
                    adjusted_result['ml_confidence'] = ml_result['confidence']
                    
                    if was_adjusted:
                        logger.info(
                            f"✓ ADJUSTED ({adjuster_used}): "
                            f"{ml_result['category']}({ml_result['confidence']:.2f}) -> "
                            f"{adjusted_result['category']}({adjusted_result['confidence']:.2f})"
                        )
                    
                    return adjusted_result
            
            # No adjustment applied
            ml_result['was_adjusted'] = False
            ml_result['adjuster_used'] = None
            return ml_result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            raise
    
    def predict_batch(self, texts, translate=True, batch_size=8):
        """
        Predict categories for multiple questions
        WITH INTELLIGENT PATTERN ADJUSTMENT AND CONSISTENCY
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        results = []
        
        try:
            # Store originals and detect languages
            original_texts = texts.copy()
            detected_languages = [self._detect_language(text) for text in texts]
            
            # Log language distribution
            id_count = sum(1 for lang in detected_languages if lang == 'id')
            en_count = len(detected_languages) - id_count
            logger.info(f"Processing {len(texts)} questions (ID:{id_count}, EN:{en_count})")
            
            # Translate texts that need it
            if translate:
                translated_texts = []
                for text, lang in zip(texts, detected_languages):
                    if lang == 'id':
                        try:
                            translated = self.translate_text(text, src="id", dest="en")
                            translated_texts.append(translated)
                        except Exception as e:
                            logger.warning(f"Translation failed, using original: {e}")
                            translated_texts.append(text)
                    else:
                        translated_texts.append(text)
            else:
                translated_texts = texts
            
            # Process in batches
            for i in range(0, len(translated_texts), batch_size):
                batch = translated_texts[i:i + batch_size]
                batch_originals = original_texts[i:i + batch_size]
                batch_languages = detected_languages[i:i + batch_size]
                
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
                for j, (probs, original, lang) in enumerate(zip(probs_batch, batch_originals, batch_languages)):
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
                        'original_text': original,
                        'detected_language': lang
                    }
                    
                    # Apply consistency rules
                    ml_result = self._apply_consistency_rules(ml_result, confidence, lang)
                    
                    # === APPLY APPROPRIATE PATTERN ADJUSTER ===
                    adjuster_used = None
                    
                    if self.use_adjusters:
                        # Indonesian adjuster
                        if lang == 'id' and self.indonesian_adjuster:
                            adjusted_result = self.indonesian_adjuster.adjust_classification(
                                original,
                                ml_result
                            )
                            adjuster_used = 'indonesian'
                        
                        # English adjuster
                        elif lang == 'en' and self.english_adjuster:
                            adjusted_result = self.english_adjuster.adjust_classification(
                                original,
                                ml_result
                            )
                            adjuster_used = 'english'
                        
                        else:
                            adjusted_result = ml_result
                        
                        # Check if adjustment was made
                        if adjuster_used:
                            was_adjusted = (
                                adjusted_result.get('category') != ml_result['category'] or
                                abs(adjusted_result.get('confidence', 0) - ml_result['confidence']) > 0.05
                            )
                            
                            adjusted_result['was_adjusted'] = was_adjusted
                            adjusted_result['adjuster_used'] = adjuster_used
                            adjusted_result['detected_language'] = lang
                            adjusted_result['ml_category'] = ml_result['category']
                            adjusted_result['ml_confidence'] = ml_result['confidence']
                            adjusted_result['original_text'] = original
                            
                            results.append(adjusted_result)
                        else:
                            ml_result['was_adjusted'] = False
                            ml_result['adjuster_used'] = None
                            results.append(ml_result)
                    else:
                        ml_result['was_adjusted'] = False
                        ml_result['adjuster_used'] = None
                        results.append(ml_result)
                
                logger.info(f"✓ Batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} completed")
            
            # Log adjustment statistics
            if self.use_adjusters:
                adjusted_count = sum(1 for r in results if r.get('was_adjusted', False))
                indonesian_adjusted = sum(1 for r in results if r.get('adjuster_used') == 'indonesian' and r.get('was_adjusted'))
                english_adjusted = sum(1 for r in results if r.get('adjuster_used') == 'english' and r.get('was_adjusted'))
                
                logger.info(
                    f"✓ COMPLETED: {len(results)} questions classified | "
                    f"{adjusted_count} adjusted (ID:{indonesian_adjusted}, EN:{english_adjusted})"
                )
            else:
                logger.info(f"✓ COMPLETED: {len(results)} questions classified")
            
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
            "adjusters": {
                "indonesian": self.indonesian_adjuster is not None,
                "english": self.english_adjuster is not None
            }
        }


# Global classifier instance (singleton pattern)
_classifier_instance = None

def get_classifier(use_pattern_adjusters=True):
    """
    Get or create the global classifier instance
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = BloomClassifier(use_pattern_adjusters=use_pattern_adjusters)
        _classifier_instance.load_model()
    return _classifier_instance


# Convenience functions

def classify_question(text, translate=True):
    """Classify a single question"""
    classifier = get_classifier()
    return classifier.predict_single(text, translate=translate)


def classify_questions_batch(texts, translate=True, batch_size=8):
    """Classify multiple questions"""
    classifier = get_classifier()
    return classifier.predict_batch(texts, translate=translate, batch_size=batch_size)