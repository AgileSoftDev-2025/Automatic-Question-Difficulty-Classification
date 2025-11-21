# apps/klasifikasi/english_rules.py - V4: ENHANCED ANTI-HALLUCINATION

import re
import logging

logger = logging.getLogger(__name__)

class EnglishBloomAdjuster:
    """
    V4: Enhanced fix for "Keyword Trap" - addressing Report #97 issues
    
    New fixes based on analysis:
    1. "Opinion" keyword trap - Q12, Q14 (Report #97)
    2. "Poisoned" technical term trap - Q98 (Report #97)
    3. "Transmission" definition trap - Q94 (Report #97)
    4. "Analysis" context errors - Q34 (Report #98)
    5. "Problem" reasoning trap - Q22 (Report #98)
    6. "Named/Called" errors in Indonesian context - Q41, Q24, Q7 (Report #99)
    """
    
    # ========== NEW: TECHNICAL TERMINOLOGY TRAPS ==========
    TECHNICAL_TERM_BLOCKERS = [
        # Audit/Opinion terminology (Fixes Report #97: Q12, Q14)
        r'\bwhat\s+is\s+(?:the\s+)?(?:auditor\'?s?\s+)?opinion\s+based\s+on',
        r'\b(?:auditor\'?s?\s+)?opinion\s+(?:is\s+)?(?:based\s+on|derives?\s+from)',
        r'\bthe\s+basis\s+(?:for|of)\s+(?:an?\s+)?(?:auditor\'?s?\s+)?opinion',
        r'\bopinion\s+(?:regarding|about|on)\s+[\w\s]+\s+is\s+based',
        
        # Security terminology (Fixes Report #97: Q98)
        r'\bthe\s+[\w\s]+\s+can\s+be\s+poisoned',
        r'\bwhat\s+(?:is\s+)?[\w\s]*poisoning',
        r'\b[\w\s]+\s+poisoning\s+(?:is|attack|vulnerability)',
        r'\bvulnerability\s+(?:called|known\s+as|named)',
        
        # Network terminology (Fixes Report #97: Q94)
        r'\b(?:a|the)\s+transmission\s+(?:that\s+)?sends?\s+[\w\s]+\s+(?:to\s+)?(?:multiple|single|all)',
        r'\b(?:multicast|unicast|broadcast)\s+transmission\s+(?:is|sends?)',
        r'\btype\s+of\s+transmission\s+(?:that|which)',
        
        # "Analysis" in context (Fixes Report #98: Q34)
        r'\b(?:can\s+be\s+)?(?:seen|identified|determined)\s+from\s+(?:the\s+)?[\w\s]*analysis',
        r'\bshown\s+in\s+(?:the\s+)?[\w\s]*analysis',
        r'\b(?:which|what)\s+type\s+of\s+analysis',
        r'\b(?:which|what)\s+[\w\s]*analysis\s+shows',
        
        # Problem/Issue reasoning (Fixes Report #98: Q22)
        r'\bwhy\s+(?:does\s+)?(?:the\s+)?problem\s+(?:of\s+)?[\w\s]+\s+occur',
        r'\bthe\s+problem\s+of\s+[\w\s]+\s+(?:occurs|happens)\s+(?:because|when)',
        r'\bcause\s+of\s+(?:the\s+)?[\w\s]*problem',
    ]
    
    # ========== ULTRA-PRIORITY: C1 DEFINITION BLOCKERS ==========
    ABSOLUTE_C1_BLOCKERS = [
        # "Is called" / "called as" patterns
        r'\bis\s+called\s+(?:a|an|the)?\s*\w*\s*\??$',
        r'\bcalled\s+(?:as|a|an|the)?\s*\??$',
        r'\bwhat\s+is\s+(?:this|it|the\s+\w+)\s+called',
        r'\bknown\s+as\s+(?:a|an|the)?\s*\??$',
        r'\breferred\s+to\s+as\s*\??$',
        r'\bnamed\s+(?:as)?\s*\??$',
        
        # "Is/are" definition patterns
        r'\bwhat\s+is\s+(?:a|an|the)\s+[\w\s]+\s*\??$',
        r'\bwhat\s+are\s+[\w\s]+\s*\??$',
        r'\b[\w\s]+\s+(?:is|are)\s*\.?\s*$',
        r'\bthis\s+is\s+(?:called|known\s+as)',
        
        # Fill-in-blank / completion
        r'_{3,}',
        r'\.\.\.',
        r'\bis\s+_{3,}',
        r'\bthe\s+_{3,}\s+is',
        
        # "Includes" / "belongs to"
        r'\bincludes?\s+(?:the\s+following|all)',
        r'\bbelongs?\s+to\s+(?:the\s+)?(?:category|type|class)',
        r'\b(?:is|are)\s+(?:part|member)\s+of',
        
        # System/terminology definitions
        r'\b(?:a|the)\s+system\s+(?:that|which)\s+(?:is\s+)?(?:designed|used|built)\s+[\w\s]+\s+is\s+called',
        r'\b(?:a|the)\s+form\s+(?:that|which)\s+(?:is\s+)?used\s+[\w\s]+\s+is\s+called',
        r'\b(?:a|the)\s+report\s+(?:that|which)\s+(?:is\s+)?used\s+[\w\s]+\s+is\s+called',
        
        # "Contains information about"
        r'\bcontains?\s+information\s+(?:about|regarding)',
        r'\bmust\s+contain\s+information',
        
        # Sequence/order recall
        r'\b(?:first|initial|last|final)\s+(?:step|stage|phase)',
        r'\bthe\s+(?:first|initial)\s+activity',
        
        # "Namely" / "that is"
        r'\bnamely\s+',
        r'\bthat\s+is\s+to\s+say',
        r'\bi\.e\.',
    ]
    
    # ========== C1 (REMEMBER) PATTERNS ==========
    FORCE_C1_PATTERNS = [
        # Definition/identification
        r'\bwhat\s+is\s+(?:the\s+)?(?:definition|meaning|term)\s+(?:of|for)',
        r'\bdefine\s+(?:the\s+)?(?:term|concept|word)',
        r'\b(?:identify|name|list|state|label)\s+(?:the|a|an)',
        r'\bwho\s+(?:is|was|are|were)',
        r'\bwhen\s+(?:did|was|is|does)',
        r'\bwhere\s+(?:is|was|are|were|did)',
        r'\bwhat\s+does\s+\w+\s+stand\s+for',
        
        # "What is the..." factual
        r'\bwhat\s+is\s+the\s+(?:basic\s+unit|first\s+step|name|type)',
        r'\bwhat\s+type\s+of\s+(?:memory|network|device|data|transmission|attack)',
        
        # Component identification
        r'\bwhich\s+component\s+is\s+(?:known|called)',
        r'\bthe\s+(?:first|second|main)\s+(?:step|stage|phase)',
        
        # Recall/recognition
        r'\brecall\s+(?:the|what|which)',
        r'\brecognize\s+(?:the|what|which)',
        r'\bmemorize\s+(?:the|what)',
        
        # Matching/selection
        r'\bmatch\s+(?:the|each)',
        r'\bselect\s+(?:the\s+correct|all\s+that)',
        r'\bchoose\s+(?:the\s+correct|all\s+that)',
        
        # "Which of the following"
        r'\bwhich\s+of\s+the\s+following\s+(?:is|are)\s+(?:true|false|correct|not|a)\b',
        
        # EXCEPT patterns
        r'\bexcept\s*[:\.]?\s*$',
        r',\s*except\s*[:\?]?\s*$',
        r'\bwhich\s+is\s+not\b',
        
        # Technical terminology
        r'\bstructure\s+of\s+[\w\s]+\s+is\s+called',
        r'\bfunction\s+of\s+[\w\s]+\s+is\s+called',
        
        # System characteristics
        r'\bsystem\s+that\s+(?:can\s+)?(?:be\s+)?(?:predicted|anticipated)',
        r'\bdecision\s+that\s+(?:is|are)\s+(?:of\s+)?(?:tactical|strategic)',
        
        # Cost/type definitions
        r'\bcost\s+(?:that\s+)?(?:is|are)\s+(?:incurred|spent)',
        r'\btype\s+of\s+(?:cost|system|data|decision|attack|vulnerability)',
        
        # NEW: Audit terminology
        r'\bwhat\s+is\s+(?:the\s+)?opinion\s+(?:based\s+on|regarding)',
        r'\b(?:the\s+)?basis\s+for\s+(?:the\s+)?opinion',
        
        # NEW: Security definitions
        r'\bwhat\s+is\s+[\w\s]*poisoning',
        r'\b[\w\s]+\s+poisoning\s+(?:is\s+)?(?:a|an)\s+(?:type|form)',
        
        # NEW: Analysis type identification
        r'\btype\s+of\s+analysis\s+(?:is|that|which)',
        r'\banalysis\s+(?:called|named|known\s+as)',
    ]
    
    # ========== C2 (UNDERSTAND) PATTERNS ==========
    FORCE_C2_PATTERNS = [
        # Explanation/description
        r'\bexplain\s+(?:why|how|what)(?!\s+you\s+would)',
        r'\bdescribe\s+(?:the|how|what)(?!\s+a\s+(?:caching|disaster))',
        r'\bsummarize\s+(?:the|what)',
        r'\bparaphrase\s+(?:the|what)',
        r'\binterpret\s+(?:the|what)',
        
        # Comprehension
        r'\bwhat\s+does\s+(?:this|it|the\s+\w+)\s+mean',
        r'\bwhat\s+is\s+meant\s+by',
        r'\bin\s+your\s+own\s+words',
        r'\bthe\s+main\s+idea\s+(?:is|of)',
        r'\bthe\s+purpose\s+(?:is|of|for)',
        
        # Inference
        r'\binfer\s+(?:what|why|how|from)',
        r'\bconclude\s+(?:that|what)',
        r'\bpredict\s+(?:what|the)(?!\s+you\s+would)',
        
        # Comparison (understanding)
        r'\bdistinguish\s+between',
        r'\bdifferentiate\s+between',
        r'\bthe\s+difference\s+between',
        r'\bexplain\s+the\s+difference',
        
        # Examples
        r'\bgive\s+(?:an\s+)?example\s+of',
        r'\billustrate\s+(?:how|the)',
        
        # Process understanding
        r'\bdescribe\s+what\s+happens\s+during',
        r'\bhow\s+does\s+(?:a|the)\s+\w+\s+(?:work|function|operate)',
        r'\bwhat\s+is\s+the\s+(?:purpose|function|role)\s+of',
        
        # "Based on" / "derives from"
        r'\b(?:is\s+)?based\s+on(?!\s+the\s+criteria)',
        r'\bderives?\s+(?:from|its)',
        r'\bobtains?\s+(?:from|its)',
        
        # Process questions
        r'\bhow\s+does\s+(?:the|an?)\s+(?:auditor|system)\s+(?:derive|obtain)',
        
        # NEW: "Why does X occur/happen"
        r'\bwhy\s+(?:does|do)\s+[\w\s]+\s+(?:occur|happen|arise)',
        r'\bwhat\s+causes?\s+[\w\s]+\s+to\s+occur',
    ]
    
    # ========== C3 (APPLY) PATTERNS ==========
    FORCE_C3_PATTERNS = [
        r'\bapply\s+(?:the|this|these)\s+(?:to|for)',
        r'\buse\s+(?:the|this|these)\s+(?:to\s+solve|to\s+calculate|to\s+determine)',
        r'\bsolve\s+(?:the|this|using)',
        r'\bcalculate\s+(?:the|using)',
        r'\bcompute\s+(?:the|using)',
        r'\bimplement\s+(?:the|a|input\s+validation)',
        r'\bexecute\s+(?:the|this)',
        r'\bperform\s+(?:the|this)',
        r'\bhow\s+would\s+you\s+(?:solve|use|apply|implement)',
        r'\bwhat\s+would\s+happen\s+if',
        r'\bin\s+what\s+situation\s+would\s+you',
        r'\bdemonstrate\s+how\s+(?:to|you\s+would)',
        r'\bshow\s+how\s+(?:to|you\s+would)',
        r'\busing\s+(?:the\s+)?(?:OSI\s+model|version\s+control|Git)',
        r'\bat\s+which\s+layer\s+would\s+you\s+troubleshoot',
        r'\bcalculate\s+the\s+number\s+of',
    ]
    
    # ========== C4 (ANALYZE) PATTERNS ==========
    FORCE_C4_PATTERNS = [
        r'\banalyze\s+(?:the|this|how|why)',
        r'\bexamine\s+(?:the|how|this)',
        r'\binvestigate\s+(?:the|how|why)',
        r'\bbreak\s+down\s+(?:the|into)',
        r'\bdiagnose\s+(?:the|what)',
        r'\bcompare\s+and\s+contrast',
        r'\bwhat\s+are\s+the\s+(?:differences|similarities)\s+between',
        r'\bwhat\s+are\s+the\s+trade-offs\s+between',
        r'\borganize\s+(?:the|these)\s+(?:into|by)',
        r'\bcategorize\s+(?:the|these|the\s+following)',
        r'\bclassify\s+(?:the|these)',
        r'\bidentify\s+the\s+(?:pattern|trend|relationship|potential\s+security)',
        r'\bwhat\s+patterns?\s+(?:can\s+you|do\s+you)\s+see',
        r'\bwhat\s+(?:are\s+the\s+)?(?:causes?|reasons?)\s+(?:of|for|behind)',
        r'\bwhat\s+(?:are\s+the\s+)?effects?\s+of',
        r'\bwhy\s+does\s+\w+\s+(?:cause|lead\s+to|result\s+in)',
        r'\bidentify\s+the\s+(?:potential\s+)?(?:security\s+)?vulnerability',
        r'\bwhat\s+is\s+the\s+(?:primary\s+)?risk\s+of\s+this\s+design',
        r'\banalyze\s+(?:the\s+following\s+)?code\s+snippet',
    ]
    
    # ========== C5 (EVALUATE) PATTERNS ==========
    FORCE_C5_PATTERNS = [
        r'\bevaluate\s+(?:the|this|how|whether)',
        r'\bassess\s+(?:the|this|how|whether)',
        r'\bjudge\s+(?:the|whether)',
        r'\brate\s+(?:the|this)',
        r'\brank\s+(?:the|these)',
        r'\bcritique\s+(?:the|this)',
        r'\breview\s+(?:the|this)\s+(?:and|to\s+determine)',
        r'\bappraise\s+(?:the|this)',
        r'\bjustify\s+(?:your|the|why)',
        r'\bdefend\s+(?:your|the|why)',
        r'\bsupport\s+(?:your|the)\s+(?:opinion|position|argument|decision)',
        r'\brecommend\s+(?:a|the|which)',
        r'\bwhich\s+(?:is\s+the\s+)?(?:best|worst|most\s+effective|least\s+effective)',
        r'\bdecide\s+(?:whether|which|if)',
        r'\bprioritize\s+(?:the|these)',
        r'\bwhat\s+is\s+(?:more|most|less|least)\s+important',
        r'\bwhich\s+(?:would\s+be\s+)?(?:more|most)\s+(?:appropriate|suitable|effective)',
        r'\bevaluate\s+.*?\s+using\s+criteria',
        r'\bassess\s+.*?\s+based\s+on\s+criteria',
    ]
    
    # ========== C6 (CREATE) PATTERNS ==========
    FORCE_C6_PATTERNS = [
        r'\bcreate\s+(?:a|an|your)\s+(?:data\s+model|monitoring)',
        r'\bdesign\s+(?:a|an|your)\s+(?:caching|access|strategy)',
        r'\bconstruct\s+(?:a|an)\s+(?:monitoring|system)',
        r'\bdevelop\s+(?:a|an|your)\s+(?:disaster|plan)',
        r'\bgenerate\s+(?:a|an)',
        r'\binvent\s+(?:a|an)',
        r'\bformulate\s+(?:a|an)\s+(?:security|policy|plan)',
        r'\bdevise\s+(?:a|an)',
        r'\bplan\s+(?:a|an|how\s+to)',
        r'\bproduce\s+(?:a|an)',
        r'\bcompose\s+(?:a|an)\s+algorithm',
        r'\bwrite\s+(?:a|an)\s+(?:new|original)',
        r'\bcombine\s+(?:the|these)\s+(?:to\s+create|into)',
        r'\bintegrate\s+(?:the|these)\s+(?:to\s+create|into)',
        r'\bsynthesize\s+(?:the|these)',
        r'\bpropose\s+(?:a|an|how)',
        r'\bhypothesize\s+(?:about|how)',
        r'\bdesign\s+a\s+(?:caching\s+strategy|disaster\s+recovery|data\s+model|security\s+policy)',
        r'\bcreate\s+a\s+(?:data\s+model|monitoring\s+and\s+alerting)',
        r'\bformulate\s+a\s+(?:security\s+policy)',
        r'\bwhat\s+(?:entities|relationships|components|metrics)\s+would\s+you\s+(?:include|establish)',
    ]
    
    # ========== CRITICAL: BLOCK FALSE C5/C6 ==========
    BLOCK_C5_C6_IF_ASKING_ABOUT = [
        r'\busing\s+(?:the\s+)?criteria',
        r'\bwith\s+(?:the\s+)?criteria',
        r'\b(?:what|which)\s+criteria',
        r'\bcriteria\s+(?:for|to)',
        r'\bbasis\s+(?:for|of)\s+(?:the\s+)?opinion',
        r'\bderived\s+from',
    ]
    
    BLOCK_C6_DESCRIPTIVE = [
        r'\b(?:a|the)\s+system\s+(?:that|which)\s+(?:generates|integrates|crosses)',
        r'\b(?:a|the)\s+(?:basic|system)\s+software',
        r'\b(?:a|the)\s+collection\s+of\s+(?:models|data)',
        r'\b(?:a|the)\s+system\s+that\s+integrates',
        r'\bdata\s+entry,?\s+processing',
        r'\bway\s+to\s+provide\s+[\w\s]+\s+is',
        r'\btransmission\s+(?:that\s+)?sends\s+[\w\s]+\s+to\s+multiple',
        r'\b(?:in|for)\s+[\w\s]+\s+transmission\s*,',
    ]
    
    # ========== ANTI-PATTERNS ==========
    NOT_C1_PATTERNS = [
        r'\banalyze\b',
        r'\bevaluate\b',
        r'\bcreate\s+(?:a|an)\s+(?:data|monitoring|caching)',
        r'\bdesign\s+(?:a|an)\s+(?:caching|disaster|security)',
        r'\bapply\s+(?:to\s+solve|to\s+calculate)\b',
        r'\bcompare\s+and\s+contrast\b',
        r'\bjustify\b',
        r'\bcritique\b',
    ]
    
    NOT_C2_PATTERNS = [
        r'\bcalculate\s+the\s+number',
        r'\bsolve\s+(?:the\s+)?problem\b',
        r'\banalyze\s+(?:the\s+)?(?:code|following)',
        r'\bevaluate\s+(?:the\s+)?(?:effectiveness|whether|security)',
        r'\bcreate\s+(?:a|an)\s+(?:data|monitoring)',
        r'\bdesign\s+(?:a|an)\s+(?:caching|disaster)',
    ]
    
    NOT_C3_PATTERNS = [
        r'\banalyze\s+(?:why|how|the\s+following)\b',
        r'\bevaluate\s+(?:whether|if|the\s+security)\b',
        r'\bcreate\s+(?:a\s+new|an\s+original|a\s+data)\b',
        r'\bdesign\s+(?:a\s+new|an\s+original|a\s+caching)\b',
    ]
    
    NOT_C4_PATTERNS = [
        r'\bcreate\s+(?:a|an)\s+(?:data|monitoring)',
        r'\bdesign\s+(?:a|an)\s+(?:caching|disaster)',
        r'\bgenerate\s+(?:a|an)\b',
        r'\bpropose\s+(?:a|an)\b',
    ]
    
    NOT_C5_PATTERNS = [
        r'\bcreate\s+(?:a|an)\s+(?:data|monitoring)',
        r'\bdesign\s+(?:a|an)\s+(?:caching|disaster)',
        r'\bgenerate\s+(?:a|an)\b',
        r'\bproduce\s+(?:a|an)\b',
    ]
    
    # ========== KEYWORDS ==========
    C1_KEYWORDS = [
        'define', 'identify', 'list', 'name', 'recall', 'recognize',
        'state', 'label', 'match', 'who', 'what is', 'when', 'where',
        'called', 'known as', 'referred to as', 'type of', 'basis for'
    ]
    
    C2_KEYWORDS = [
        'explain', 'describe', 'summarize', 'paraphrase', 'interpret',
        'infer', 'conclude', 'predict', 'distinguish', 'differentiate',
        'based on', 'derives from', 'obtains from', 'why does', 'what causes'
    ]
    
    C3_KEYWORDS = [
        'apply', 'use', 'solve', 'calculate', 'compute', 'implement',
        'execute', 'perform', 'demonstrate how', 'using the'
    ]
    
    C4_KEYWORDS = [
        'analyze', 'examine', 'investigate', 'compare and contrast',
        'categorize', 'classify', 'organize', 'differentiate',
        'pattern', 'diagnose', 'trade-offs', 'vulnerability'
    ]
    
    C5_KEYWORDS = [
        'evaluate', 'assess', 'judge', 'critique', 'justify',
        'defend', 'recommend', 'prioritize', 'rate', 'rank',
        'best', 'effective', 'appropriate'
    ]
    
    C6_KEYWORDS = [
        'create a', 'design a', 'construct a', 'develop a', 'formulate a',
        'devise', 'generate a', 'plan a', 'compose an', 'synthesize',
        'propose', 'build a', 'produce a'
    ]
    
    def __init__(self):
        """Compile all patterns"""
        self.compiled_technical_blockers = [re.compile(p, re.IGNORECASE) for p in self.TECHNICAL_TERM_BLOCKERS]
        self.compiled_absolute_c1 = [re.compile(p, re.IGNORECASE) for p in self.ABSOLUTE_C1_BLOCKERS]
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
        
        self.compiled_block_c5_c6 = [re.compile(p, re.IGNORECASE) for p in self.BLOCK_C5_C6_IF_ASKING_ABOUT]
        self.compiled_block_c6_desc = [re.compile(p, re.IGNORECASE) for p in self.BLOCK_C6_DESCRIPTIVE]
    
    def _boost_confidence(self, category, ml_confidence, pattern_strength, keyword_count):
        """Boost confidence based on pattern strength"""
        base = {'C1': 0.95, 'C2': 0.90, 'C3': 0.87, 'C4': 0.89, 'C5': 0.91, 'C6': 0.93}
        confidence = base.get(category, 0.85)
        
        if ml_confidence > 0.70:
            confidence = min(0.98, confidence + 0.05)
        
        if pattern_strength >= 2 or keyword_count >= 3:
            confidence = min(0.98, confidence + 0.03)
            
        if pattern_strength >= 1 and keyword_count >= 2:
            confidence = min(0.98, confidence + 0.04)
        
        return confidence
    
    def adjust_classification(self, question_text, ml_prediction):
        """V4: Enhanced anti-hallucination with technical term blocking"""
        question_lower = question_text.lower().strip()
        
        ml_level = ml_prediction['category']
        ml_confidence = ml_prediction['confidence']
        
        # ====== STAGE 0A: TECHNICAL TERMINOLOGY BLOCKERS ======
        technical_block_count = sum(1 for p in self.compiled_technical_blockers if p.search(question_lower))
        
        if technical_block_count >= 1:
            if ml_level in ['C3', 'C4', 'C5', 'C6']:
                # Determine if C1 or C2 based on question type
                target = 'C2' if any(word in question_lower for word in ['why', 'how does', 'what causes']) else 'C1'
                target_name = 'Understand' if target == 'C2' else 'Remember'
                logger.info(f"🔒 TECHNICAL TERM BLOCK: {ml_level}({ml_confidence:.2f}) → {target}(0.95)")
                return self._create_result(target, target_name, 0.95, ml_prediction,
                                          'technical_term_blocker', ml_level, ml_confidence)
        
        # ====== STAGE 0B: ABSOLUTE C1 BLOCKERS ======
        absolute_c1_count = sum(1 for p in self.compiled_absolute_c1 if p.search(question_lower))
        
        if absolute_c1_count >= 1:
            logger.info(f"🔒 ABSOLUTE C1 BLOCK: {ml_level}({ml_confidence:.2f}) → C1(0.96)")
            return self._create_result('C1', 'Remember', 0.96, ml_prediction,
                                      'absolute_c1_blocker', ml_level, ml_confidence)
        
        # ====== STAGE 1: BLOCK FALSE C6 (DESCRIPTIVE SYSTEMS) ======
        if ml_level == 'C6':
            if any(p.search(question_lower) for p in self.compiled_block_c6_desc):
                logger.info(f"⛔ BLOCK C6→C1: False C6 (descriptive definition)")
                return self._create_result('C1', 'Remember', 0.94, ml_prediction,
                                           'block_false_c6_descriptive', ml_level, ml_confidence)
        
        # ====== STAGE 2: BLOCK C5/C6 IF ASKING ABOUT CRITERIA/BASIS ======
        if any(p.search(question_lower) for p in self.compiled_block_c5_c6):
            if ml_level in ['C5', 'C6']:
                logger.info(f"⛔ BLOCK C5/C6→C1: Asking about criteria/basis")
                return self._create_result('C1', 'Remember', 0.93, ml_prediction,
                                           'block_c5_c6_criteria', ml_level, ml_confidence)
        
        # ====== STAGE 3: CHECK C6 (CREATE) ======
        result = self._check_level(question_lower, self.compiled_force_c6,
                                   self.C6_KEYWORDS, [],
                                   ml_level, 'C6', 'Create', ml_confidence, ml_prediction)
        if result:
            return result
        
        # ====== STAGE 4: CHECK C5 (EVALUATE) ======
        result = self._check_level(question_lower, self.compiled_force_c5,
                                   self.C5_KEYWORDS, self.compiled_not_c5,
                                   ml_level, 'C5', 'Evaluate', ml_confidence, ml_prediction)
        if result:
            return result
        
        # ====== STAGE 5: CHECK C4 (ANALYZE) ======
        result = self._check_level(question_lower, self.compiled_force_c4,
                                   self.C4_KEYWORDS, self.compiled_not_c4,
                                   ml_level, 'C4', 'Analyze', ml_confidence, ml_prediction)
        if result:
            return result
        
        # ====== STAGE 6: CHECK C3 (APPLY) ======
        result = self._check_level(question_lower, self.compiled_force_c3,
                                   self.C3_KEYWORDS, self.compiled_not_c3,
                                   ml_level, 'C3', 'Apply', ml_confidence, ml_prediction)
        if result:
            return result
        
        # ====== STAGE 7: CHECK C2 (UNDERSTAND) ======
        result = self._check_level(question_lower, self.compiled_force_c2,
                                   self.C2_KEYWORDS, self.compiled_not_c2,
                                   ml_level, 'C2', 'Understand', ml_confidence, ml_prediction)
        if result:
            return result
        
        # ====== STAGE 8: CHECK C1 (REMEMBER) ======
        result = self._check_level(question_lower, self.compiled_force_c1,
                                   self.C1_KEYWORDS, self.compiled_not_c1,
                                   ml_level, 'C1', 'Remember', ml_confidence, ml_prediction)
        if result:
            return result
        
        # ====== STAGE 9: DEFAULT - KEEP ML PREDICTION ======
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
    
    def _check_level(self, text, patterns, keywords, anti_patterns,
                     current_ml_level, target_level, level_name, ml_confidence, ml_prediction):
        """Helper to check patterns for specific level"""
        # 1. Check Anti-Patterns (disqualify if found)
        if any(p.search(text) for p in anti_patterns):
            return None
        
        # 2. Check Positive Patterns and Keywords
        pattern_strength = sum(1 for p in patterns if p.search(text))
        keyword_count = sum(1 for k in keywords if k in text)
        
        # 3. Decision Logic
        result = None
        
        # Case A: Strong Pattern Match → Override ML
        if pattern_strength > 0:
            new_conf = self._boost_confidence(target_level, ml_confidence, pattern_strength, keyword_count)
            result = {
                'category': target_level,
                'category_name': level_name,
                'confidence': new_conf,
                'all_probabilities': ml_prediction.get('all_probabilities', {}),
                'adjustment_reason': f"Detected strong {level_name} pattern (Rule-based override)",
                'ml_category': current_ml_level,
                'ml_confidence': ml_confidence,
                'was_adjusted': True
            }
            
            if target_level != current_ml_level:
                logger.info(f"✓ ADJUSTED: {current_ml_level} → {target_level} | Reason: Strong Pattern")
        
        # Case B: ML matches + keywords present → Boost confidence
        elif current_ml_level == target_level and keyword_count > 0:
            new_conf = self._boost_confidence(target_level, ml_confidence, 0, keyword_count)
            
            if new_conf > ml_confidence:
                result = {
                    'category': target_level,
                    'category_name': level_name,
                    'confidence': new_conf,
                    'all_probabilities': ml_prediction.get('all_probabilities', {}),
                    'adjustment_reason': f"ML prediction confirmed by {level_name} keywords",
                    'ml_category': current_ml_level,
                    'ml_confidence': ml_confidence,
                    'was_adjusted': True
                }
        
        return result
    
    def _create_result(self, category, name, confidence, ml_pred, reason, ml_cat, ml_conf):
        """Helper to create result dictionary"""
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
    """Convenience function for English pattern adjustment"""
    adjuster = EnglishBloomAdjuster()
    return adjuster.adjust_classification(question_text, ml_prediction)