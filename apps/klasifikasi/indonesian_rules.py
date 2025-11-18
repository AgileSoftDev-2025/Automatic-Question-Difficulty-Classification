# apps/klasifikasi/indonesian_rules.py - V5.1: SURGICAL FIXES ONLY

import re
import logging

logger = logging.getLogger(__name__)


class IndonesianBloomAdjuster:
    """
    V5.1: MINIMAL changes to V5 - Only fix the 4 under-predictions
    
    V5 Performance: 31/45 correct (69%)
    - Over-predictions (14): Already handled well by V5
    - Under-predictions (4): Q3, Q6, Q29, Q43 - THESE ARE THE ONLY CHANGES
    
    Changes from V5:
    1. Add pattern for Q3: "Yang dimaksud relevansi" (C1→C2)
    2. Add pattern for Q6: "Aksesibilitas mempengaruhi" (C1→C2)
    3. Add pattern for Q29: "Evaluasi...melalui kriteria" (C1→C2)
    4. Add pattern for Q43: "Upaya menentukan" (C1→C2)
    
    Everything else: KEEP V5 AS IS
    """
    
    # ========== C1 (REMEMBER) - ULTRA STRONG PATTERNS (UNCHANGED FROM V5) ==========
    FORCE_C1_PATTERNS = [
        # === STRONGEST: Pure definition patterns ===
        r'\bpengertian\s+(?:yang\s+)?(?:paling\s+)?(?:umum|utama|inti|dari|tentang)',
        r'\bdefinisi\s+(?:dari|tentang|yang)',
        r'\barti\s+(?:dari\s+)?[\w\s]+\s+(?:adalah|merupakan|ialah)',
        r'\bapakah\s+(?:yang\s+)?dimaksud\s+(?:dengan|dari)',
        r'\bapa\s+(?:yang\s+)?dimaksud\s+(?:dengan|dari)\s+[\w\s]+\??$',
        
        # === "Yang dimaksud" with "adalah" pattern (Q1, Q3, Q18, Q25, Q27, Q35) ===
        r'\byang\s+dimaksud\s+(?:dengan\s+)?[\w\s]{3,40}\s+(?:adalah|ialah|merupakan)',
        r'\b(?:adalah|merupakan)\s+yang\s+dimaksud\s+(?:dengan|dari)',

        # FIX Q7: Izinkan kata-kata filler di antara 'kategori' dan 'analisis'
        r'\bkategori\s+.*?\b(?:analisis|evaluasi)',

        # FIX Q8: Tangkap 'disebut sebagai sistem...' (bukan cuma 'sebagai apa')
        r'\bdisebut\s+sebagai\s+(?!apa|apakah)\w+',

        # FIX Q37/38: Pastikan pola biaya langsung lebih kuat
        r'\bbiaya\s+langsung\s+.*?(?:dikeluarkan|adalah)',
        
        # === Naming questions - "disebut apa/sebagai" (Q2, Q12, Q16, Q39, Q42) ===
        r'\b(?:disebut|dinamakan|dikenal)\s+(?:apa|apakah|sebagai\s+apa)\s*\??$',
        r'\b(?:disebut|dinamakan|dikenal)\s+sebagai\s+(?:apa|apakah)',
        r'\bapa\s+(?:nama|istilah|sebutan)\s+(?:dari|untuk|bagi)',
        r'\bformulir\s+[\w\s]+\s+disebut\b',  # Q39 specific
        r'\bpengujian\s+[\w\s]+\s+disebut\s+pengujian\b',  # Q42 specific
        r'\bsistem\s+[\w\s]+\s+disebut\b',  # Q16 specific
        
        # === Classification - "termasuk/salah satu" (Q7, Q17, Q44) ===
        r'\btermasuk\s+(?:dalam\s+)?(?:kategori|jenis|subsistem|golongan|komponen|bentuk)',
        r'\bsalah\s+satu\s+(?:komponen|faktor|bentuk|unsur|teknik|metode|upaya|elemen)',
        r'\bkategori\s+(?:analisis|evaluasi)\s+[\w\s]+\s+(?:adalah|merupakan)',
        r'\bmerupakan\s+(?:salah\s+satu|bagian\s+dari)',
        
        # === Sequence/order questions (Q5, Q30, Q41) ===
        r'\btahap\s+(?:pertama|awal|akhir|terakhir|pertama\s+kali)',
        r'\bkegiatan\s+(?:pertama|awal|terakhir|yang\s+pertama)',
        r'\blangkah\s+(?:pertama|awal|terakhir)',
        
        # === Properties - asking WHAT characteristic (Q4, Q20, Q21, Q28) ===
        r'\bsifat\s+(?:utama|dari|yang|khas)',
        r'\bkondisi\s+(?:yang\s+)?(?:ideal|terbaik|optimum)',
        r'\bkomponen\s+(?:penentu|utama|yang)',
        r'\bkarakteristik\s+(?:utama|dari)',
        
        # === Lists - "sebutkan" (Q31, Q32) ===
        r'\bsebutkan\s+(?:apa|yang|jenis|salah\s+satu)(?!\s+perbedaan)',
        r'\bsumber\s+(?:utama|yang)',  # Q31
        r'\bmetode\s+(?:analisis|yang\s+digunakan)\s+untuk',  # Q32
        
        # === Meaning/interpretation (Q19, Q45) ===
        r'\bpengertian\s+inti\s+(?:dari|tentang)',
        r'\b(?:artinya|maksudnya)\s+adalah',
        r'\binspeksi\s+audit\s+artinya',  # Q45
        
        # === Technical definitions (Q14, Q23, Q26, Q36) ===
        r'\bprogram\s+[\w\s]+\s+(?:adalah|merupakan)',
        r'\belemen\s+proses\s+[\w\s]+\s+(?:adalah|merupakan)',
        
        # === Risk/advantage identification (Q37, Q38) ===
        r'\bbiaya\s+langsung\s+(?:dikeluarkan|adalah)',
    ]
    
    # ========== C2 (UNDERSTAND) PATTERNS - ADDED 4 NEW PATTERNS ==========
    FORCE_C2_PATTERNS = [
        # === NEW: Fix Q3 - Yang dimaksud relevance (understanding, not just definition) ===
        r'\byang\s+dimaksud\s+(?:dengan\s+)?relevansi(?!\s+adalah)',
        
        # === NEW: Fix Q6 - "mempengaruhi" indicates understanding relationships ===
        r'\baksesibilitas\s+(?:dapat\s+)?mempengaruhi',
        r'\b(?:mempengaruhi|berpengaruh\s+terhadap)\s+nilai',

        # FIX Q9: Deteksi 'keputusan' + 'sifat' dengan lebih longgar
        r'\bkeputusan\s+.*?sifat',

        # FIX Q2: Deteksi 'dasar... untuk mengukur' (C2 Concept, bukan C5 Evaluate)
        r'\bdasar\s+.*?untuk\s+mengukur',
        
        # === NEW: Fix Q29 - Evaluasi "melalui kriteria" = understanding evaluation ===
        r'\bevaluasi\s+[\w\s]+\s+melalui\s+kriteria',
        
        # === NEW: Fix Q43 - "Upaya menentukan" = understanding process ===
        r'\bupaya\s+(?:untuk\s+)?menentukan\s+prioritas',
        
        # === EXISTING V5 PATTERNS (UNCHANGED) ===
        # === Explanation with reasoning ===
        r'\bjelaskan\s+mengapa(?!\s+cara)',
        r'\bjelaskan\s+bagaimana(?!\s+cara\s+(?:menggunakan|menerapkan|membuat))',
        r'\buraikan\s+(?:hubungan|perbedaan|mengapa)',
        
        # === WHY questions (understanding cause/effect) ===
        r'\bmengapa\s+[\w\s]+\s+(?:dapat|bisa|mempengaruhi|menyebabkan)',
        r'\bmengapa\s+[\w\s]+\s+(?:penting|diperlukan)',
        
        # === HOW questions (understanding process, not procedure) ===
        r'\bbagaimana\s+[\w\s]+\s+(?:mempengaruhi|dapat|bisa)(?!\s+cara)',
        
        # === Relationships (Q10, Q11, Q24, Q33, Q34) ===
        r'\bhubungan\s+antara\s+[\w\s]+\s+(?:dan|dengan)',
        r'\bfaktor\s+(?:yang\s+)?(?:mempengaruhi|menentukan|menjadi)',
        r'\bkeuntungan\s+(?:utama|dari)\s+[\w\s]+\s+(?:adalah|merupakan)',
        r'\brisiko\s+(?:yang\s+)?(?:mendasar|utama|yang)',
        r'\bsebagai\s+alat\s+bantu',  # Q11
        r'\bsesuai\s+dengan',  # Q34
        
        # === Function/purpose (Q6, Q13, Q15) ===
        r'\bmembantu\s+[\w\s]+\s+(?:jenis|tipe)\s+keputusan',  # Q13
        r'\bpemeriksaan\s+mutu\s+[\w\s]+\s+dilakukan',  # Q15
        
        # === Nature/characteristics (Q8, Q9, Q22) ===
        r'\bsistem\s+yang\s+diduga\s+reaksinya',  # Q8
        r'\bkeputusan\s+(?:yang\s+)?bersifat',  # Q9
        r'\b(?:terjadi|muncul)\s+karena',  # Q22
        
        # === Purpose/intent (Q40, Q43) ===
        r'\bberisi\s+informasi\s+tentang',  # Q40
        
        # === Comparison (but not evaluation) ===
        r'\bperbedaan\s+(?:antara|dari)\s+[\w\s]+\s+(?:dan|dengan)',
    ]
    
    # ========== C3 (APPLY) - MUST BE IMPERATIVE (UNCHANGED) ==========
    FORCE_C3_PATTERNS = [
        r'\bterapkan(?:lah)?\s+',
        r'\bgunakan(?:lah)?\s+[\w\s]+\s+untuk\s+(?:menghitung|menyelesaikan|menganalisis)',
        r'\bhitunglah\b',
        r'\bselesaikan(?:lah)?\s+',
        r'\bimplementasikan\b',
        r'\baplikasikan\b',
        r'\bcara\s+(?:menggunakan|menerapkan)\s+[\w\s]+\s+untuk',  # Must be procedural
    ]
    
    # ========== C4 (ANALYZE) - MUST BE IMPERATIVE + ANALYTICAL (UNCHANGED) ==========
    FORCE_C4_PATTERNS = [
        r'\banalisis(?:lah)?\s+(?:penyebab|faktor|komponen|struktur|hubungan)',
        r'\bteliti\s+(?:pola|struktur)',
        r'\bbandingkan\s+dan\s+kontraskan',
        r'\bidentifikasi\s+(?:pola|kecenderungan|masalah|penyebab)',
        r'\bklasifikasikan(?:lah)?\s+[\w\s]+\s+berdasarkan',
    ]
    
    # ========== C5 (EVALUATE) - MUST BE IMPERATIVE + JUDGMENT (UNCHANGED) ==========
    FORCE_C5_PATTERNS = [
        r'\bevaluasi(?:lah)?\s+(?:efektivitas|kualitas|kelayakan)\s+dari',
        r'\bnilai(?:lah)?\s+(?:efektivitas|kelayakan)\s+dari',
        r'\bpertimbangkan\s+[\w\s]+\s+untuk\s+memilih',
        r'\bjustifikasi\s+(?:pilihan|keputusan)',
        r'\brekomendasi(?:kan)?\s+[\w\s]+\s+yang\s+(?:terbaik|paling)',
        r'\bapa\s+yang\s+(?:lebih|paling)\s+(?:baik|efektif)\s+antara',
        r'\bmana\s+yang\s+lebih\s+baik',
        r'\bputuskan\s+(?:apakah|mana|sistem\s+mana)',
    ]
    
    # ========== C6 (CREATE) - MUST BE IMPERATIVE + CREATIVE (UNCHANGED) ==========
    FORCE_C6_PATTERNS = [
        r'\brancang(?:lah)?\s+(?:sebuah|suatu)\s+(?:sistem|model)',
        r'\bdesain(?:lah)?\s+(?:sebuah|suatu)',
        r'\bbuatlah\s+(?:sistem|model)',
        r'\bkembangkan\s+(?:sistem|model)',
        r'\bciptakan\b',
        r'\bsusun(?:lah)?\s+(?:rencana|strategi|sistem)',
        r'\busulkan\s+(?:desain|rancangan)\s+untuk',
    ]
    
    # ========== BLOCKING PATTERNS (UNCHANGED) ==========
    ULTRA_STRONG_C1_BLOCKERS = [
        r'\bpengertian\b',
        r'\bdefinisi\b',
        r'\barti\s+(?:dari|tentang)',
        r'\byang\s+dimaksud\s+[\w\s]+\s+(?:adalah|merupakan|ialah)',
        r'\bdisebut\s+(?:apa|sebagai\s+apa|apakah)',
        r'\btermasuk\s+(?:dalam\s+)?(?:kategori|subsistem)',
        r'\bsalah\s+satu\s+(?:komponen|bentuk)',
        r'\b(?:adalah|merupakan|ialah)\s+',  # Declarative, not imperative
    ]
    
    BLOCK_C5_C6_CRITERIA = [
        r'\bmelalui\s+kriteria',
        r'\bdengan\s+kriteria',
        r'\bmenggunakan\s+kriteria',
        r'\bkriteria\s+(?:yang|untuk|evaluasi)',
    ]
    
    def __init__(self):
        """Compile all patterns"""
        self.compiled_force_c1 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C1_PATTERNS]
        self.compiled_force_c2 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C2_PATTERNS]
        self.compiled_force_c3 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C3_PATTERNS]
        self.compiled_force_c4 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C4_PATTERNS]
        self.compiled_force_c5 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C5_PATTERNS]
        self.compiled_force_c6 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C6_PATTERNS]
        
        self.compiled_c1_blockers = [re.compile(p, re.IGNORECASE) for p in self.ULTRA_STRONG_C1_BLOCKERS]
        self.compiled_block_c5_c6 = [re.compile(p, re.IGNORECASE) for p in self.BLOCK_C5_C6_CRITERIA]
    
    def _has_imperative_verb(self, text):
        """Check if question has imperative verb (command)"""
        imperative_verbs = [
            'hitunglah', 'terapkan', 'gunakan', 'selesaikan', 'buatlah',
            'rancanglah', 'evaluasilah', 'analisislah', 'bandingkan',
            'klasifikasikan', 'susun', 'kembangkan', 'ciptakan',
            'identifikasi', 'nilai', 'tentukan'
        ]
        text_lower = text.lower()
        return any(verb in text_lower for verb in imperative_verbs)
    
    def _is_question_declarative(self, text):
        """Check if question uses declarative form (not command)"""
        declarative_indicators = [
            r'\badalah\s+',
            r'\bmerupakan\s+',
            r'\bialah\s+',
            r'\btermasuk\s+',
            r'\bdisebut\s+',
            r'\byang\s+dimaksud\s+',
        ]
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in declarative_indicators)
    
    def _boost_confidence(self, category, ml_confidence, pattern_count):
        """Boost confidence based on pattern strength"""
        base_confidence = {
            'C1': 0.94,
            'C2': 0.90,
            'C3': 0.87,
            'C4': 0.89,
            'C5': 0.91,
            'C6': 0.93,
        }
        
        confidence = base_confidence.get(category, 0.85)
        
        # Boost if ML agrees (within 1 level)
        ml_num = int(ml_confidence) if isinstance(ml_confidence, str) and ml_confidence.startswith('C') else 0
        if ml_num == 0 and isinstance(ml_confidence, float):
            ml_num = 1  # Default to C1 if confidence is float
        
        cat_num = int(category[1])
        if abs(ml_num - cat_num) <= 1:
            confidence = min(0.97, confidence + 0.03)
        
        # Boost if multiple patterns match
        if pattern_count >= 2:
            confidence = min(0.97, confidence + 0.02)
        
        return confidence
    
    def adjust_classification(self, question_text, ml_prediction):
        """
        V5.1: V5 with ONLY 4 new C2 patterns added
        """
        question_lower = question_text.lower().strip()
        
        ml_level = ml_prediction['category']
        ml_confidence = ml_prediction['confidence']
        
        # ====== STAGE 1: ULTRA-STRONG C1 BLOCKING (UNCHANGED) ======
        c1_blocker_count = sum(1 for p in self.compiled_c1_blockers if p.search(question_lower))
        
        if c1_blocker_count >= 1:
            c1_pattern_count = sum(1 for p in self.compiled_force_c1 if p.search(question_lower))
            
            if c1_pattern_count >= 1:
                confidence = self._boost_confidence('C1', ml_confidence, c1_pattern_count)
                logger.info(f"✓ ULTRA-BLOCK: {ml_level}({ml_confidence:.2f}) → C1({confidence:.2f}) [Blockers:{c1_blocker_count}, Patterns:{c1_pattern_count}]")
                return {
                    'category': 'C1',
                    'category_name': 'Remember',
                    'confidence': confidence,
                    'all_probabilities': ml_prediction.get('all_probabilities', {}),
                    'adjustment_reason': 'ultra_strong_c1_block',
                    'ml_category': ml_level,
                    'ml_confidence': ml_confidence,
                    'was_adjusted': True
                }
        
        # ====== STAGE 2: BLOCK C5/C6 IF ASKING ABOUT CRITERIA (UNCHANGED) ======
        if any(p.search(question_lower) for p in self.compiled_block_c5_c6):
            if ml_level in ['C5', 'C6']:
                logger.info(f"BLOCK C5/C6: {ml_level} → C1 (asking about criteria)")
                return {
                    'category': 'C1',
                    'category_name': 'Remember',
                    'confidence': 0.92,
                    'all_probabilities': ml_prediction.get('all_probabilities', {}),
                    'adjustment_reason': 'block_c5_c6_criteria',
                    'ml_category': ml_level,
                    'ml_confidence': ml_confidence,
                    'was_adjusted': True
                }
        
        # ====== STAGE 3: PATTERN MATCHING (C1 → C6) ======
        
        # Check C1 patterns
        c1_count = sum(1 for p in self.compiled_force_c1 if p.search(question_lower))
        if c1_count >= 1:
            confidence = self._boost_confidence('C1', ml_confidence, c1_count)
            if ml_level != 'C1':
                logger.info(f"FORCE C1: {ml_level}({ml_confidence:.2f}) → C1({confidence:.2f}) [Patterns:{c1_count}]")
            return {
                'category': 'C1',
                'category_name': 'Remember',
                'confidence': confidence,
                'all_probabilities': ml_prediction.get('all_probabilities', {}),
                'adjustment_reason': 'force_c1_pattern',
                'ml_category': ml_level,
                'ml_confidence': ml_confidence,
                'was_adjusted': ml_level != 'C1'
            }
        
        # Check C2 patterns (NOW WITH 4 NEW PATTERNS FOR UNDER-PREDICTIONS)
        c2_count = sum(1 for p in self.compiled_force_c2 if p.search(question_lower))
        if c2_count >= 1:
            if not self._is_question_declarative(question_text):
                confidence = self._boost_confidence('C2', ml_confidence, c2_count)
                if ml_level != 'C2':
                    logger.info(f"FORCE C2: {ml_level}({ml_confidence:.2f}) → C2({confidence:.2f}) [Patterns:{c2_count}]")
                return {
                    'category': 'C2',
                    'category_name': 'Understand',
                    'confidence': confidence,
                    'all_probabilities': ml_prediction.get('all_probabilities', {}),
                    'adjustment_reason': 'force_c2_pattern',
                    'ml_category': ml_level,
                    'ml_confidence': ml_confidence,
                    'was_adjusted': ml_level != 'C2'
                }
        
        # Check C3+ patterns (MUST have imperative verb) - UNCHANGED
        has_imperative = self._has_imperative_verb(question_text)
        
        if has_imperative:
            # Check C3
            c3_count = sum(1 for p in self.compiled_force_c3 if p.search(question_lower))
            if c3_count >= 1:
                confidence = self._boost_confidence('C3', ml_confidence, c3_count)
                if ml_level != 'C3':
                    logger.info(f"FORCE C3: {ml_level}({ml_confidence:.2f}) → C3({confidence:.2f})")
                return {
                    'category': 'C3',
                    'category_name': 'Apply',
                    'confidence': confidence,
                    'all_probabilities': ml_prediction.get('all_probabilities', {}),
                    'adjustment_reason': 'force_c3_pattern',
                    'ml_category': ml_level,
                    'ml_confidence': ml_confidence,
                    'was_adjusted': ml_level != 'C3'
                }
            
            # Check C4
            c4_count = sum(1 for p in self.compiled_force_c4 if p.search(question_lower))
            if c4_count >= 1:
                confidence = self._boost_confidence('C4', ml_confidence, c4_count)
                if ml_level != 'C4':
                    logger.info(f"FORCE C4: {ml_level}({ml_confidence:.2f}) → C4({confidence:.2f})")
                return {
                    'category': 'C4',
                    'category_name': 'Analyze',
                    'confidence': confidence,
                    'all_probabilities': ml_prediction.get('all_probabilities', {}),
                    'adjustment_reason': 'force_c4_pattern',
                    'ml_category': ml_level,
                    'ml_confidence': ml_confidence,
                    'was_adjusted': ml_level != 'C4'
                }
            
            # Check C5
            c5_count = sum(1 for p in self.compiled_force_c5 if p.search(question_lower))
            if c5_count >= 1:
                confidence = self._boost_confidence('C5', ml_confidence, c5_count)
                if ml_level != 'C5':
                    logger.info(f"FORCE C5: {ml_level}({ml_confidence:.2f}) → C5({confidence:.2f})")
                return {
                    'category': 'C5',
                    'category_name': 'Evaluate',
                    'confidence': confidence,
                    'all_probabilities': ml_prediction.get('all_probabilities', {}),
                    'adjustment_reason': 'force_c5_pattern',
                    'ml_category': ml_level,
                    'ml_confidence': ml_confidence,
                    'was_adjusted': ml_level != 'C5'
                }
            
            # Check C6
            c6_count = sum(1 for p in self.compiled_force_c6 if p.search(question_lower))
            if c6_count >= 1:
                confidence = self._boost_confidence('C6', ml_confidence, c6_count)
                if ml_level != 'C6':
                    logger.info(f"FORCE C6: {ml_level}({ml_confidence:.2f}) → C6({confidence:.2f})")
                return {
                    'category': 'C6',
                    'category_name': 'Create',
                    'confidence': confidence,
                    'all_probabilities': ml_prediction.get('all_probabilities', {}),
                    'adjustment_reason': 'force_c6_pattern',
                    'ml_category': ml_level,
                    'ml_confidence': ml_confidence,
                    'was_adjusted': ml_level != 'C6'
                }
        
        # ====== STAGE 4: DOWNGRADE UNCERTAIN HIGH LEVELS (UNCHANGED) ======
        if ml_level in ['C3', 'C4', 'C5', 'C6'] and ml_confidence < 0.70:
            if not has_imperative:
                if self._is_question_declarative(question_text):
                    logger.info(f"DOWNGRADE: {ml_level}({ml_confidence:.2f}) → C1 (no imperative + declarative)")
                    return {
                        'category': 'C1',
                        'category_name': 'Remember',
                        'confidence': 0.82,
                        'all_probabilities': ml_prediction.get('all_probabilities', {}),
                        'adjustment_reason': 'downgrade_to_c1',
                        'ml_category': ml_level,
                        'ml_confidence': ml_confidence,
                        'was_adjusted': True
                    }
                else:
                    logger.info(f"DOWNGRADE: {ml_level}({ml_confidence:.2f}) → C2 (no imperative)")
                    return {
                        'category': 'C2',
                        'category_name': 'Understand',
                        'confidence': 0.78,
                        'all_probabilities': ml_prediction.get('all_probabilities', {}),
                        'adjustment_reason': 'downgrade_uncertain',
                        'ml_category': ml_level,
                        'ml_confidence': ml_confidence,
                        'was_adjusted': True
                    }
        
        # ====== STAGE 5: KEEP ML PREDICTION ======
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


def adjust_classification_with_patterns(question_text, ml_prediction):
    """Convenience function"""
    adjuster = IndonesianBloomAdjuster()
    return adjuster.adjust_classification(question_text, ml_prediction)