# apps/klasifikasi/indonesian_rules.py 


import re
import logging

logger = logging.getLogger(__name__)


class IndonesianBloomAdjuster:
    """
    AGGRESSIVE adjuster - forces correct classification for Indonesian questions
    WITH CONFIDENCE BOOSTING
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
        r'\bfungsi\s+(?:dari\s+)?(?:adalah)?(?!\s+untuk)',
        r'\barti\s+dari',
        r'\bmaksud\s+dari',
        r'\bjenis\s+(?:dari)?',
        r'\bmacam\s+(?:dari)?',
        r'\bkondisi\s+(?:yang\s+)?(?:ideal|terbaik)',
        r'\bmetode\s+yang\s+(?:sering\s+digunakan|paling)',
        r'\bsumber\s+(?:yang\s+paling\s+penting|utama)',
        r'\bbiaya\s+yang\s+dikeluarkan\s+untuk',
        r'\bformulir\s+yang\s+digunakan',
        r'\bkegiatan\s+terakhir\s+dari',
        r'\bsalah\s+satu\s+(?:bentuk|upaya|teknik)',
        r'\bsebutkan\s+(?:apa|yang|jenis)',
        r'\bidentifikasi\s+(?:apa|yang)',
        r'\bapa\s+(?:nama|istilah)',
    ]
    
    # ULTIMATE C2 INDICATORS - these FORCE C2 classification
    FORCE_C2_PATTERNS = [
        # "hal ini berarti" = understanding = C2
        r'\bhal\s+ini\s+berarti',
        r'\bsebagai\s+dasar\s+yang\s+digunakan\s+untuk',
        r'\bfaktor\s+yang\s+mempengaruhi',
        r'\bhubungan\s+antara',
        r'\bperbedaan\s+(?:antara|dari)',
        r'\bbagaimana\b(?!\s+cara)',
        r'\bmengapa\b',
        r'\bjelaskan\b(?!\s+cara)',
        r'\buraikan\b',
        r'\bgambarkan\b',
        r'\bpaparkan\b',
        r'\bdeskripsikan\b',
        r'\bmaksud\s+dari\s+pernyataan',
        r'\bapa\s+yang\s+dimaksud\s+dengan\s+pernyataan',
        r'\bapa\s+arti\s+dari',
        r'\binterpretasikan\b',
    ]
    
    # C3 (APPLY) PATTERNS
    FORCE_C3_PATTERNS = [
        r'\bterapkan\b',
        r'\bgunakan\b(?=.{0,20}(?:untuk\s+(?:menghitung|menyelesaikan|memecahkan)))',
        r'\bhitunglah\b',
        r'\bselesaikan\b',
        r'\bimplementasikan\b',
        r'\baplikasikan\b',
        r'\bpraktikkan\b',
        r'\blaksanakan\b',
        r'\bmodifikasi\b',
        r'\badaptasikan\b',
        r'\bbagaimana\s+cara\s+(?:menggunakan|menerapkan)',
    ]
    
    # C4 (ANALYZE) PATTERNS
    FORCE_C4_PATTERNS = [
        r'\banalisis\b',
        r'\banalisa\b',
        r'\bteliti\b',
        r'\bperiksa\b',
        r'\bbandingkan\s+dan\s+kontraskan',
        r'\bkategorikan\b',
        r'\bklasifikasikan\b',
        r'\borganisasikan\b',
        r'\buraikan\s+(?:hubungan|perbedaan|persamaan)',
        r'\bidentifikasi\s+(?:pola|kecenderungan|hubungan)',
        r'\bapa\s+(?:penyebab|akibat|dampak)',
        r'\bmengapa\s+\w+\s+(?:menyebabkan|mengakibatkan)',
        r'\bbedakan\b',
        r'\bpecah\s+menjadi',
    ]
    
    # C5 (EVALUATE) PATTERNS
    FORCE_C5_PATTERNS = [
        r'\bevaluasi\b',
        r'\bnilai\b(?=.{0,30}(?:efektivitas|kualitas|kelayakan))',
        r'\bpertimbangkan\b',
        r'\bkritik\b',
        r'\bkaji\b',
        r'\bjustifikasi\b',
        r'\bpertahankan\b',
        r'\brekomendasi\b',
        r'\busulkan\b(?!\s+(?:desain|rancangan|model))',
        r'\bapa\s+yang\s+(?:lebih|paling)\s+(?:baik|efektif|tepat)',
        r'\bapakah\s+(?:tepat|sesuai|efektif)',
        r'\bberikan\s+penilaian',
        r'\bputuskan\s+(?:apakah|mana)',
    ]
    
    # C6 (CREATE) PATTERNS
    FORCE_C6_PATTERNS = [
        r'\brancang\b',
        r'\bdesain\b',
        r'\bbuatlah\b',
        r'\bkembangkan\b',
        r'\bciptakan\b',
        r'\bsusun\b(?=.{0,30}(?:rencana|strategi|model|sistem))',
        r'\bformulasikan\b',
        r'\brumuskan\b',
        r'\bmenghasilkan\b',
        r'\bbuat\s+(?:model|rancangan|desain|sistem|strategi)',
        r'\busulkan\s+(?:desain|rancangan|model)',
        r'\brencanakan\b',
        r'\bproduksi\b',
        r'\bintegrasikan\b',
        r'\bsintesis\b',
    ]
    
    # C1/C2 KEYWORDS
    C1_KEYWORDS = [
        'pengertian', 'definisi', 'arti', 'maksud', 'dimaksud', 'disebut', 
        'dinamakan', 'merupakan', 'termasuk', 'salah satu', 'tahap pertama',
        'tahap awal', 'tahap akhir', 'tahap terakhir', 'kegiatan terakhir',
        'sifat utama', 'jenis', 'macam', 'kategori', 'komponen', 'unsur',
        'bentuk dari', 'kondisi ideal', 'metode yang', 'sumber utama',
        'sumber yang paling', 'biaya yang dikeluarkan', 'formulir yang',
        'salah satu bentuk', 'salah satu teknik', 'salah satu upaya',
        'sebutkan', 'identifikasi', 'nama', 'istilah'
    ]
    
    C2_KEYWORDS = [
        'hal ini berarti', 'sebagai dasar', 'dasar yang digunakan',
        'faktor yang mempengaruhi', 'hubungan antara', 'perbedaan',
        'jelaskan', 'mengapa', 'bagaimana', 'uraikan', 'gambarkan',
        'paparkan', 'deskripsikan', 'interpretasikan'
    ]
    
    C3_KEYWORDS = [
        'terapkan', 'gunakan', 'hitunglah', 'selesaikan', 'implementasikan',
        'aplikasikan', 'praktikkan', 'laksanakan', 'modifikasi', 'adaptasikan',
        'cara menggunakan', 'cara menerapkan'
    ]
    
    C4_KEYWORDS = [
        'analisis', 'analisa', 'teliti', 'periksa', 'bandingkan',
        'kategorikan', 'klasifikasikan', 'organisasikan', 'identifikasi pola',
        'penyebab', 'akibat', 'dampak', 'bedakan'
    ]
    
    C5_KEYWORDS = [
        'evaluasi', 'nilai', 'pertimbangkan', 'kritik', 'kaji',
        'justifikasi', 'pertahankan', 'rekomendasi', 'usulkan',
        'lebih baik', 'paling efektif', 'paling tepat', 'berikan penilaian',
        'putuskan'
    ]
    
    C6_KEYWORDS = [
        'rancang', 'desain', 'buatlah', 'kembangkan', 'ciptakan',
        'susun', 'formulasikan', 'rumuskan', 'menghasilkan', 'buat model',
        'rencanakan', 'produksi', 'integrasikan', 'sintesis'
    ]
    
    # ANTI-PATTERNS
    NOT_C1_PATTERNS = [
        r'\bhitunglah\b',
        r'\bterapkan\b',
        r'\bgunakan\b(?=.{0,20}untuk\s+(?:menghitung|menyelesaikan))',
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
    
    NOT_C2_PATTERNS = [
        r'\bhitunglah\b',
        r'\bterapkan\b',
        r'\banalisis\b',
        r'\brancang\b',
        r'\bbuatlah\b',
        r'\bgunakan\s+untuk\s+menghitung',
    ]
    
    NOT_C3_PATTERNS = [
        r'\banalisis\b',
        r'\bevaluasi\b',
        r'\brancang\b',
        r'\bbuatlah\b',
        r'\bkembangkan\b',
    ]
    
    NOT_C4_PATTERNS = [
        r'\brancang\b',
        r'\bbuatlah\b',
        r'\bdesain\b',
        r'\bkembangkan\b',
        r'\bciptakan\b',
    ]
    
    NOT_C5_PATTERNS = [
        r'\brancang\b',
        r'\bbuatlah\b',
        r'\bdesain\b',
        r'\bciptakan\b',
        r'\bsusun\s+(?:rencana|model)',
    ]
    
    NOT_C6_PATTERNS = []
    
    def __init__(self):
        self.compiled_force_c1 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C1_PATTERNS]
        self.compiled_force_c2 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C2_PATTERNS]
        self.compiled_force_c3 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C3_PATTERNS]
        self.compiled_force_c4 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C4_PATTERNS]
        self.compiled_force_c5 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C5_PATTERNS]
        self.compiled_force_c6 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C6_PATTERNS]
        
        self.compiled_not_c1 = [re.compile(p, re.IGNORECASE) for p in self.NOT_C1_PATTERNS]
        self.compiled_not_c2 = [re.compile(p, re.IGNORECASE) for p in self.NOT_C2_PATTERNS]
        self.compiled_not_c3 = [re.compile(p, re.IGNORECASE) for p in self.NOT_C3_PATTERNS]
        self.compiled_not_c4 = [re.compile(p, re.IGNORECASE) for p in self.NOT_C4_PATTERNS]
        self.compiled_not_c5 = [re.compile(p, re.IGNORECASE) for p in self.NOT_C5_PATTERNS]
    
    def _boost_confidence(self, category, ml_confidence, pattern_strength, keyword_count):
        """
        Boost confidence when pattern is very strong
        
        Args:
            category: Predicted category (C1-C6)
            ml_confidence: Original ML confidence
            pattern_strength: Number of patterns matched
            keyword_count: Number of keywords found
        
        Returns:
            Boosted confidence (0.85-0.98)
        """
        base_confidence = {
            'C1': 0.95,  # C1 Indonesian patterns very reliable
            'C2': 0.92,
            'C3': 0.88,
            'C4': 0.90,
            'C5': 0.91,
            'C6': 0.93,
        }
        
        confidence = base_confidence.get(category, 0.85)
        
        # Boost if ML also agrees
        if ml_confidence > 0.70:
            confidence = min(0.98, confidence + 0.03)
        
        # Boost if multiple strong signals
        if pattern_strength >= 2 or keyword_count >= 3:
            confidence = min(0.98, confidence + 0.03)
        
        # Boost if both pattern AND keywords match
        if pattern_strength >= 1 and keyword_count >= 2:
            confidence = min(0.98, confidence + 0.02)
        
        return confidence
    
    def adjust_classification(self, question_text, ml_prediction):
        """
        AGGRESSIVE adjustment with confidence boosting
        
        Priority:
        1. Check C6 first (highest level)
        2. Check C5, C4, C3, C2, C1 in descending order
        3. Boost confidence when patterns are strong
        4. Keep ML prediction if no strong patterns
        """
        question_lower = question_text.lower().strip()
        
        ml_level = ml_prediction['category']
        ml_confidence = ml_prediction['confidence']
        
        # === CHECK C6 (CREATE) ===
        result = self._check_level(
            question_lower,
            self.compiled_force_c6,
            self.C6_KEYWORDS,
            [],
            ml_level,
            'C6',
            'Create',
            ml_confidence
        )
        if result:
            return result
        
        # === CHECK C5 (EVALUATE) ===
        result = self._check_level(
            question_lower,
            self.compiled_force_c5,
            self.C5_KEYWORDS,
            self.compiled_not_c5,
            ml_level,
            'C5',
            'Evaluate',
            ml_confidence
        )
        if result:
            return result
        
        # === CHECK C4 (ANALYZE) ===
        result = self._check_level(
            question_lower,
            self.compiled_force_c4,
            self.C4_KEYWORDS,
            self.compiled_not_c4,
            ml_level,
            'C4',
            'Analyze',
            ml_confidence
        )
        if result:
            return result
        
        # === CHECK C3 (APPLY) ===
        result = self._check_level(
            question_lower,
            self.compiled_force_c3,
            self.C3_KEYWORDS,
            self.compiled_not_c3,
            ml_level,
            'C3',
            'Apply',
            ml_confidence
        )
        if result:
            return result
        
        # === CHECK C2 (UNDERSTAND) ===
        result = self._check_level(
            question_lower,
            self.compiled_force_c2,
            self.C2_KEYWORDS,
            self.compiled_not_c2,
            ml_level,
            'C2',
            'Understand',
            ml_confidence
        )
        if result:
            return result
        
        # === CHECK C1 (REMEMBER) ===
        result = self._check_level(
            question_lower,
            self.compiled_force_c1,
            self.C1_KEYWORDS,
            self.compiled_not_c1,
            ml_level,
            'C1',
            'Remember',
            ml_confidence
        )
        if result:
            return result
        
        # === DOWNGRADE HIGH CLASSIFICATIONS FOR SIMPLE QUESTIONS ===
        if ml_level in ['C4', 'C5', 'C6']:
            word_count = len(question_lower.split())
            
            if word_count < 12 and ml_confidence < 0.75:
                logger.info(
                    f"DOWNGRADED: {ml_level}({ml_confidence:.2f}) -> C3 (too simple) | "
                    f"Q: {question_text[:70]}..."
                )
                return {
                    'category': 'C3',
                    'category_name': 'Apply',
                    'confidence': 0.70,
                    'all_probabilities': ml_prediction.get('all_probabilities', {}),
                    'adjustment_reason': 'downgrade_simple_question',
                    'ml_category': ml_level,
                    'ml_confidence': ml_confidence,
                    'was_adjusted': True
                }
        
        # === KEEP ML PREDICTION ===
        return {
            'category': ml_level,
            'category_name': ml_prediction.get('category_name', ''),
            'confidence': ml_confidence,
            'all_probabilities': ml_prediction.get('all_probabilities', {}),
            'adjustment_reason': 'ml_kept',
            'ml_category': ml_level,
            'ml_confidence': ml_confidence,
            'was_adjusted': False
        }
    
    def _check_level(self, question_lower, force_patterns, keywords, 
                     anti_patterns, ml_level, target_level, level_name, ml_confidence):
        """
        Check if question matches a specific Bloom level
        WITH CONFIDENCE BOOSTING
        """
        # Check anti-patterns first
        if any(p.search(question_lower) for p in anti_patterns):
            return None
        
        # Count patterns and keywords
        pattern_count = sum(1 for p in force_patterns if p.search(question_lower))
        keyword_count = sum(1 for kw in keywords if kw.lower() in question_lower)
        
        # Decision logic
        has_strong_pattern = pattern_count >= 1
        has_strong_keywords = keyword_count >= 2
        
        if has_strong_pattern or (keyword_count >= 3):
            # Calculate boosted confidence
            confidence = self._boost_confidence(
                target_level,
                ml_confidence,
                pattern_count,
                keyword_count
            )
            
            if ml_level != target_level:
                logger.info(
                    f"ADJUSTED: ML={ml_level}({ml_confidence:.2f}) -> {target_level}({confidence:.2f}) "
                    f"(patterns:{pattern_count}, keywords:{keyword_count})"
                )
            
            return {
                'category': target_level,
                'category_name': level_name,
                'confidence': confidence,
                'all_probabilities': {},
                'adjustment_reason': f'force_{target_level.lower()}_pattern',
                'ml_category': ml_level,
                'ml_confidence': ml_confidence,
                'was_adjusted': True
            }
        
        return None


def adjust_classification_with_patterns(question_text, ml_prediction):
    """Convenience function"""
    adjuster = IndonesianBloomAdjuster()
    return adjuster.adjust_classification(question_text, ml_prediction)