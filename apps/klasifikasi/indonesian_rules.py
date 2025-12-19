# apps/klasifikasi/indonesian_rules.py - V8: LEGAL/HISTORICAL CONTEXT FIX

import re
import logging

logger = logging.getLogger(__name__)


class IndonesianBloomAdjuster:
    """
    V8: Critical fix for Legal/Historical multiple-choice exams
    
    New issues fixed from Report #105:
    1. "Dikemukakan oleh" (proposed by) → asking WHO, not asking to propose
    2. "Dikembangkan" (developed) in historical context → asking NAME, not create
    3. "Disampaikan kepada" (sent to) → asking WHERE/WHO, not create
    4. "Membuat" in prohibition context → asking what's prohibited, not create
    5. Article citations ("Menurut Pasal X") → recall of article content, not apply
    6. Passive voice verbs describing facts, not student actions
    """
    
    # ========== V8 NEW: PASSIVE VOICE FACT PATTERNS ==========
    # These describe WHAT HAPPENED, not what student must DO
    PASSIVE_FACT_PATTERNS = [
        # "Proposed by" / "Said by" patterns - asking WHO said it
        r'\bdikemukakan\s+oleh\b',
        r'\bdikatakan\s+oleh\b', 
        r'\bdinyatakan\s+oleh\b',
        r'\bdisampaikan\s+oleh\b',
        r'\bdiungkapkan\s+oleh\b',
        r'\bdiperkenalkan\s+oleh\b',
        r'\bdicetuskan\s+oleh\b',
        r'\bdirumuskan\s+oleh\b',
        
        # "Sent to" / "Delivered to" - asking WHERE/TO WHOM
        r'\bdisampaikan\s+kepada\b',
        r'\bdikirimkan\s+kepada\b',
        r'\bdiserahkan\s+kepada\b',
        r'\bdilaporkan\s+kepada\b',
        
        # "Developed into" / "Known as" - asking for NAME
        r'\bdikembangkan\s+menjadi\b',
        r'\bdikenal\s+dengan\s+nama\b',
        r'\bdikenal\s+sebagai\b',
        r'\bdisebut\s+dengan\b',
        r'\bdinamakan\b',
        
        # "Regulated in" / "Stated in" - asking which article/law
        r'\bdiatur\s+dalam\b',
        r'\bdicantumkan\s+dalam\b',
        r'\bditetapkan\s+dalam\b',
        r'\bdimuat\s+dalam\b',
        r'\btercantum\s+dalam\b',
    ]
    
    # ========== V8 NEW: PROHIBITION/RULE CONTEXT ==========
    # Questions about what is PROHIBITED/REQUIRED - these are recall
    PROHIBITION_RULE_PATTERNS = [
        r'\bdilarang\s+(?:untuk\s+)?(?:membuat|melakukan|mencantumkan)',
        r'\btidak\s+(?:boleh|diperbolehkan|diizinkan)\s+(?:untuk\s+)?',
        r'\bharus\s+memenuhi\s+(?:syarat|ketentuan|kriteria)',
        r'\bwajib\s+(?:untuk\s+)?(?:memenuhi|mematuhi)',
        r'\bapabila\s+menyatakan\b',  # "if stating..." in prohibition context
    ]
    
    # ========== V8 NEW: ARTICLE/LAW CITATION PATTERNS ==========
    # "According to Article X" - usually recall, not application
    ARTICLE_CITATION_RECALL = [
        r'\bmenurut\s+pasal\s+\d+',
        r'\bberdasarkan\s+pasal\s+\d+',
        r'\bsesuai\s+(?:dengan\s+)?pasal\s+\d+',
        r'\bsebagaimana\s+(?:diatur|dimaksud)\s+(?:dalam\s+)?pasal',
        r'\bdalam\s+pasal\s+\d+\s+(?:diatur|dinyatakan|disebutkan)',
        r'\bpasal\s+\d+\s+(?:mengatur|menyatakan|menyebutkan)',
        # Asking WHICH article number
        r'\bdiatur\s+dalam\s+pasal\s*$',
        r'\btercantum\s+dalam\s+pasal\s*$',
    ]
    
    # ========== V8 NEW: WHO/WHAT/WHERE QUESTION MARKERS ==========
    # These indicate factual recall, not higher-order thinking
    WHO_WHAT_WHERE_MARKERS = [
        # WHO questions
        r'\boleh\s+siapa\b',
        r'\bsiapa\s+(?:yang|saja)\b',
        r'\b(?:dikemukakan|disampaikan|diperkenalkan)\s+oleh\s*$',
        
        # WHERE questions  
        r'\bkepada\s+siapa\b',
        r'\bdi\s+mana\b',
        r'\bke\s+mana\b',
        r'\bdisampaikan\s+kepada\s*$',
        
        # WHAT questions (naming)
        r'\bdengan\s+nama\s*$',
        r'\bsebagai\s+apa\b',
        r'\bapa\s+(?:nama|istilah|sebutan)nya\b',
    ]
    
    # ========== ULTRA-PRIORITY: C1 DEFINITION BLOCKERS ==========
    ABSOLUTE_C1_BLOCKERS = [
        # "Disebut" patterns - ALWAYS C1
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
        
        # Fill-in-blank/completion
        r'\.{3,}',
        r'\b(?:adalah|merupakan)\s+\.{3,}',
        r'\.{3,}\s+(?:adalah|merupakan)',
        
        # "Termasuk" (includes/belongs to) - ALWAYS C1
        r'\btermasuk\s+(?:dalam\s+)?(?:kategori|jenis|golongan|tipe)',
        r'\bkategori\s+[\w\s]+\s+termasuk',
        
        # System/form definitions
        r'\bsistem\s+(?:informasi\s+)?(?:yang\s+)?(?:dirancang|digunakan|dibuat)\s+[\w\s]+\s+disebut',
        r'\bformulir\s+(?:yang\s+)?(?:digunakan|dibuat)\s+[\w\s]+\s+disebut',
        r'\blaporan\s+(?:yang\s+)?(?:digunakan|dibuat)\s+[\w\s]+\s+disebut',
        
        # "Berisi informasi tentang"
        r'\bberisi\s+informasi\s+(?:tentang|mengenai)',
        r'\bharus\s+berisi\s+informasi',
        
        # Technical terminology identification
        r'\bstruktur\s+[\w\s]+\s+disebut',
        r'\bfungsi\s+[\w\s]+\s+disebut',
        r'\bperangkat\s+[\w\s]+\s+disebut',
        
        # "Tahap/langkah pertama" (sequence recall)
        r'\btahap\s+(?:pertama|awal|terakhir)',
        r'\blangkah\s+(?:pertama|awal|terakhir)',
        r'\bkegiatan\s+(?:pertama|awal)',
        
        # "Yaitu berupa" (namely/that is)
        r'\byaitu\s+berupa',
        r'\byaitu\s+[\w\s]+$',
        r'\bberupa\s+[\w\s]+$',
        
        # V8 NEW: Historical/Legal recall patterns
        r'\bdikemukakan\s+oleh\s*$',
        r'\bdikenal\s+dengan\s+nama\s*$',
        r'\bdisampaikan\s+kepada\s*$',
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
        
        # === "Cara" when asking for definition ===
        r'\bcara\s+[\w\s]+\s+yaitu\s+berupa',
        r'\bcara\s+[\w\s]+\s+adalah',
        r'\bmetode\s+[\w\s]+\s+yaitu',
        
        # === KECUALI (except) questions - ALWAYS C1 ===
        r'\bkecuali\s*[:\.]?\s*$',
        r'\b(?:adalah|berikut)\s+[\w\s,]+,?\s+kecuali',
        r'\bseperti\s+(?:tersebut\s+)?di\s+bawah\s+ini,?\s+kecuali',
        r'\bseperti\s+hal-hal\s+(?:tersebut\s+)?di\s+bawah\s+ini,?\s+kecuali',
        
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
        
        # === System characteristics (not creation) ===
        r'\bsistem\s+yang\s+(?:dapat\s+)?diduga\s+reaksinya',
        r'\bkeputusan\s+(?:yang\s+)?bersifat',
        
        # === Cost/type definitions ===
        r'\bbiaya\s+[\w\s]+\s+(?:yang\s+)?dikeluarkan',
        r'\bjenis\s+(?:biaya|sistem|data|keputusan)',
        
        # === Component listing ===
        r'\bkomponen\s+(?:penentu|utama|dari)',
        r'\bperangkat\s+(?:keras|lunak)\s+(?:yang\s+)?termasuk',
        
        # === V8 NEW: Legal/Historical fact patterns ===
        r'\bpengertian\s+[\w\s]+\s+(?:tersebut\s+)?dikemukakan\s+oleh',
        r'\bteori\s+[\w\s]+\s+dikemukakan\s+oleh',
        r'\btokoh\s+(?:yang\s+)?mendukung',
        r'\btokoh-tokoh\s+(?:yang\s+)?mendukung',
        r'\byang\s+bertindak\s+sebagai',
        r'\byang\s+memiliki\s+fungsi',
        r'\bcontoh\s+[\w\s]+\s+adalah',
        r'\bcontohnya\s+(?:adalah\s+)?seperti',
        r'\bdapat\s+berasal\s+dari',
        r'\bbiasa\s+digunakan\s+oleh',
        r'\bartinya\s+sebagai',
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
        
        # === Purpose/basis ===
        r'\bdasar\s+(?:untuk\s+)?(?:mengukur|opini)',
        r'\bberdasarkan\s+(?:pada|atas)',
        r'\bditurunkan\s+dari',
        
        # === Process understanding (not application) ===
        r'\bproses\s+(?:yang\s+)?(?:bertujuan|dilakukan)',
        r'\baktivitas\s+[\w\s]+\s+(?:yang\s+)?meliputi',
        
        # === V8 NEW: Understanding basis/reasoning ===
        r'\bdidasarkan\s+pada\b',
        r'\batas\s+dasar\b',
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
        r'\bdasar\s+(?:untuk\s+)?opini',
    ]
    
    BLOCK_C6_DESCRIPTIVE = [
        # These describe systems, not ask to create them
        r'\bsistem\s+(?:yang\s+)?(?:menghasilkan|mengintegrasikan|melintasi)',
        r'\bperangkat\s+lunak\s+(?:dasar|sistem)',
        r'\bkumpulan\s+(?:model|data)',
        r'\bsuatu\s+sistem\s+yang\s+mengintegrasikan',
        r'\bentri\s+data,?\s+pemrosesan',
        r'\bcara\s+menyediakan\s+[\w\s]+\s+yaitu',
        
        # V8 NEW: Historical development (not student creation)
        r'\bdikembangkan\s+menjadi',
        r'\bkemudian\s+dikenal\s+dengan',
        r'\bdikenal\s+dengan\s+nama',
    ]
    
    # ========== V8 NEW: BLOCK FALSE C3 (APPLY) ==========
    BLOCK_C3_ARTICLE_RECALL = [
        # Article number questions - recall, not apply
        r'\bmenurut\s+pasal\s+\d+\s+[\w\s]+,\s+[\w\s]+\s+sesuai\s+dengan',
        r'\bsebagaimana\s+diatur\s+dalam\s+pasal',
        r'\bKUH\s*(?:Perdata|Pidana)\s+mengatur',
        r'\bUndang-undang\s+[\w\s]+\s+(?:mengatur|menyatakan)',
        # Asking what law says
        r'\bmenurut\s+[\w\s]+,\s+[\w\s]+\s+dianggap',
        r'\bmenurut\s+[\w\s]+,\s+pengertian',
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
        
        # V8 NEW
        self.compiled_passive_fact = [re.compile(p, re.IGNORECASE) for p in self.PASSIVE_FACT_PATTERNS]
        self.compiled_prohibition = [re.compile(p, re.IGNORECASE) for p in self.PROHIBITION_RULE_PATTERNS]
        self.compiled_article_citation = [re.compile(p, re.IGNORECASE) for p in self.ARTICLE_CITATION_RECALL]
        self.compiled_who_what_where = [re.compile(p, re.IGNORECASE) for p in self.WHO_WHAT_WHERE_MARKERS]
        self.compiled_block_c3 = [re.compile(p, re.IGNORECASE) for p in self.BLOCK_C3_ARTICLE_RECALL]
    
    def _has_imperative_verb(self, text):
        """Check if question has imperative verb directed at student"""
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
            r'\.{3,}',
        ]
        return any(re.search(p, text_lower) for p in declarative_patterns)
    
    def _has_passive_fact_pattern(self, text):
        """V8: Check if question contains passive voice describing facts"""
        return any(p.search(text) for p in self.compiled_passive_fact)
    
    def _has_prohibition_context(self, text):
        """V8: Check if question is about rules/prohibitions"""
        return any(p.search(text) for p in self.compiled_prohibition)
    
    def _has_article_citation(self, text):
        """V8: Check if question cites specific legal article"""
        return any(p.search(text) for p in self.compiled_article_citation)
    
    def _has_who_what_where(self, text):
        """V8: Check if question asks WHO/WHAT/WHERE"""
        return any(p.search(text) for p in self.compiled_who_what_where)
    
    def _is_kecuali_question(self, text):
        """V8: Check if question is 'kecuali' (except) type - always C1"""
        text_lower = text.lower()
        return 'kecuali' in text_lower
    
    def _boost_confidence(self, category, pattern_count):
        """Boost confidence based on pattern strength"""
        base = {'C1': 0.95, 'C2': 0.90, 'C3': 0.87, 'C4': 0.89, 'C5': 0.91, 'C6': 0.93}
        confidence = base.get(category, 0.85)
        if pattern_count >= 2:
            confidence = min(0.97, confidence + 0.02)
        return confidence
    
    def adjust_classification(self, question_text, ml_prediction):
        """V8: Anti-hallucination logic with legal/historical context awareness"""
        question_lower = question_text.lower().strip()
        
        ml_level = ml_prediction['category']
        ml_confidence = ml_prediction['confidence']
        
        # ====== STAGE 0: ABSOLUTE C1 BLOCKERS (HIGHEST PRIORITY) ======
        absolute_c1_count = sum(1 for p in self.compiled_absolute_c1 if p.search(question_lower))
        
        if absolute_c1_count >= 1:
            logger.info(f"🔒 ABSOLUTE C1 BLOCK: {ml_level}({ml_confidence:.2f}) → C1(0.96)")
            return self._create_result('C1', 'Remember', 0.96, ml_prediction,
                                      'absolute_c1_blocker', ml_level, ml_confidence)
        
        # ====== STAGE 0.5: V8 NEW - KECUALI QUESTIONS (ALWAYS C1) ======
        if self._is_kecuali_question(question_text):
            logger.info(f"🔒 KECUALI QUESTION: {ml_level}({ml_confidence:.2f}) → C1(0.97)")
            return self._create_result('C1', 'Remember', 0.97, ml_prediction,
                                      'kecuali_question', ml_level, ml_confidence)
        
        # ====== STAGE 1: V8 NEW - PASSIVE FACT PATTERNS (BLOCK C6/C3) ======
        if self._has_passive_fact_pattern(question_lower):
            if ml_level in ['C6', 'C5', 'C4', 'C3']:
                logger.info(f"⛔ PASSIVE FACT→C1: {ml_level}({ml_confidence:.2f}) → C1")
                return self._create_result('C1', 'Remember', 0.95, ml_prediction,
                                          'passive_fact_to_c1', ml_level, ml_confidence)
        
        # ====== STAGE 1.5: V8 NEW - WHO/WHAT/WHERE QUESTIONS ======
        if self._has_who_what_where(question_lower):
            if ml_level in ['C6', 'C5', 'C4', 'C3']:
                logger.info(f"⛔ WHO/WHAT/WHERE→C1: {ml_level}({ml_confidence:.2f}) → C1")
                return self._create_result('C1', 'Remember', 0.94, ml_prediction,
                                          'who_what_where_to_c1', ml_level, ml_confidence)
        
        # ====== STAGE 2: V8 NEW - PROHIBITION/RULE CONTEXT ======
        if self._has_prohibition_context(question_lower):
            if ml_level in ['C6', 'C5', 'C4', 'C3']:
                # Questions about what is prohibited are recall
                logger.info(f"⛔ PROHIBITION CONTEXT→C1: {ml_level}({ml_confidence:.2f}) → C1")
                return self._create_result('C1', 'Remember', 0.94, ml_prediction,
                                          'prohibition_context_to_c1', ml_level, ml_confidence)
        
        # ====== STAGE 2.5: V8 NEW - ARTICLE CITATION (BLOCK FALSE C3) ======
        if self._has_article_citation(question_lower):
            if ml_level == 'C3':
                # Asking what an article says is recall, not application
                logger.info(f"⛔ ARTICLE CITATION→C1: C3({ml_confidence:.2f}) → C1")
                return self._create_result('C1', 'Remember', 0.94, ml_prediction,
                                          'article_citation_to_c1', ml_level, ml_confidence)
        
        # ====== STAGE 2.6: V8 NEW - BLOCK C3 ARTICLE RECALL ======
        if any(p.search(question_lower) for p in self.compiled_block_c3):
            if ml_level == 'C3':
                logger.info(f"⛔ BLOCK C3→C1: Article recall pattern")
                return self._create_result('C1', 'Remember', 0.93, ml_prediction,
                                          'block_c3_article_recall', ml_level, ml_confidence)
        
        # ====== STAGE 3: BLOCK FALSE C6 (DESCRIPTIVE SYSTEMS) ======
        if ml_level == 'C6':
            if any(p.search(question_lower) for p in self.compiled_block_c6_desc):
                logger.info(f"⛔ BLOCK C6→C1: False C6 (descriptive definition)")
                return self._create_result('C1', 'Remember', 0.94, ml_prediction,
                                          'block_false_c6_descriptive', ml_level, ml_confidence)
        
        # ====== STAGE 4: BLOCK C5/C6 IF ASKING ABOUT CRITERIA/BASIS ======
        if any(p.search(question_lower) for p in self.compiled_block_c5_c6):
            if ml_level in ['C5', 'C6']:
                logger.info(f"⛔ BLOCK C5/C6→C1: Asking about criteria/basis")
                return self._create_result('C1', 'Remember', 0.93, ml_prediction,
                                          'block_c5_c6_criteria', ml_level, ml_confidence)
        
        # ====== STAGE 5: DECLARATIVE ENDING CHECK ======
        if self._is_declarative(question_text):
            if ml_level in ['C3', 'C4', 'C5', 'C6']:
                logger.info(f"⛔ DECLARATIVE→C1: {ml_level} → C1 (declarative form)")
                return self._create_result('C1', 'Remember', 0.94, ml_prediction,
                                          'declarative_downgrade', ml_level, ml_confidence)
        
        # ====== STAGE 6: PATTERN MATCHING (C1 → C6) ======
        
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
        
        # ====== STAGE 7: DOWNGRADE UNCERTAIN HIGH LEVELS ======
        if ml_level in ['C3', 'C4', 'C5', 'C6'] and ml_confidence < 0.70:
            if not has_imperative:
                target = 'C1' if self._is_declarative(question_text) else 'C2'
                target_name = 'Remember' if target == 'C1' else 'Understand'
                logger.info(f"⬇️ DOWNGRADE: {ml_level}({ml_confidence:.2f}) → {target}")
                return self._create_result(target, target_name, 0.80, ml_prediction,
                                          'downgrade_uncertain', ml_level, ml_confidence)
        
        # ====== STAGE 8: V8 NEW - FINAL SAFETY CHECK FOR C6 ======
        # If ML still says C6 but no imperative creative verb, block it
        if ml_level == 'C6' and not has_imperative:
            logger.info(f"⛔ FINAL C6 BLOCK: No imperative verb → C1")
            return self._create_result('C1', 'Remember', 0.88, ml_prediction,
                                      'final_c6_block_no_imperative', ml_level, ml_confidence)
        
        # ====== STAGE 9: KEEP ML PREDICTION ======
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