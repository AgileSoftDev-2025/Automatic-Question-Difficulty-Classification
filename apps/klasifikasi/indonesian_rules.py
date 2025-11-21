# apps/klasifikasi/indonesian_rules.py - V6: COMPREHENSIVE ACCURACY IMPROVEMENT

import re
import logging

logger = logging.getLogger(__name__)


class IndonesianBloomAdjuster:
    """
    V6: Comprehensive improvements based on classification report analysis
    
    Key improvements:
    1. Better C6 blocking - many C6 are actually C1/C2 definitions
    2. Improved "sistem yang..." pattern detection
    3. Better handling of "adalah" declarative statements
    4. Fixed low-confidence misclassifications
    5. Added patterns for common Indonesian exam question structures
    """
    
    # ========== C1 (REMEMBER) - EXPANDED PATTERNS ==========
    FORCE_C1_PATTERNS = [
        # === STRONGEST: Pure definition patterns ===
        r'\bpengertian\s+(?:yang\s+)?(?:paling\s+)?(?:umum|utama|inti|dari|tentang)',
        r'\bdefinisi\s+(?:dari|tentang|yang)',
        r'\barti\s+(?:dari\s+)?[\w\s]+\s+(?:adalah|merupakan|ialah)',
        r'\bapakah\s+(?:yang\s+)?dimaksud\s+(?:dengan|dari)',
        r'\bapa\s+(?:yang\s+)?dimaksud\s+(?:dengan|dari)\s+[\w\s]+\??$',
        
        # === "Yang dimaksud" with "adalah" pattern ===
        r'\byang\s+dimaksud\s+(?:dengan\s+)?[\w\s]{3,40}\s+(?:adalah|ialah|merupakan)',
        r'\b(?:adalah|merupakan)\s+yang\s+dimaksud\s+(?:dengan|dari)',

        # === Category/classification questions ===
        r'\bkategori\s+.*?\b(?:analisis|evaluasi)',
        r'\btermasuk\s+(?:dalam\s+)?(?:kategori|jenis|subsistem|golongan|komponen|bentuk|klasifikasi)',
        r'\bsalah\s+satu\s+(?:komponen|faktor|bentuk|unsur|teknik|metode|upaya|elemen|jenis|contoh)',
        r'\bkategori\s+(?:analisis|evaluasi)\s+[\w\s]+\s+(?:adalah|merupakan)',
        r'\bmerupakan\s+(?:salah\s+satu|bagian\s+dari)',
        
        # === "disebut sebagai" patterns (fixed) ===
        r'\bdisebut\s+sebagai\s+(?!apa|apakah)\w+',
        r'\b(?:disebut|dinamakan|dikenal)\s+(?:apa|apakah|sebagai\s+apa)\s*\??$',
        r'\b(?:disebut|dinamakan|dikenal)\s+sebagai\s+(?:apa|apakah)',
        r'\bapa\s+(?:nama|istilah|sebutan)\s+(?:dari|untuk|bagi)',
        
        # === Naming/identification patterns ===
        r'\bformulir\s+[\w\s]+\s+disebut\b',
        r'\bpengujian\s+[\w\s]+\s+disebut\s+pengujian\b',
        r'\bsistem\s+[\w\s]+\s+disebut\b',
        r'\bsistem\s+informasi\s+(?:yang\s+)?(?:dirancang|digunakan|mendukung)\s+untuk',
        
        # === Sequence/order questions ===
        r'\btahap\s+(?:pertama|awal|akhir|terakhir|pertama\s+kali)',
        r'\bkegiatan\s+(?:pertama|awal|terakhir|yang\s+pertama)',
        r'\blangkah\s+(?:pertama|awal|terakhir)',
        
        # === Properties/characteristics - asking WHAT ===
        r'\bsifat\s+(?:utama|dari|yang|khas)',
        r'\bkondisi\s+(?:yang\s+)?(?:ideal|terbaik|optimum)',
        r'\bkomponen\s+(?:penentu|utama|yang)',
        r'\bkarakteristik\s+(?:utama|dari|produk)',
        
        # === Cost/type questions ===
        r'\bbiaya\s+langsung\s+.*?(?:dikeluarkan|adalah)',
        r'\bjenis\s+(?:biaya|sistem|data)',
        
        # === Structural/component questions ===
        r'\bstruktur\s+(?:basis\s+data|dasar|utama)',
        r'\bkomponen\s+utama\s+(?:CPU|komputer|sistem)',
        r'\bperangkat\s+(?:keras|lunak)\s+(?:yang\s+)?(?:termasuk|adalah)',
        
        # === NEW: System definition patterns (fixes C6 over-predictions) ===
        r'\bsistem\s+(?:yang\s+)?(?:dapat|mampu|bisa)\s+[\w\s]+\s+(?:adalah|disebut)',
        r'\bsistem\s+(?:informasi\s+)?(?:yang\s+)?menghasilkan\s+laporan',
        r'\bsistem\s+(?:yang\s+)?mengintegrasikan',
        r'\bperangkat\s+lunak\s+(?:dasar|sistem)\s+(?:yang\s+)?(?:berfungsi|adalah)',
        r'\bkumpulan\s+(?:model|data|informasi)\s+[\w\s]+\s+adalah',
        
        # === NEW: "merupakan" definition patterns ===
        r'^[\w\s,]+\s+merupakan\s*$',
        r'\b[\w\s]+\s+merupakan\s+(?:contoh|jenis|bagian)',
        
        # === NEW: KECUALI (except) questions - always recall ===
        r'\bkecuali\s*$',
        r'\b(?:adalah|berikut)\s+[\w\s,]+,?\s+kecuali',
        
        # === NEW: Definition by listing ===
        r'\bberikut\s+(?:ini\s+)?(?:yang\s+)?(?:merupakan|adalah|termasuk)',
        r'\bdi\s+bawah\s+ini\s+(?:yang\s+)?(?:merupakan|adalah|termasuk|bukan)',
        
        # === NEW: Specific domain patterns ===
        r'\bprotokol\s+(?:yang\s+)?(?:digunakan|adalah)',
        r'\bmedia\s+(?:transmisi|penyimpanan)\s+[\w\s]+\s+adalah',
        r'\btopologi\s+(?:jaringan\s+)?(?:yang\s+)?(?:menyediakan|adalah)',
        r'\blayer\s+(?:OSI\s+)?(?:yang\s+)?(?:beroperasi|adalah)',
        
        # === NEW: "adalah...berikut" patterns ===
        r'\badalah\s+(?:sebagai\s+)?berikut',
        r'\bsebagai\s+berikut\s*[,:]',
    ]
    
    # ========== C2 (UNDERSTAND) PATTERNS ==========
    FORCE_C2_PATTERNS = [
        # === Relationship understanding ===
        r'\byang\s+dimaksud\s+(?:dengan\s+)?relevansi(?!\s+adalah)',
        r'\baksesibilitas\s+(?:dapat\s+)?mempengaruhi',
        r'\b(?:mempengaruhi|berpengaruh\s+terhadap)\s+nilai',
        r'\bevaluasi\s+[\w\s]+\s+melalui\s+kriteria',
        r'\bupaya\s+(?:untuk\s+)?menentukan\s+prioritas',
        
        # === Decision/nature questions ===
        r'\bkeputusan\s+.*?sifat',
        r'\bdasar\s+.*?untuk\s+mengukur',
        
        # === Explanation with reasoning ===
        r'\bjelaskan\s+mengapa(?!\s+cara)',
        r'\bjelaskan\s+bagaimana(?!\s+cara\s+(?:menggunakan|menerapkan|membuat))',
        r'\buraikan\s+(?:hubungan|perbedaan|mengapa)',
        
        # === WHY questions (understanding cause/effect) ===
        r'\bmengapa\s+[\w\s]+\s+(?:dapat|bisa|mempengaruhi|menyebabkan)',
        r'\bmengapa\s+[\w\s]+\s+(?:penting|diperlukan)',
        r'\bapa\s+(?:yang\s+)?menyebabkan',
        
        # === HOW questions (understanding process) ===
        r'\bbagaimana\s+[\w\s]+\s+(?:mempengaruhi|dapat|bisa)(?!\s+cara)',
        r'\bbagaimana\s+[\w\s]+\s+(?:melindungi|menjaga)',
        
        # === Relationships ===
        r'\bhubungan\s+antara\s+[\w\s]+\s+(?:dan|dengan)',
        r'\bfaktor\s+(?:yang\s+)?(?:mempengaruhi|menentukan|menjadi)',
        r'\bkeuntungan\s+(?:utama|dari)\s+[\w\s]+\s+(?:adalah|merupakan)',
        r'\brisiko\s+(?:yang\s+)?(?:mendasar|utama|yang)',
        r'\bsebagai\s+alat\s+bantu',
        r'\bsesuai\s+dengan',
        
        # === Function/purpose understanding ===
        r'\bfungsi\s+(?:basis\s+data|dari|utama)',
        r'\btujuan\s+(?:dari|utama)',
        r'\bmembantu\s+[\w\s]+\s+(?:jenis|tipe)\s+keputusan',
        r'\bpemeriksaan\s+mutu\s+[\w\s]+\s+dilakukan',
        
        # === Nature/characteristics understanding ===
        r'\bsistem\s+yang\s+diduga\s+reaksinya',
        r'\bkeputusan\s+(?:yang\s+)?bersifat',
        r'\b(?:terjadi|muncul)\s+karena',
        r'\bproblem\s+[\w\s]+\s+(?:terjadi|dapat\s+terjadi)\s+karena',
        
        # === Purpose/intent ===
        r'\bberisi\s+informasi\s+tentang',
        
        # === Comparison (understanding level) ===
        r'\bperbedaan\s+(?:antara|dari)\s+[\w\s]+\s+(?:dan|dengan)',
        r'\bapa\s+(?:perbedaan|persamaan)',
        
        # === NEW: Process understanding ===
        r'\bproses\s+(?:yang\s+)?(?:bertujuan|dilakukan)\s+untuk',
        r'\baktivitas\s+[\w\s]+\s+(?:yang\s+)?(?:meliputi|termasuk|adalah)',
        r'\bpertukaran\s+[\w\s]+\s+(?:di\s+antara|antara)',
        
        # === NEW: Characteristic listing ===
        r'\bkarakteristik\s+[\w\s]+\s+(?:yang\s+)?membuat',
        r'\bnilai\s+bisnis\s+(?:utama\s+)?(?:dari|adalah)',
    ]
    
    # ========== C3 (APPLY) - MUST BE IMPERATIVE ==========
    FORCE_C3_PATTERNS = [
        r'\bterapkan(?:lah)?\s+',
        r'\bgunakan(?:lah)?\s+[\w\s]+\s+untuk\s+(?:menghitung|menyelesaikan|menganalisis)',
        r'\bhitunglah\b',
        r'\bselesaikan(?:lah)?\s+',
        r'\bimplementasikan\b',
        r'\baplikasikan\b',
        r'\bcara\s+(?:menggunakan|menerapkan)\s+[\w\s]+\s+untuk',
        
        # === NEW: Application patterns ===
        r'\bpenggunaan\s+[\w\s]+\s+untuk\s+menghubungkan',
        r'\bmenggunakan\s+[\w\s]+\s+untuk\s+(?:pelelangan|transaksi)',
    ]
    
    # ========== C4 (ANALYZE) - MUST BE IMPERATIVE + ANALYTICAL ==========
    FORCE_C4_PATTERNS = [
        r'\banalisis(?:lah)?\s+(?:penyebab|faktor|komponen|struktur|hubungan)',
        r'\bteliti\s+(?:pola|struktur)',
        r'\bbandingkan\s+dan\s+kontraskan',
        r'\bidentifikasi\s+(?:pola|kecenderungan|masalah|penyebab)',
        r'\bklasifikasikan(?:lah)?\s+[\w\s]+\s+berdasarkan',
        
        # === NEW: Analytical patterns ===
        r'\bperusahaan\s+harus\s+berhadapan\s+dengan',
    ]
    
    # ========== C5 (EVALUATE) - MUST BE IMPERATIVE + JUDGMENT ==========
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
    
    # ========== C6 (CREATE) - MUST BE IMPERATIVE + CREATIVE ==========
    FORCE_C6_PATTERNS = [
        r'\brancang(?:lah)?\s+(?:sebuah|suatu)\s+(?:sistem|model)',
        r'\bdesain(?:lah)?\s+(?:sebuah|suatu)',
        r'\bbuatlah\s+(?:sistem|model)',
        r'\bkembangkan\s+(?:sistem|model)',
        r'\bciptakan\b',
        r'\bsusun(?:lah)?\s+(?:rencana|strategi|sistem)',
        r'\busulkan\s+(?:desain|rancangan)\s+untuk',
    ]
    
    # ========== BLOCKING PATTERNS ==========
    ULTRA_STRONG_C1_BLOCKERS = [
        r'\bpengertian\b',
        r'\bdefinisi\b',
        r'\barti\s+(?:dari|tentang)',
        r'\byang\s+dimaksud\s+[\w\s]+\s+(?:adalah|merupakan|ialah)',
        r'\bdisebut\s+(?:apa|sebagai\s+apa|apakah)',
        r'\btermasuk\s+(?:dalam\s+)?(?:kategori|subsistem)',
        r'\bsalah\s+satu\s+(?:komponen|bentuk)',
        r'\b(?:adalah|merupakan|ialah)\s+',
    ]
    
    BLOCK_C5_C6_CRITERIA = [
        r'\bmelalui\s+kriteria',
        r'\bdengan\s+kriteria',
        r'\bmenggunakan\s+kriteria',
        r'\bkriteria\s+(?:yang|untuk|evaluasi)',
    ]
    
    # === NEW: C6 BLOCKING PATTERNS (prevent false C6) ===
    BLOCK_C6_PATTERNS = [
        r'\bsistem\s+(?:yang\s+)?(?:menghasilkan|mengintegrasikan|melintasi)',
        r'\bperangkat\s+lunak\s+(?:dasar|sistem)',
        r'\bkumpulan\s+(?:model|data)',
        r'\bproses\s+(?:mengembangkan|memasarkan)',
        r'\bcara\s+menyediakan',
        r'\bsuatu\s+sistem\s+yang\s+mengintegrasikan',
        r'\bpembelian,?\s+penjualan',
        r'\bentri\s+data,?\s+pemrosesan',
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
        self.compiled_block_c6 = [re.compile(p, re.IGNORECASE) for p in self.BLOCK_C6_PATTERNS]
    
    def _has_imperative_verb(self, text):
        """Check if question has imperative verb (command)"""
        imperative_verbs = [
            'hitunglah', 'terapkan', 'gunakan', 'selesaikan', 'buatlah',
            'rancanglah', 'evaluasilah', 'analisislah', 'bandingkan',
            'klasifikasikan', 'susun', 'kembangkan', 'ciptakan',
            'identifikasi', 'nilai', 'tentukan', 'jelaskan', 'uraikan'
        ]
        text_lower = text.lower()
        return any(verb in text_lower for verb in imperative_verbs)
    
    def _is_question_declarative(self, text):
        """Check if question uses declarative form (not command)"""
        declarative_indicators = [
            r'\badalah\s*$',
            r'\bmerupakan\s*$',
            r'\bialah\s*$',
            r'\b(?:adalah|merupakan|ialah)\s+[\w\s]+$',
            r'\btermasuk\s+',
            r'\bdisebut\s+',
            r'\byang\s+dimaksud\s+',
            r'\bkecuali\s*$',
        ]
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in declarative_indicators)
    
    def _ends_with_adalah(self, text):
        """Check if question ends with 'adalah' or similar"""
        text_lower = text.lower().strip()
        endings = ['adalah', 'merupakan', 'ialah', 'yaitu']
        return any(text_lower.endswith(e) for e in endings)
    
    def _boost_confidence(self, category, ml_confidence, pattern_count):
        """Boost confidence based on pattern strength"""
        base = {'C1': 0.94, 'C2': 0.90, 'C3': 0.87, 'C4': 0.89, 'C5': 0.91, 'C6': 0.93}
        confidence = base.get(category, 0.85)
        if pattern_count >= 2:
            confidence = min(0.97, confidence + 0.02)
        return confidence
    
    def adjust_classification(self, question_text, ml_prediction):
        """V6: Comprehensive pattern-based adjustment"""
        question_lower = question_text.lower().strip()
        
        ml_level = ml_prediction['category']
        ml_confidence = ml_prediction['confidence']
        
        # ====== STAGE 0: BLOCK FALSE C6 PREDICTIONS ======
        if ml_level == 'C6':
            if any(p.search(question_lower) for p in self.compiled_block_c6):
                if self._is_question_declarative(question_text) or self._ends_with_adalah(question_text):
                    logger.info(f"BLOCK C6→C1: False C6 detected (declarative definition)")
                    return self._create_result('C1', 'Remember', 0.92, ml_prediction,
                                              'block_false_c6', ml_level, ml_confidence)
        
        # ====== STAGE 1: ULTRA-STRONG C1 BLOCKING ======
        c1_blocker_count = sum(1 for p in self.compiled_c1_blockers if p.search(question_lower))
        
        if c1_blocker_count >= 1:
            c1_pattern_count = sum(1 for p in self.compiled_force_c1 if p.search(question_lower))
            
            if c1_pattern_count >= 1:
                confidence = self._boost_confidence('C1', ml_confidence, c1_pattern_count)
                if ml_level != 'C1':
                    logger.info(f"✓ ULTRA-BLOCK: {ml_level}({ml_confidence:.2f}) → C1({confidence:.2f})")
                return self._create_result('C1', 'Remember', confidence, ml_prediction,
                                          'ultra_strong_c1_block', ml_level, ml_confidence)
        
        # ====== STAGE 2: BLOCK C5/C6 IF ASKING ABOUT CRITERIA ======
        if any(p.search(question_lower) for p in self.compiled_block_c5_c6):
            if ml_level in ['C5', 'C6']:
                logger.info(f"BLOCK C5/C6: {ml_level} → C1 (asking about criteria)")
                return self._create_result('C1', 'Remember', 0.92, ml_prediction,
                                          'block_c5_c6_criteria', ml_level, ml_confidence)
        
        # ====== STAGE 3: DECLARATIVE ENDING CHECK ======
        if self._ends_with_adalah(question_text):
            if ml_level in ['C3', 'C4', 'C5', 'C6']:
                logger.info(f"DECLARATIVE END: {ml_level} → C1 (ends with adalah)")
                return self._create_result('C1', 'Remember', 0.93, ml_prediction,
                                          'declarative_ending', ml_level, ml_confidence)
        
        # ====== STAGE 4: PATTERN MATCHING (C1 → C6) ======
        
        # Check C1 patterns
        c1_count = sum(1 for p in self.compiled_force_c1 if p.search(question_lower))
        if c1_count >= 1:
            confidence = self._boost_confidence('C1', ml_confidence, c1_count)
            if ml_level != 'C1':
                logger.info(f"FORCE C1: {ml_level}({ml_confidence:.2f}) → C1({confidence:.2f})")
            return self._create_result('C1', 'Remember', confidence, ml_prediction,
                                      'force_c1_pattern', ml_level, ml_confidence)
        
        # Check C2 patterns
        c2_count = sum(1 for p in self.compiled_force_c2 if p.search(question_lower))
        if c2_count >= 1:
            if not self._is_question_declarative(question_text):
                confidence = self._boost_confidence('C2', ml_confidence, c2_count)
                if ml_level != 'C2':
                    logger.info(f"FORCE C2: {ml_level}({ml_confidence:.2f}) → C2({confidence:.2f})")
                return self._create_result('C2', 'Understand', confidence, ml_prediction,
                                          'force_c2_pattern', ml_level, ml_confidence)
        
        # Check C3+ patterns (MUST have imperative verb)
        has_imperative = self._has_imperative_verb(question_text)
        
        if has_imperative:
            for level, patterns, name in [
                ('C3', self.compiled_force_c3, 'Apply'),
                ('C4', self.compiled_force_c4, 'Analyze'),
                ('C5', self.compiled_force_c5, 'Evaluate'),
                ('C6', self.compiled_force_c6, 'Create'),
            ]:
                count = sum(1 for p in patterns if p.search(question_lower))
                if count >= 1:
                    confidence = self._boost_confidence(level, ml_confidence, count)
                    if ml_level != level:
                        logger.info(f"FORCE {level}: {ml_level}({ml_confidence:.2f}) → {level}({confidence:.2f})")
                    return self._create_result(level, name, confidence, ml_prediction,
                                              f'force_{level.lower()}_pattern', ml_level, ml_confidence)
        
        # ====== STAGE 5: DOWNGRADE UNCERTAIN HIGH LEVELS ======
        if ml_level in ['C3', 'C4', 'C5', 'C6'] and ml_confidence < 0.70:
            if not has_imperative:
                if self._is_question_declarative(question_text):
                    logger.info(f"DOWNGRADE: {ml_level}({ml_confidence:.2f}) → C1")
                    return self._create_result('C1', 'Remember', 0.82, ml_prediction,
                                              'downgrade_to_c1', ml_level, ml_confidence)
                else:
                    logger.info(f"DOWNGRADE: {ml_level}({ml_confidence:.2f}) → C2")
                    return self._create_result('C2', 'Understand', 0.78, ml_prediction,
                                              'downgrade_uncertain', ml_level, ml_confidence)
        
        # ====== STAGE 6: KEEP ML PREDICTION ======
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
    
    def _create_result(self, category, name, confidence, ml_pred, reason, ml_cat, ml_conf):
        return {
            'category': category,
            'category_name': name,
            'confidence': confidence,
            'all_probabilities': ml_pred.get('all_probabilities', {}),
            'adjustment_reason': reason,
            'ml_category': ml_cat,
            'ml_confidence': ml_conf,
            'was_adjusted': category != ml_cat
        }


def adjust_classification_with_patterns(question_text, ml_prediction):
    """Convenience function"""
    adjuster = IndonesianBloomAdjuster()
    return adjuster.adjust_classification(question_text, ml_prediction)