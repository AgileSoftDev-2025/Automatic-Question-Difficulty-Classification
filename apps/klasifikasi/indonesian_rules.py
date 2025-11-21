# apps/klasifikasi/indonesian_rules.py - V7: ANTI-HALLUCINATION FIX

import re
import logging

logger = logging.getLogger(__name__)


class IndonesianBloomAdjuster:
    """
    V7: Critical fix for "High-Level Hallucination" - system over-predicting C5/C6
    
    Root causes fixed:
    1. "Disebut" questions always misclassified as C3/C6
    2. System definitions ("Sistem yang...") triggered C6 instead of C1
    3. Long technical descriptions confused as higher-order thinking
    4. Keywords like "formulir", "laporan" auto-triggered C6
    5. "Cara" (way/method) triggered C3/C6 for definitional questions
    """
    
    # ========== ULTRA-PRIORITY: C1 DEFINITION BLOCKERS ==========
    # These patterns MUST force C1, regardless of other signals
    ABSOLUTE_C1_BLOCKERS = [
        # "Disebut" patterns - ALWAYS C1 (Fixes #48-16, #48-39, #94-21, #94-24)
        r'\bdisebut\s+(?:sebagai\s+)?(?:apa|apakah)\s*\??$',
        r'\b(?:apa|apakah)\s+yang\s+disebut\b',
        r'\b[\w\s]+\s+disebut\s*\??$',
        r'\bdinamakan\s+(?:apa|apakah)',
        r'\bdikenal\s+sebagai\s+(?:apa|apakah)',
        r'\bapa\s+(?:nama|istilah|sebutan)\s+(?:dari|untuk)',
        
        # "Adalah" definition patterns - ALWAYS C1
        r'\b[\w\s]+\s+adalah\s*\.?\s*$',
        r'\byang\s+dimaksud\s+(?:dengan\s+)?[\w\s]+\s+adalah\s*$',
        r'\b[\w\s]+\s+merupakan\s*\.?\s*$',
        r'\b[\w\s]+\s+ialah\s*\.?\s*$',
        
        # Fill-in-blank/completion (Fixes #93-42)
        r'\.{3,}',  # "..." ellipsis
        r'\b(?:adalah|merupakan)\s+\.{3,}',
        r'\.{3,}\s+(?:adalah|merupakan)',
        
        # "Termasuk" (includes/belongs to) - ALWAYS C1 (Fixes #93-9)
        r'\btermasuk\s+(?:dalam\s+)?(?:kategori|jenis|golongan|tipe)',
        r'\bkategori\s+[\w\s]+\s+termasuk',
        
        # System/form definitions that look like C6 (Fixes #48-16, #48-39, #93-40)
        r'\bsistem\s+(?:informasi\s+)?(?:yang\s+)?(?:dirancang|digunakan|dibuat)\s+[\w\s]+\s+disebut',
        r'\bformulir\s+(?:yang\s+)?(?:digunakan|dibuat)\s+[\w\s]+\s+disebut',
        r'\blaporan\s+(?:yang\s+)?(?:digunakan|dibuat)\s+[\w\s]+\s+disebut',
        
        # "Berisi informasi tentang" (Fixes #93-40)
        r'\bberisi\s+informasi\s+(?:tentang|mengenai)',
        r'\bharus\s+berisi\s+informasi',
        
        # Technical terminology identification (Fixes #94-24)
        r'\bstruktur\s+[\w\s]+\s+disebut',
        r'\bfungsi\s+[\w\s]+\s+disebut',
        r'\bperangkat\s+[\w\s]+\s+disebut',
        
        # "Tahap/langkah pertama" (sequence recall) (Fixes #48-30)
        r'\btahap\s+(?:pertama|awal|terakhir)',
        r'\blangkah\s+(?:pertama|awal|terakhir)',
        r'\bkegiatan\s+(?:pertama|awal)',
        
        # "Yaitu berupa" (namely/that is) (Fixes #94-48)
        r'\byaitu\s+berupa',
        r'\byaitu\s+[\w\s]+$',
        r'\bberupa\s+[\w\s]+$',
    ]
    
    # ========== C1 (REMEMBER) - COMPREHENSIVE PATTERNS ==========
    FORCE_C1_PATTERNS = [
        # === Core definition patterns ===
        r'\bpengertian\s+(?:yang\s+)?(?:paling\s+)?(?:umum|utama|dari|tentang)',
        r'\bdefinisi\s+(?:dari|tentang|yang)',
        r'\barti\s+(?:dari\s+)?[\w\s]+\s+(?:adalah|merupakan)',
        r'\bapakah\s+(?:yang\s+)?dimaksud\s+(?:dengan|dari)',
        r'\bapa\s+(?:yang\s+)?dimaksud\s+(?:dengan|dari)',
        
        # === "Yang dimaksud" patterns ===
        r'\byang\s+dimaksud\s+(?:dengan\s+)?[\w\s]{3,40}\s+(?:adalah|merupakan)',
        
        # === Category/classification ===
        r'\bkategori\s+.*?\b(?:analisis|evaluasi)',
        r'\bsalah\s+satu\s+(?:komponen|faktor|bentuk|unsur|teknik|metode)',
        r'\bmerupakan\s+(?:salah\s+satu|bagian\s+dari)',
        
        # === Naming patterns ===
        r'\bsistem\s+informasi\s+(?:yang\s+)?mendukung',
        r'\bpengujian\s+[\w\s]+\s+disebut\s+pengujian',
        
        # === Properties/characteristics - asking WHAT ===
        r'\bsifat\s+(?:utama|dari|yang|khas)',
        r'\bkondisi\s+(?:yang\s+)?(?:ideal|terbaik)',
        r'\bkarakteristik\s+(?:utama|dari|produk)',
        
        # === NEW: "Cara" when asking for definition (Fixes #94-48) ===
        r'\bcara\s+[\w\s]+\s+yaitu\s+berupa',
        r'\bcara\s+[\w\s]+\s+adalah',
        r'\bmetode\s+[\w\s]+\s+yaitu',
        
        # === KECUALI (except) questions ===
        r'\bkecuali\s*[:\.]?\s*$',
        r'\b(?:adalah|berikut)\s+[\w\s,]+,?\s+kecuali',
        
        # === Definition by listing ===
        r'\bberikut\s+(?:ini\s+)?(?:yang\s+)?(?:merupakan|adalah|termasuk)',
        r'\bdi\s+bawah\s+ini\s+(?:yang\s+)?(?:merupakan|adalah)',
        
        # === Domain-specific patterns ===
        r'\bprotokol\s+(?:yang\s+)?(?:digunakan|adalah)',
        r'\bmedia\s+(?:transmisi|penyimpanan)\s+[\w\s]+\s+adalah',
        r'\btopologi\s+(?:jaringan\s+)?yang',
        r'\blayer\s+(?:OSI\s+)?yang',
        
        # === "Adalah...berikut" patterns ===
        r'\badalah\s+(?:sebagai\s+)?berikut',
        r'\bsebagai\s+berikut\s*[,:.]',
        
        # === NEW: System characteristics (not creation) ===
        r'\bsistem\s+yang\s+(?:dapat\s+)?diduga\s+reaksinya',
        r'\bkeputusan\s+(?:yang\s+)?bersifat',
        
        # === NEW: Cost/type definitions ===
        r'\bbiaya\s+[\w\s]+\s+(?:yang\s+)?dikeluarkan',
        r'\bjenis\s+(?:biaya|sistem|data|keputusan)',
        
        # === NEW: Component listing ===
        r'\bkomponen\s+(?:penentu|utama|dari)',
        r'\bperangkat\s+(?:keras|lunak)\s+(?:yang\s+)?termasuk',
    ]
    
    # ========== C2 (UNDERSTAND) PATTERNS ==========
    FORCE_C2_PATTERNS = [
        # === Relationship understanding ===
        r'\byang\s+dimaksud\s+(?:dengan\s+)?relevansi(?!\s+adalah)',
        r'\baksesibilitas\s+(?:dapat\s+)?mempengaruhi',
        r'\bmempengaruhi\s+nilai',
        r'\bupaya\s+(?:untuk\s+)?menentukan\s+prioritas',
        
        # === Explanation with reasoning ===
        r'\bjelaskan\s+mengapa(?!\s+cara)',
        r'\bjelaskan\s+bagaimana(?!\s+cara\s+(?:menggunakan|menerapkan))',
        r'\buraikan\s+(?:hubungan|perbedaan|mengapa)',
        
        # === WHY questions ===
        r'\bmengapa\s+[\w\s]+\s+(?:dapat|mempengaruhi|menyebabkan)',
        r'\bmengapa\s+[\w\s]+\s+(?:penting|diperlukan)',
        r'\bapa\s+(?:yang\s+)?menyebabkan',
        
        # === HOW questions (process understanding) ===
        r'\bbagaimana\s+[\w\s]+\s+mempengaruhi(?!\s+cara)',
        r'\bbagaimana\s+auditor\s+(?:memperoleh|mendapatkan)',
        
        # === Relationships ===
        r'\bhubungan\s+antara\s+[\w\s]+\s+(?:dan|dengan)',
        r'\bfaktor\s+(?:yang\s+)?(?:mempengaruhi|menentukan)',
        r'\bkeuntungan\s+(?:utama|dari)',
        r'\brisiko\s+(?:yang\s+)?(?:mendasar|utama)',
        
        # === Function/purpose understanding ===
        r'\bfungsi\s+(?:basis\s+data|dari|utama)(?!\s+disebut)',
        r'\btujuan\s+(?:dari|utama)(?!\s+adalah\s*$)',
        r'\bmembantu\s+[\w\s]+\s+jenis\s+keputusan',
        
        # === Purpose/basis (Fixes #96-12, #96-14) ===
        r'\bdasar\s+(?:untuk\s+)?(?:mengukur|opini)',
        r'\bberdasarkan\s+(?:pada|atas)',
        r'\bditurunkan\s+dari',
        
        # === NEW: Process understanding (not application) ===
        r'\bproses\s+(?:yang\s+)?(?:bertujuan|dilakukan)',
        r'\baktivitas\s+[\w\s]+\s+(?:yang\s+)?meliputi',
    ]
    
    # ========== C3 (APPLY) - MUST BE IMPERATIVE ==========
    FORCE_C3_PATTERNS = [
        r'\bterapkan(?:lah)?\s+',
        r'\bgunakan(?:lah)?\s+[\w\s]+\s+untuk\s+(?:menghitung|menyelesaikan)',
        r'\bhitunglah\b',
        r'\bselesaikan(?:lah)?\s+',
        r'\bimplementasikan\b',
        r'\baplikasikan\b',
        
        # === Application scenarios ===
        r'\bpenggunaan\s+[\w\s]+\s+untuk\s+(?:menghubungkan|transaksi)',
    ]
    
    # ========== C4 (ANALYZE) - MUST BE IMPERATIVE + ANALYTICAL ==========
    FORCE_C4_PATTERNS = [
        r'\banalisis(?:lah)?\s+(?:penyebab|faktor|komponen|struktur)',
        r'\bteliti\s+(?:pola|struktur)',
        r'\bbandingkan\s+dan\s+kontraskan',
        r'\bidentifikasi\s+(?:pola|kecenderungan|masalah|penyebab)',
        r'\bklasifikasikan(?:lah)?\s+[\w\s]+\s+berdasarkan',
        
        # === Analytical challenges ===
        r'\bperusahaan\s+harus\s+berhadapan\s+dengan',
    ]
    
    # ========== C5 (EVALUATE) - MUST BE IMPERATIVE + JUDGMENT ==========
    FORCE_C5_PATTERNS = [
        r'\bevaluasi(?:lah)?\s+(?:efektivitas|kualitas|kelayakan)',
        r'\bnilai(?:lah)?\s+(?:efektivitas|kelayakan)',
        r'\bpertimbangkan\s+[\w\s]+\s+untuk\s+memilih',
        r'\bjustifikasi\s+(?:pilihan|keputusan)',
        r'\brekomendasi(?:kan)?\s+[\w\s]+\s+yang\s+(?:terbaik|paling)',
        r'\bapa\s+yang\s+(?:lebih|paling)\s+(?:baik|efektif)',
        r'\bmana\s+yang\s+lebih\s+baik',
        r'\bputuskan\s+(?:apakah|mana)',
    ]
    
    # ========== C6 (CREATE) - MUST BE IMPERATIVE + CREATIVE ==========
    FORCE_C6_PATTERNS = [
        r'\brancang(?:lah)?\s+(?:sebuah|suatu)\s+(?:sistem|model)',
        r'\bdesain(?:lah)?\s+(?:sebuah|suatu)',
        r'\bbuatlah\s+(?:sistem|model|rancangan)',
        r'\bkembangkan\s+(?:sistem|model)',
        r'\bciptakan\b',
        r'\bsusun(?:lah)?\s+(?:rencana|strategi|sistem)',
        r'\busulkan\s+(?:desain|rancangan)',
    ]
    
    # ========== CRITICAL: BLOCK FALSE C5/C6 ==========
    BLOCK_C5_C6_IF_ASKING_ABOUT = [
        r'\bmelalui\s+kriteria',
        r'\bdengan\s+kriteria',
        r'\bmenggunakan\s+kriteria',
        r'\bkriteria\s+(?:yang|untuk|evaluasi)',
        r'\bdasar\s+(?:untuk\s+)?opini',  # Fixes #96-12
    ]
    
    BLOCK_C6_DESCRIPTIVE = [
        # These describe systems, not ask to create them
        r'\bsistem\s+(?:yang\s+)?(?:menghasilkan|mengintegrasikan|melintasi)',
        r'\bperangkat\s+lunak\s+(?:dasar|sistem)',
        r'\bkumpulan\s+(?:model|data)',
        r'\bsuatu\s+sistem\s+yang\s+mengintegrasikan',
        r'\bentri\s+data,?\s+pemrosesan',
        
        # "Cara menyediakan" when asking definition (Fixes #94-48)
        r'\bcara\s+menyediakan\s+[\w\s]+\s+yaitu',
    ]
    
    def __init__(self):
        """Compile all patterns"""
        self.compiled_absolute_c1 = [re.compile(p, re.IGNORECASE) for p in self.ABSOLUTE_C1_BLOCKERS]
        self.compiled_force_c1 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C1_PATTERNS]
        self.compiled_force_c2 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C2_PATTERNS]
        self.compiled_force_c3 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C3_PATTERNS]
        self.compiled_force_c4 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C4_PATTERNS]
        self.compiled_force_c5 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C5_PATTERNS]
        self.compiled_force_c6 = [re.compile(p, re.IGNORECASE) for p in self.FORCE_C6_PATTERNS]
        
        self.compiled_block_c5_c6 = [re.compile(p, re.IGNORECASE) for p in self.BLOCK_C5_C6_IF_ASKING_ABOUT]
        self.compiled_block_c6_desc = [re.compile(p, re.IGNORECASE) for p in self.BLOCK_C6_DESCRIPTIVE]
    
    def _has_imperative_verb(self, text):
        """Check if question has imperative verb"""
        imperative_verbs = [
            'hitunglah', 'terapkan', 'gunakan', 'selesaikan', 'buatlah',
            'rancanglah', 'evaluasilah', 'analisislah', 'bandingkan',
            'klasifikasikan', 'susun', 'kembangkan', 'ciptakan',
            'identifikasi', 'nilai', 'tentukan', 'jelaskan', 'uraikan'
        ]
        text_lower = text.lower()
        return any(verb in text_lower for verb in imperative_verbs)
    
    def _is_declarative(self, text):
        """Check if question uses declarative form"""
        text_lower = text.lower().strip()
        
        # Check endings
        endings = ['adalah', 'merupakan', 'ialah', 'yaitu', 'disebut', 'termasuk']
        if any(text_lower.endswith(e) for e in endings):
            return True
        
        # Check patterns
        declarative_patterns = [
            r'\b(?:adalah|merupakan|ialah)\s+[\w\s]+$',
            r'\bdisebut\s+(?:apa|apakah|sebagai)?\s*\??$',
            r'\btermasuk\s+(?:dalam\s+)?kategori',
            r'\.{3,}',  # ellipsis
        ]
        return any(re.search(p, text_lower) for p in declarative_patterns)
    
    def _boost_confidence(self, category, pattern_count):
        """Boost confidence based on pattern strength"""
        base = {'C1': 0.95, 'C2': 0.90, 'C3': 0.87, 'C4': 0.89, 'C5': 0.91, 'C6': 0.93}
        confidence = base.get(category, 0.85)
        if pattern_count >= 2:
            confidence = min(0.97, confidence + 0.02)
        return confidence
    
    def adjust_classification(self, question_text, ml_prediction):
        """V7: Anti-hallucination logic with absolute C1 priority"""
        question_lower = question_text.lower().strip()
        
        ml_level = ml_prediction['category']
        ml_confidence = ml_prediction['confidence']
        
        # ====== STAGE 0: ABSOLUTE C1 BLOCKERS (HIGHEST PRIORITY) ======
        absolute_c1_count = sum(1 for p in self.compiled_absolute_c1 if p.search(question_lower))
        
        if absolute_c1_count >= 1:
            logger.info(f"🔒 ABSOLUTE C1 BLOCK: {ml_level}({ml_confidence:.2f}) → C1(0.96)")
            return self._create_result('C1', 'Remember', 0.96, ml_prediction,
                                      'absolute_c1_blocker', ml_level, ml_confidence)
        
        # ====== STAGE 1: BLOCK FALSE C6 (DESCRIPTIVE SYSTEMS) ======
        if ml_level == 'C6':
            if any(p.search(question_lower) for p in self.compiled_block_c6_desc):
                if self._is_declarative(question_text):
                    logger.info(f"⛔ BLOCK C6→C1: False C6 (descriptive definition)")
                    return self._create_result('C1', 'Remember', 0.94, ml_prediction,
                                              'block_false_c6_descriptive', ml_level, ml_confidence)
        
        # ====== STAGE 2: BLOCK C5/C6 IF ASKING ABOUT CRITERIA/BASIS ======
        if any(p.search(question_lower) for p in self.compiled_block_c5_c6):
            if ml_level in ['C5', 'C6']:
                logger.info(f"⛔ BLOCK C5/C6→C1: Asking about criteria/basis")
                return self._create_result('C1', 'Remember', 0.93, ml_prediction,
                                          'block_c5_c6_criteria', ml_level, ml_confidence)
        
        # ====== STAGE 3: DECLARATIVE ENDING CHECK ======
        if self._is_declarative(question_text):
            if ml_level in ['C3', 'C4', 'C5', 'C6']:
                logger.info(f"⛔ DECLARATIVE→C1: {ml_level} → C1 (declarative form)")
                return self._create_result('C1', 'Remember', 0.94, ml_prediction,
                                          'declarative_downgrade', ml_level, ml_confidence)
        
        # ====== STAGE 4: PATTERN MATCHING (C1 → C6) ======
        
        # C1
        c1_count = sum(1 for p in self.compiled_force_c1 if p.search(question_lower))
        if c1_count >= 1:
            confidence = self._boost_confidence('C1', c1_count)
            if ml_level != 'C1':
                logger.info(f"✓ FORCE C1: {ml_level}({ml_confidence:.2f}) → C1({confidence:.2f})")
            return self._create_result('C1', 'Remember', confidence, ml_prediction,
                                      'force_c1_pattern', ml_level, ml_confidence)
        
        # C2
        c2_count = sum(1 for p in self.compiled_force_c2 if p.search(question_lower))
        if c2_count >= 1:
            if not self._is_declarative(question_text):
                confidence = self._boost_confidence('C2', c2_count)
                if ml_level != 'C2':
                    logger.info(f"✓ FORCE C2: {ml_level}({ml_confidence:.2f}) → C2({confidence:.2f})")
                return self._create_result('C2', 'Understand', confidence, ml_prediction,
                                          'force_c2_pattern', ml_level, ml_confidence)
        
        # C3+ (MUST have imperative)
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
                    confidence = self._boost_confidence(level, count)
                    if ml_level != level:
                        logger.info(f"✓ FORCE {level}: {ml_level}({ml_confidence:.2f}) → {level}({confidence:.2f})")
                    return self._create_result(level, name, confidence, ml_prediction,
                                              f'force_{level.lower()}_pattern', ml_level, ml_confidence)
        
        # ====== STAGE 5: DOWNGRADE UNCERTAIN HIGH LEVELS ======
        if ml_level in ['C3', 'C4', 'C5', 'C6'] and ml_confidence < 0.70:
            if not has_imperative:
                target = 'C1' if self._is_declarative(question_text) else 'C2'
                target_name = 'Remember' if target == 'C1' else 'Understand'
                logger.info(f"⬇️ DOWNGRADE: {ml_level}({ml_confidence:.2f}) → {target}")
                return self._create_result(target, target_name, 0.80, ml_prediction,
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