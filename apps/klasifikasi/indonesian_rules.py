# apps/klasifikasi/indonesian_rules.py - NUCLEAR C1/C2 ENFORCEMENT

"""
ULTRA-AGGRESSIVE Indonesian pattern recognition
Rule: When in doubt, force to lower level (C1/C2)
"""

import re
import logging

logger = logging.getLogger(__name__)


class IndonesianBloomAdjuster:
    """
    AGGRESSIVE adjuster - forces C1/C2 for definition questions
    """
    
    # ULTIMATE C1 INDICATORS - these FORCE C1 classification
    FORCE_C1_PATTERNS = [
        # "Pengertian/definisi/arti" = definition = ALWAYS C1
        r'\b(?:pengertian|definisi|arti)\s+(?:dari\s+)?(?:yang\s+paling\s+)?(?:umum|utama|inti)?',
        r'\bapa\s+(?:yang\s+)?dimaksud\s+(?:dengan|dari)',
        r'\byang\s+dimaksud\s+(?:dengan|dari|sebagai)',
        r'\bdisebut\s+(?:sebagai\s+)?(?:adalah)?',
        r'\bdinamakan\s+(?:sebagai)?',
        r'\bmerupakan\s+(?:salah\s+satu)?',
        r'\btermasuk\s+(?:dalam\s+)?(?:kategori|jenis|golongan)',
        r'\bsalah\s+satu\s+(?:komponen|faktor|kategori|jenis|bentuk|unsur|teknik|metode)',
        r'\btahap\s+(?:pertama|awal|akhir|terakhir)',
        r'\bkegiatan\s+(?:pertama|awal|terakhir)',
        r'\bsifat\s+(?:utama|dari)',
        r'\bfungsi\s+(?:dari\s+)?(?:adalah)?(?!\s+untuk)',  # "fungsi adalah" but NOT "fungsi adalah untuk"
        r'\barti\s+dari',
        r'\bmaksud\s+dari',
        r'\bjenis\s+(?:dari)?',
        r'\bmacam\s+(?:dari)?',
        r'\bkondisi\s+(?:yang\s+)?(?:ideal|terbaik)',
        r'\bmetode\s+(?:yang\s+sering\s+digunakan|yang\s+paling)',
        r'\bsumber\s+(?:yang\s+paling\s+penting|utama)',
        r'\bbiaya\s+yang\s+dikeluarkan\s+untuk',
        r'\bformulir\s+yang\s+digunakan',
        r'\bkegiatan\s+terakhir\s+dari',
        r'\bsalah\s+satu\s+(?:bentuk|upaya|teknik)',
    ]
    
    # ULTIMATE C2 INDICATORS - these FORCE C2 classification
    FORCE_C2_PATTERNS = [
        # "hal ini berarti" = understanding = C2
        r'\bhal\s+ini\s+berarti',
        r'\bsebagai\s+dasar\s+yang\s+digunakan\s+untuk',
        r'\bfaktor\s+yang\s+mempengaruhi',
        r'\bhubungan\s+antara',
        r'\bperbedaan\s+(?:antara|dari)',
        r'\bbagaimana\b(?!\s+cara)',  # "bagaimana" but NOT "bagaimana cara"
        r'\bmengapa\b',
        r'\bjelaskan\b(?!\s+cara)',  # "jelaskan" but NOT "jelaskan cara"
    ]
    
    # C1/C2 KEYWORDS - if present, very likely C1/C2
    C1_KEYWORDS = [
        'pengertian', 'definisi', 'arti', 'maksud', 'dimaksud', 'disebut', 
        'dinamakan', 'merupakan', 'termasuk', 'salah satu', 'tahap pertama',
        'tahap awal', 'tahap akhir', 'tahap terakhir', 'kegiatan terakhir',
        'sifat utama', 'jenis', 'macam', 'kategori', 'komponen', 'unsur',
        'bentuk dari', 'kondisi ideal', 'metode yang', 'sumber utama',
        'sumber yang paling', 'biaya yang dikeluarkan', 'formulir yang',
        'salah satu bentuk', 'salah satu teknik', 'salah satu upaya',
    ]
    
    C2_KEYWORDS = [
        'hal ini berarti', 'sebagai dasar', 'dasar yang digunakan',
        'faktor yang mempengaruhi', 'hubungan antara', 'perbedaan',
    ]
    
    # ANTI-PATTERNS - if these exist, NOT C1
    NOT_C1_PATTERNS = [
        r'\bhitunglah\b',
        r'\bterapkan\b',
        r'\bgunakan\b',
        r'\baplikasikan\b',
        r'\banalisis\b',
        r'\bbandingkan\b',
        r'\bevaluasi\b',
        r'\bnilai\b',
        r'\brancang\b',
        r'\bbuatlah\b',
        r'\bdesain\b',
        r'\bkembangkan\b',
    ]
    
    # ANTI-PATTERNS - if these exist, NOT C2
    NOT_C2_PATTERNS = [
        r'\bhitunglah\b',
        r'\bterapkan\b',
        r'\banalisis\b',
        r'\brancang\b',
        r'\bbuatlah\b',
    ]
    
    def __init__(self):
        self.compiled_force_c1 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C1_PATTERNS]
        self.compiled_force_c2 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C2_PATTERNS]
        self.compiled_not_c1 = [re.compile(p, re.IGNORECASE) for p in self.NOT_C1_PATTERNS]
        self.compiled_not_c2 = [re.compile(p, re.IGNORECASE) for p in self.NOT_C2_PATTERNS]
    
    def adjust_classification(self, question_text, ml_prediction):
        """
        AGGRESSIVE adjustment
        
        Priority:
        1. FORCE C1 if C1 pattern detected (unless strong anti-pattern)
        2. FORCE C2 if C2 pattern detected (unless anti-pattern)
        3. Otherwise keep ML prediction
        """
        question_lower = question_text.lower().strip()
        
        ml_level = ml_prediction['category']
        ml_confidence = ml_prediction['confidence']
        
        # === RULE 1: CHECK FOR FORCE C1 ===
        has_force_c1 = any(p.search(question_lower) for p in self.compiled_force_c1)
        has_c1_keywords = any(kw in question_lower for kw in self.C1_KEYWORDS)
        has_anti_c1 = any(p.search(question_lower) for p in self.compiled_not_c1)
        
        if (has_force_c1 or has_c1_keywords) and not has_anti_c1:
            if ml_level != 'C1':
                logger.info(
                    f"FORCED C1: ML said {ml_level}({ml_confidence:.2f}) | "
                    f"Q: {question_text[:70]}..."
                )
            return {
                'category': 'C1',
                'category_name': 'Remember',
                'confidence': 0.95,
                'all_probabilities': ml_prediction['all_probabilities'],
                'adjustment_reason': 'force_c1_pattern',
                'ml_category': ml_level,
                'ml_confidence': ml_confidence,
                'was_adjusted': True
            }
        
        # === RULE 2: CHECK FOR FORCE C2 ===
        has_force_c2 = any(p.search(question_lower) for p in self.compiled_force_c2)
        has_c2_keywords = any(kw in question_lower for kw in self.C2_KEYWORDS)
        has_anti_c2 = any(p.search(question_lower) for p in self.compiled_not_c2)
        
        if (has_force_c2 or has_c2_keywords) and not has_anti_c2:
            if ml_level != 'C2':
                logger.info(
                    f"FORCED C2: ML said {ml_level}({ml_confidence:.2f}) | "
                    f"Q: {question_text[:70]}..."
                )
            return {
                'category': 'C2',
                'category_name': 'Understand',
                'confidence': 0.90,
                'all_probabilities': ml_prediction['all_probabilities'],
                'adjustment_reason': 'force_c2_pattern',
                'ml_category': ml_level,
                'ml_confidence': ml_confidence,
                'was_adjusted': True
            }
        
        # === RULE 3: DOWNGRADE HIGH CLASSIFICATIONS FOR SIMPLE QUESTIONS ===
        # If ML says C4/C5/C6 but question is simple (short, basic), downgrade
        if ml_level in ['C4', 'C5', 'C6']:
            word_count = len(question_lower.split())
            
            # Simple question = C3 max
            if word_count < 12 and ml_confidence < 0.75:
                logger.info(
                    f"DOWNGRADED: {ml_level}({ml_confidence:.2f}) -> C3 (too simple) | "
                    f"Q: {question_text[:70]}..."
                )
                return {
                    'category': 'C3',
                    'category_name': 'Apply',
                    'confidence': 0.70,
                    'all_probabilities': ml_prediction['all_probabilities'],
                    'adjustment_reason': 'downgrade_simple_question',
                    'ml_category': ml_level,
                    'ml_confidence': ml_confidence,
                    'was_adjusted': True
                }
        
        # === RULE 4: KEEP ML PREDICTION ===
        return {
            'category': ml_level,
            'category_name': ml_prediction['category_name'],
            'confidence': ml_confidence,
            'all_probabilities': ml_prediction['all_probabilities'],
            'adjustment_reason': 'ml_kept',
            'ml_category': ml_level,
            'ml_confidence': ml_confidence,
            'was_adjusted': False
        }


def adjust_classification_with_patterns(question_text, ml_prediction):
    """Convenience function"""
    adjuster = IndonesianBloomAdjuster()
    return adjuster.adjust_classification(question_text, ml_prediction)