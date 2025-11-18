# apps/klasifikasi/english_rules.py 


import re
import logging

logger = logging.getLogger(__name__)


class EnglishBloomAdjuster:
    """
    AGGRESSIVE adjuster for English questions
    Recognizes patterns across all Bloom's levels (C1-C6)
    WITH CONFIDENCE BOOSTING
    """
    
    # ========== C1 (REMEMBER) PATTERNS ==========
    FORCE_C1_PATTERNS = [
        # Definition/identification questions
        r'\bwhat\s+is\s+(?:the\s+)?(?:definition|meaning|term)\s+(?:of|for)',
        r'\bdefine\s+(?:the\s+)?(?:term|concept|word)',
        r'\b(?:identify|name|list|state|label)\s+(?:the|a|an)',
        r'\bwho\s+(?:is|was|are|were)',
        r'\bwhen\s+(?:did|was|is|does)',
        r'\bwhere\s+(?:is|was|are|were|did)',
        r'\bwhich\s+of\s+the\s+following\s+is\s+(?:the\s+)?(?:definition|meaning)',
        r'\bwhat\s+does\s+\w+\s+stand\s+for',
        
        # Recall/recognition questions
        r'\brecall\s+(?:the|what|which)',
        r'\brecognize\s+(?:the|what|which)',
        r'\bmemorize\s+(?:the|what)',
        r'\brepeat\s+(?:the|what)',
        r'\breproduce\s+(?:the|what)',
        
        # Fill-in-the-blank/completion
        r'\bcomplete\s+the\s+(?:following|sentence|statement)',
        r'\bfill\s+in\s+the\s+blank',
        r'\bthe\s+term\s+for\s+this\s+is',
        r'\bthis\s+is\s+called',
        r'\bthis\s+is\s+known\s+as',
        r'\b(?:is|are)\s+called\s+what',
        
        # Matching/selection
        r'\bmatch\s+(?:the|each)',
        r'\bselect\s+(?:the\s+correct|all\s+that)',
        r'\bchoose\s+(?:the\s+correct|all\s+that)',
        
        # Factual recall
        r'\baccording\s+to\s+the\s+(?:text|passage|article)',
        r'\bas\s+stated\s+in',
        r'\bthe\s+(?:first|second|third|main|primary)\s+(?:step|stage|phase)\s+(?:is|in)',
        r'\b(?:how\s+many|what\s+type\s+of|what\s+kind\s+of)',
        r'\bwhich\s+(?:component|part)\s+is\s+(?:known|called)',
        r'\bthe\s+basic\s+unit\s+of',
    ]
    
    # ========== C2 (UNDERSTAND) PATTERNS ==========
    FORCE_C2_PATTERNS = [
        # Explanation/description
        r'\bexplain\s+(?:why|how|what|the)',
        r'\bdescribe\s+(?:the|how|what)',
        r'\bsummarize\s+(?:the|what)',
        r'\bparaphrase\s+(?:the|what)',
        r'\binterpret\s+(?:the|what)',
        
        # Comprehension
        r'\bwhat\s+does\s+(?:this|it|the\s+\w+)\s+mean',
        r'\bwhat\s+is\s+meant\s+by',
        r'\bwhat\s+does\s+it\s+mean\s+when',
        r'\bin\s+your\s+own\s+words',
        r'\bthe\s+main\s+idea\s+(?:is|of)',
        r'\bthe\s+purpose\s+(?:is|of|for)',
        r'\bwhy\s+is\s+\w+\s+important',
        
        # Inference/conclusion
        r'\binfer\s+(?:what|why|how|from)',
        r'\bconclude\s+(?:that|what)',
        r'\bpredict\s+(?:what|the)',
        r'\bestimate\s+(?:what|the)',
        r'\bimply\s+(?:that|what)',
        
        # Comparison (understanding level)
        r'\bcompare\s+(?:the|these)(?!\s+and\s+contrast)',
        r'\bcontrast\s+(?:the|these)(?!\s+and)',
        r'\bdistinguish\s+between',
        r'\bdifferentiate\s+between',
        r'\bthe\s+difference\s+between',
        
        # Relationships
        r'\bwhat\s+is\s+the\s+relationship\s+between',
        r'\bhow\s+(?:does|do|is|are)\s+\w+\s+(?:related\s+to|connected\s+to)',
        r'\bthe\s+connection\s+between',
        
        # Examples/illustration
        r'\bgive\s+(?:an\s+)?example\s+of',
        r'\billustrate\s+(?:how|the)',
        r'\bdemonstrate\s+(?:what\s+you\s+understand|your\s+understanding)',
    ]
    
    # ========== C3 (APPLY) PATTERNS ==========
    FORCE_C3_PATTERNS = [
        # Application/use
        r'\bapply\s+(?:the|this|these)',
        r'\buse\s+(?:the|this|these)\s+(?:to\s+solve|to\s+calculate|to\s+determine)',
        r'\bsolve\s+(?:the|this|using)',
        r'\bcalculate\s+(?:the|using)',
        r'\bcompute\s+(?:the|using)',
        
        # Implementation
        r'\bimplement\s+(?:the|a)',
        r'\bexecute\s+(?:the|this)',
        r'\bcarry\s+out\s+(?:the|this)',
        r'\bperform\s+(?:the|this)',
        
        # Problem-solving
        r'\bhow\s+would\s+you\s+(?:solve|use|apply)',
        r'\bwhat\s+would\s+happen\s+if',
        r'\bin\s+what\s+situation\s+would\s+you',
        r'\bunder\s+what\s+circumstances',
        r'\bgiven\s+(?:an\s+array|a\s+\w+),\s+apply',
        
        # Practice/demonstration
        r'\bdemonstrate\s+how\s+(?:to|you\s+would)',
        r'\bshow\s+how\s+(?:to|you\s+would)',
        r'\bpractice\s+(?:by|using)',
        
        # Modification/adaptation
        r'\bmodify\s+(?:the|this)\s+(?:to|for)',
        r'\badapt\s+(?:the|this)\s+(?:to|for)',
        r'\badjust\s+(?:the|this)',
        
        # Using tools/methods
        r'\busing\s+(?:the\s+)?(?:OSI\s+model|version\s+control|Git)',
        r'\bat\s+which\s+layer\s+would\s+you',
    ]
    
    # ========== C4 (ANALYZE) PATTERNS ==========
    FORCE_C4_PATTERNS = [
        # Analysis/breakdown
        r'\banalyze\s+(?:the|this|how|why)',
        r'\bexamine\s+(?:the|how|this)',
        r'\binvestigate\s+(?:the|how|why)',
        r'\bbreak\s+down\s+(?:the|into)',
        r'\bdiagnose\s+(?:the|what)',
        
        # Comparison (analytical)
        r'\bcompare\s+and\s+contrast',
        r'\bwhat\s+are\s+the\s+(?:differences|similarities)\s+between',
        r'\bhow\s+(?:does|do)\s+\w+\s+differ\s+from',
        r'\bwhat\s+are\s+the\s+trade-offs\s+between',
        
        # Organization/structure
        r'\borganize\s+(?:the|these)\s+(?:into|by)',
        r'\bcategorize\s+(?:the|these)',
        r'\bclassify\s+(?:the|these)',
        r'\bstructure\s+(?:the|this)',
        
        # Relationships/patterns
        r'\bwhat\s+is\s+the\s+function\s+of',
        r'\bidentify\s+the\s+(?:pattern|trend|relationship)',
        r'\bwhat\s+patterns?\s+(?:can\s+you|do\s+you)\s+see',
        
        # Cause/effect
        r'\bwhat\s+(?:are\s+the\s+)?(?:causes?|reasons?)\s+(?:of|for|behind)',
        r'\bwhat\s+(?:are\s+the\s+)?effects?\s+of',
        r'\bwhy\s+does\s+\w+\s+(?:cause|lead\s+to|result\s+in)',
        r'\banalyze\s+why\s+(?:a|the)',
        
        # Components/elements
        r'\bwhat\s+are\s+the\s+(?:parts|components|elements)\s+of',
        r'\bidentify\s+the\s+(?:key|main|essential)\s+(?:factors|components)',
        r'\bbreak\s+down\s+the\s+components',
        
        # Security/vulnerability
        r'\bidentify\s+the\s+(?:potential\s+)?(?:security\s+)?vulnerability',
        r'\bwhat\s+is\s+the\s+(?:primary\s+)?risk\s+of',
    ]
    
    # ========== C5 (EVALUATE) PATTERNS ==========
    FORCE_C5_PATTERNS = [
        # Evaluation/judgment
        r'\bevaluate\s+(?:the|this|how|whether)',
        r'\bassess\s+(?:the|this|how|whether)',
        r'\bjudge\s+(?:the|whether)',
        r'\brate\s+(?:the|this)',
        r'\brank\s+(?:the|these)',
        
        # Critique/review
        r'\bcritique\s+(?:the|this)',
        r'\breview\s+(?:the|this)\s+(?:and|to\s+determine)',
        r'\bappraise\s+(?:the|this)',
        
        # Justification/defense
        r'\bjustify\s+(?:your|the|why)',
        r'\bdefend\s+(?:your|the|why)',
        r'\bsupport\s+(?:your|the)\s+(?:opinion|position|argument|decision)',
        r'\bwhy\s+(?:do\s+you\s+think|is)\s+\w+\s+(?:better|worse|more|less)',
        
        # Recommendations/decisions
        r'\brecommend\s+(?:a|the|which)',
        r'\bwhich\s+(?:is\s+the\s+)?(?:best|worst|most\s+effective|least\s+effective)',
        r'\bwhat\s+is\s+the\s+(?:best|worst|most|least)',
        r'\bdecide\s+(?:whether|which|if)',
        
        # Value/priority
        r'\bprioritize\s+(?:the|these)',
        r'\bwhat\s+is\s+(?:more|most|less|least)\s+important',
        r'\bwhich\s+(?:would\s+be\s+)?(?:more|most)\s+(?:appropriate|suitable|effective)',
        r'\bis\s+this\s+(?:appropriate|suitable)',
        
        # Criteria/standards
        r'\bbased\s+on\s+(?:the\s+)?criteria',
        r'\baccording\s+to\s+(?:the\s+)?standards?',
        r'\bto\s+what\s+extent',
        r'\bhow\s+well\s+does',
        
        # Evaluation questions
        r'\bevaluate\s+whether\s+\w+\s+is\s+appropriate',
        r'\bassess\s+the\s+trade-offs',
        r'\bjudge\s+the\s+effectiveness',
    ]
    
    # ========== C6 (CREATE) PATTERNS ==========
    FORCE_C6_PATTERNS = [
        # Creation/construction
        r'\bcreate\s+(?:a|an|your)',
        r'\bdesign\s+(?:a|an|your)',
        r'\bconstruct\s+(?:a|an)',
        r'\bdevelop\s+(?:a|an|your)',
        r'\bgenerate\s+(?:a|an)',
        
        # Invention/formulation
        r'\binvent\s+(?:a|an)',
        r'\bformulate\s+(?:a|an)',
        r'\bdevise\s+(?:a|an)',
        r'\boriginate\s+(?:a|an)',
        
        # Planning/production
        r'\bplan\s+(?:a|an|how\s+to)',
        r'\bproduce\s+(?:a|an)',
        r'\bcompose\s+(?:a|an)',
        r'\bwrite\s+(?:a|an)\s+(?:new|original)',
        
        # Combination/integration
        r'\bcombine\s+(?:the|these)\s+(?:to\s+create|into)',
        r'\bintegrate\s+(?:the|these)\s+(?:to\s+create|into)',
        r'\bsynthesize\s+(?:the|these)',
        r'\bcompile\s+(?:a|an)',
        
        # Proposal/hypothesis
        r'\bpropose\s+(?:a|an|how)',
        r'\bhypothesize\s+(?:about|how)',
        r'\bspeculate\s+(?:about|on)',
        r'\bimagine\s+(?:a|an|how)',
        
        # Alternative solutions
        r'\bwhat\s+(?:alternative|other)\s+(?:ways|methods|solutions)',
        r'\bhow\s+else\s+(?:could|can|might)',
        r'\bwhat\s+if\s+we\s+(?:changed|modified|created)',
        
        # Specific design/create tasks
        r'\bdesign\s+a\s+(?:caching\s+strategy|disaster\s+recovery\s+plan|data\s+model)',
        r'\bcreate\s+a\s+(?:data\s+model|monitoring\s+system|security\s+policy)',
        r'\bcompose\s+an\s+algorithm',
        r'\bconstruct\s+a\s+(?:monitoring|system)',
    ]
    
    # ========== ANTI-PATTERNS ==========
    
    NOT_C1_PATTERNS = [
        r'\banalyze\b',
        r'\bevaluate\b',
        r'\bcreate\s+(?:a|an)\b',
        r'\bdesign\s+(?:a|an)\b',
        r'\bapply\s+(?:to\s+solve|to\s+calculate)\b',
        r'\bcompare\s+and\s+contrast\b',
        r'\bjustify\b',
        r'\bcritique\b',
        r'\bcalculate\b',
    ]
    
    NOT_C2_PATTERNS = [
        r'\bcalculate\b',
        r'\bsolve\s+(?:the\s+)?problem\b',
        r'\banalyze\s+(?:the\s+)?(?:data|results)\b',
        r'\bevaluate\s+(?:the\s+)?(?:effectiveness|quality)\b',
        r'\bcreate\s+(?:a|an)\b',
        r'\bdesign\s+(?:a|an)\b',
        r'\bapply\s+the\b',
    ]
    
    NOT_C3_PATTERNS = [
        r'\banalyze\s+(?:why|how)\b',
        r'\bevaluate\s+(?:whether|if)\b',
        r'\bcreate\s+(?:a\s+new|an\s+original)\b',
        r'\bdesign\s+(?:a\s+new|an\s+original)\b',
        r'\bjustify\s+your\b',
        r'\bcompare\s+and\s+contrast\b',
    ]
    
    NOT_C4_PATTERNS = [
        r'\bcreate\s+(?:a|an)\b',
        r'\bdesign\s+(?:a|an)\b',
        r'\bgenerate\s+(?:a|an)\b',
        r'\bpropose\s+(?:a|an)\b',
        r'\bevaluate\s+whether\b',
        r'\bjustify\b',
    ]
    
    NOT_C5_PATTERNS = [
        r'\bcreate\s+(?:a|an)\b',
        r'\bdesign\s+(?:a|an)\b',
        r'\bgenerate\s+(?:a|an)\b',
        r'\bproduce\s+(?:a|an)\b',
        r'\bcompose\s+(?:a|an)\b',
        r'\bdevelop\s+(?:a|an)\b',
    ]
    
    NOT_C6_PATTERNS = []
    
    # ========== KEYWORDS ==========
    
    C1_KEYWORDS = [
        'define', 'identify', 'list', 'name', 'recall', 'recognize',
        'state', 'label', 'match', 'who', 'what', 'when', 'where',
        'memorize', 'repeat', 'reproduce', 'stand for', 'called',
        'known as', 'basic unit'
    ]
    
    C2_KEYWORDS = [
        'explain', 'describe', 'summarize', 'paraphrase', 'interpret',
        'infer', 'conclude', 'predict', 'estimate', 'distinguish',
        'differentiate', 'compare', 'contrast', 'illustrate', 'mean',
        'relationship', 'difference between'
    ]
    
    C3_KEYWORDS = [
        'apply', 'use', 'solve', 'calculate', 'compute', 'implement',
        'execute', 'carry out', 'perform', 'demonstrate', 'practice',
        'modify', 'adapt', 'given', 'using'
    ]
    
    C4_KEYWORDS = [
        'analyze', 'examine', 'investigate', 'compare and contrast',
        'categorize', 'classify', 'organize', 'differentiate',
        'distinguish', 'relate', 'function', 'pattern', 'diagnose',
        'break down', 'trade-offs', 'risk', 'vulnerability'
    ]
    
    C5_KEYWORDS = [
        'evaluate', 'assess', 'judge', 'critique', 'justify',
        'defend', 'recommend', 'prioritize', 'rate', 'rank',
        'appraise', 'value', 'appropriate', 'effective', 'best',
        'support your'
    ]
    
    C6_KEYWORDS = [
        'create', 'design', 'construct', 'develop', 'formulate',
        'devise', 'generate', 'plan', 'compose', 'synthesize',
        'propose', 'hypothesize', 'invent', 'build', 'produce'
    ]
    
    def __init__(self):
        """Compile all regex patterns for efficiency"""
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
            'C1': 0.92,
            'C2': 0.90,
            'C3': 0.87,
            'C4': 0.89,
            'C5': 0.91,
            'C6': 0.93,
        }
        
        confidence = base_confidence.get(category, 0.85)
        
        # Boost if ML also agrees (similar level)
        ml_level = ml_confidence if ml_confidence > 0 else 0.5
        
        # If ML confidence is high and agrees
        if ml_confidence > 0.70:
            confidence = min(0.98, confidence + 0.05)
        
        # If multiple strong signals
        if pattern_strength >= 2 or keyword_count >= 3:
            confidence = min(0.98, confidence + 0.03)
        
        # If both pattern AND keywords match
        if pattern_strength >= 1 and keyword_count >= 2:
            confidence = min(0.98, confidence + 0.04)
        
        return confidence
    
    def adjust_classification(self, question_text, ml_prediction):
        """
        AGGRESSIVE pattern-based adjustment with confidence boosting
        
        Priority:
        1. Check C6 patterns (highest level) first
        2. Check C5, C4, C3, C2, C1 in descending order
        3. Each level checked only if no anti-patterns exist
        4. Boost confidence when patterns are strong
        5. Keep ML prediction if no strong patterns found
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
        
        # === CONFIDENCE-BASED ADJUSTMENT ===
        if ml_confidence < 0.65 and ml_level in ['C5', 'C6']:
            logger.info(
                f"DOWNGRADED: {ml_level}({ml_confidence:.2f}) -> C4 (low confidence) | "
                f"Q: {question_text[:70]}..."
            )
            return self._create_result('C4', 'Analyze', 0.70, ml_prediction,
                                      'downgrade_uncertain', ml_level, ml_confidence)
        
        # === KEEP ML PREDICTION ===
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
            
            return self._create_result(
                target_level,
                level_name,
                confidence,
                {'all_probabilities': {}},
                f'force_{target_level.lower()}_pattern',
                ml_level,
                ml_confidence
            )
        
        return None
    
    def _create_result(self, category, category_name, confidence, 
                       ml_prediction, reason, ml_category, ml_confidence):
        """Create adjusted result dictionary"""
        was_adjusted = (category != ml_category or 
                       abs(confidence - ml_confidence) > 0.05)
        
        return {
            'category': category,
            'category_name': category_name,
            'confidence': confidence,
            'all_probabilities': ml_prediction.get('all_probabilities', {}),
            'adjustment_reason': reason,
            'ml_category': ml_category,
            'ml_confidence': ml_confidence,
            'was_adjusted': was_adjusted
        }


def adjust_classification_with_patterns(question_text, ml_prediction):
    """Convenience function for English pattern adjustment"""
    adjuster = EnglishBloomAdjuster()
    return adjuster.adjust_classification(question_text, ml_prediction)