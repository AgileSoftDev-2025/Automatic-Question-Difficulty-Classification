# apps/klasifikasi/english_rules.py - BLOOM'S TAXONOMY PATTERN ENFORCEMENT

"""
AGGRESSIVE English pattern recognition for Bloom's Taxonomy
Rule: Pattern-based adjustment to improve ML classification accuracy
Focus: Recognize common question patterns across all 6 cognitive levels
"""

import re
import logging

logger = logging.getLogger(__name__)


class EnglishBloomAdjuster:
    """
    AGGRESSIVE adjuster for English questions
    Recognizes patterns across all Bloom's levels (C1-C6)
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
        
        # Matching/selection
        r'\bmatch\s+(?:the|each)',
        r'\bselect\s+(?:the\s+correct|all)',
        r'\bchoose\s+(?:the\s+correct|all)',
        
        # Factual recall
        r'\baccording\s+to\s+the\s+(?:text|passage|article)',
        r'\bas\s+stated\s+in',
        r'\bthe\s+(?:first|second|third|main|primary)\s+(?:step|stage|phase)\s+is',
        r'\b(?:how\s+many|what\s+type\s+of|what\s+kind\s+of)\s+',
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
        r'\bin\s+your\s+own\s+words',
        r'\bthe\s+main\s+idea\s+(?:is|of)',
        r'\bthe\s+purpose\s+(?:is|of|for)',
        
        # Inference/conclusion
        r'\binfer\s+(?:what|why|how|from)',
        r'\bconclude\s+(?:that|what)',
        r'\bpredict\s+(?:what|the)',
        r'\bestimate\s+(?:what|the)',
        r'\bimply\s+(?:that|what)',
        
        # Comparison (understanding level)
        r'\bcompare\s+(?:the|these)\s+(?:to\s+understand|in\s+terms)',
        r'\bcontrast\s+(?:the|these)\s+(?:to\s+understand|in\s+terms)',
        r'\bdistinguish\s+between',
        r'\bdifferentiate\s+between',
        
        # Relationships
        r'\bwhat\s+is\s+the\s+relationship\s+between',
        r'\bhow\s+(?:does|do|is|are)\s+\w+\s+(?:related\s+to|connected\s+to)',
        r'\bthe\s+connection\s+between',
        
        # Examples/illustration
        r'\bgive\s+(?:an\s+)?example\s+of',
        r'\billustrate\s+(?:how|the)',
        r'\bdemonstrate\s+(?:how|the)',
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
        
        # Practice/demonstration
        r'\bdemonstrate\s+(?:your|the)\s+(?:ability|understanding)\s+by',
        r'\bshow\s+how\s+(?:to|you\s+would)',
        r'\bpractice\s+(?:by|using)',
        
        # Modification/adaptation
        r'\bmodify\s+(?:the|this)\s+(?:to|for)',
        r'\badapt\s+(?:the|this)\s+(?:to|for)',
        r'\badjust\s+(?:the|this)',
    ]
    
    # ========== C4 (ANALYZE) PATTERNS ==========
    FORCE_C4_PATTERNS = [
        # Analysis/breakdown
        r'\banalyze\s+(?:the|this|how)',
        r'\bexamine\s+(?:the|how)',
        r'\binvestigate\s+(?:the|how|why)',
        r'\bbreak\s+down\s+(?:the|into)',
        
        # Comparison (analytical)
        r'\bcompare\s+and\s+contrast',
        r'\bwhat\s+are\s+the\s+(?:differences|similarities)\s+between',
        r'\bhow\s+(?:does|do)\s+\w+\s+differ\s+from',
        
        # Organization/structure
        r'\borganize\s+(?:the|these)\s+(?:into|by)',
        r'\bcategorize\s+(?:the|these)',
        r'\bclassify\s+(?:the|these)',
        r'\bstructure\s+(?:the|this)',
        
        # Relationships/patterns
        r'\bwhat\s+is\s+the\s+function\s+of',
        r'\bwhat\s+is\s+the\s+relationship\s+between\s+\w+\s+and\s+its',
        r'\bidentify\s+the\s+(?:pattern|trend|relationship)',
        r'\bwhat\s+patterns?\s+(?:can\s+you|do\s+you)\s+see',
        
        # Cause/effect
        r'\bwhat\s+(?:are\s+the\s+)?(?:causes?|reasons?)\s+(?:of|for|behind)',
        r'\bwhat\s+(?:are\s+the\s+)?effects?\s+of',
        r'\bwhy\s+does\s+\w+\s+(?:cause|lead\s+to|result\s+in)',
        
        # Components/elements
        r'\bwhat\s+are\s+the\s+(?:parts|components|elements)\s+of',
        r'\bidentify\s+the\s+(?:key|main|essential)\s+(?:factors|components)',
    ]
    
    # ========== C5 (EVALUATE) PATTERNS ==========
    FORCE_C5_PATTERNS = [
        # Evaluation/judgment
        r'\bevaluate\s+(?:the|this|how)',
        r'\bassess\s+(?:the|this|how)',
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
        r'\bsupport\s+(?:your|the)\s+(?:opinion|position|argument)',
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
        
        # Criteria/standards
        r'\bbased\s+on\s+(?:the\s+)?criteria',
        r'\baccording\s+to\s+(?:the\s+)?standards?',
        r'\bto\s+what\s+extent',
        r'\bhow\s+well\s+does',
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
    ]
    
    # ========== ANTI-PATTERNS (prevent false positives) ==========
    
    # NOT C1 if these exist
    NOT_C1_PATTERNS = [
        r'\banalyze\b',
        r'\bevaluate\b',
        r'\bcreate\s+(?:a|an)\b',
        r'\bdesign\s+(?:a|an)\b',
        r'\bapply\s+(?:to\s+solve|to\s+calculate)\b',
        r'\bcompare\s+and\s+contrast\b',
        r'\bjustify\b',
        r'\bcritique\b',
    ]
    
    # NOT C2 if these exist
    NOT_C2_PATTERNS = [
        r'\bcalculate\b',
        r'\bsolve\s+(?:the\s+)?problem\b',
        r'\banalyze\s+(?:the\s+)?(?:data|results)\b',
        r'\bevaluate\s+(?:the\s+)?(?:effectiveness|quality)\b',
        r'\bcreate\s+(?:a|an)\b',
        r'\bdesign\s+(?:a|an)\b',
    ]
    
    # NOT C3 if these exist
    NOT_C3_PATTERNS = [
        r'\banalyze\s+(?:why|how)\b',
        r'\bevaluate\s+(?:whether|if)\b',
        r'\bcreate\s+(?:a\s+new|an\s+original)\b',
        r'\bdesign\s+(?:a\s+new|an\s+original)\b',
        r'\bjustify\s+your\b',
    ]
    
    # NOT C4 if these exist  
    NOT_C4_PATTERNS = [
        r'\bcreate\s+(?:a|an)\b',
        r'\bdesign\s+(?:a|an)\b',
        r'\bgenerate\s+(?:a|an)\b',
        r'\bpropose\s+(?:a|an)\b',
    ]
    
    # NOT C5 if these exist
    NOT_C5_PATTERNS = [
        r'\bcreate\s+(?:a|an)\b',
        r'\bdesign\s+(?:a|an)\b',
        r'\bgenerate\s+(?:a|an)\b',
        r'\bproduce\s+(?:a|an)\b',
        r'\bcompose\s+(?:a|an)\b',
    ]
    
    # NOT C6 - none needed (C6 is highest)
    NOT_C6_PATTERNS = []
    
    # ========== KEYWORD LISTS FOR SECONDARY CHECKS ==========
    
    C1_KEYWORDS = [
        'define', 'identify', 'list', 'name', 'recall', 'recognize',
        'state', 'label', 'match', 'who', 'what', 'when', 'where',
        'memorize', 'repeat', 'reproduce'
    ]
    
    C2_KEYWORDS = [
        'explain', 'describe', 'summarize', 'paraphrase', 'interpret',
        'infer', 'conclude', 'predict', 'estimate', 'distinguish',
        'differentiate', 'compare', 'contrast', 'illustrate'
    ]
    
    C3_KEYWORDS = [
        'apply', 'use', 'solve', 'calculate', 'compute', 'implement',
        'execute', 'carry out', 'perform', 'demonstrate', 'practice',
        'modify', 'adapt'
    ]
    
    C4_KEYWORDS = [
        'analyze', 'examine', 'investigate', 'compare and contrast',
        'categorize', 'classify', 'organize', 'differentiate',
        'distinguish', 'relate', 'function', 'pattern'
    ]
    
    C5_KEYWORDS = [
        'evaluate', 'assess', 'judge', 'critique', 'justify',
        'defend', 'recommend', 'prioritize', 'rate', 'rank',
        'appraise', 'value'
    ]
    
    C6_KEYWORDS = [
        'create', 'design', 'construct', 'develop', 'formulate',
        'devise', 'generate', 'plan', 'compose', 'synthesize',
        'propose', 'hypothesize', 'invent'
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
    
    def adjust_classification(self, question_text, ml_prediction):
        """
        AGGRESSIVE pattern-based adjustment
        
        Priority:
        1. Check C6 patterns (highest level) first
        2. Check C5, C4, C3, C2, C1 in descending order
        3. Each level checked only if no anti-patterns exist
        4. Keep ML prediction if no strong patterns found
        
        Args:
            question_text: Original question text
            ml_prediction: ML model prediction dict
            
        Returns:
            Adjusted prediction dict with adjustment metadata
        """
        question_lower = question_text.lower().strip()
        
        ml_level = ml_prediction['category']
        ml_confidence = ml_prediction['confidence']
        
        # Check each level from highest to lowest
        # This ensures we don't under-classify complex questions
        
        # === CHECK C6 (CREATE) ===
        if self._check_level(
            question_lower,
            self.compiled_force_c6,
            self.C6_KEYWORDS,
            [],  # No anti-patterns for C6
            ml_level,
            'C6'
        ):
            return self._create_result('C6', 'Create', 0.93, ml_prediction, 
                                      'force_c6_pattern', ml_level, ml_confidence)
        
        # === CHECK C5 (EVALUATE) ===
        if self._check_level(
            question_lower,
            self.compiled_force_c5,
            self.C5_KEYWORDS,
            self.compiled_not_c5,
            ml_level,
            'C5'
        ):
            return self._create_result('C5', 'Evaluate', 0.91, ml_prediction,
                                      'force_c5_pattern', ml_level, ml_confidence)
        
        # === CHECK C4 (ANALYZE) ===
        if self._check_level(
            question_lower,
            self.compiled_force_c4,
            self.C4_KEYWORDS,
            self.compiled_not_c4,
            ml_level,
            'C4'
        ):
            return self._create_result('C4', 'Analyze', 0.89, ml_prediction,
                                      'force_c4_pattern', ml_level, ml_confidence)
        
        # === CHECK C3 (APPLY) ===
        if self._check_level(
            question_lower,
            self.compiled_force_c3,
            self.C3_KEYWORDS,
            self.compiled_not_c3,
            ml_level,
            'C3'
        ):
            return self._create_result('C3', 'Apply', 0.87, ml_prediction,
                                      'force_c3_pattern', ml_level, ml_confidence)
        
        # === CHECK C2 (UNDERSTAND) ===
        if self._check_level(
            question_lower,
            self.compiled_force_c2,
            self.C2_KEYWORDS,
            self.compiled_not_c2,
            ml_level,
            'C2'
        ):
            return self._create_result('C2', 'Understand', 0.90, ml_prediction,
                                      'force_c2_pattern', ml_level, ml_confidence)
        
        # === CHECK C1 (REMEMBER) ===
        if self._check_level(
            question_lower,
            self.compiled_force_c1,
            self.C1_KEYWORDS,
            self.compiled_not_c1,
            ml_level,
            'C1'
        ):
            return self._create_result('C1', 'Remember', 0.92, ml_prediction,
                                      'force_c1_pattern', ml_level, ml_confidence)
        
        # === CONFIDENCE ADJUSTMENT ===
        # If ML is very confident (>0.85), trust it
        # If ML is uncertain (<0.65), downgrade complex classifications
        if ml_confidence < 0.65 and ml_level in ['C5', 'C6']:
            # Uncertain high classification -> downgrade
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
                     anti_patterns, ml_level, target_level):
        """
        Check if question matches a specific Bloom level
        
        Returns True if:
        - Force pattern matches AND no anti-patterns
        - OR strong keyword presence AND no anti-patterns
        """
        # Check anti-patterns first
        if any(p.search(question_lower) for p in anti_patterns):
            return False
        
        # Check force patterns
        has_force_pattern = any(p.search(question_lower) for p in force_patterns)
        
        # Check keywords
        keyword_count = sum(1 for kw in keywords if kw.lower() in question_lower)
        has_strong_keywords = keyword_count >= 2
        
        # Decision logic
        if has_force_pattern:
            if ml_level != target_level:
                logger.info(
                    f"ADJUSTED: ML={ml_level} -> {target_level} (pattern match)"
                )
            return True
        
        if has_strong_keywords and keyword_count >= 3:
            # Very strong keyword presence
            if ml_level != target_level:
                logger.info(
                    f"ADJUSTED: ML={ml_level} -> {target_level} ({keyword_count} keywords)"
                )
            return True
        
        return False
    
    def _create_result(self, category, category_name, confidence, 
                       ml_prediction, reason, ml_category, ml_confidence):
        """Create adjusted result dictionary"""
        was_adjusted = (category != ml_category or 
                       abs(confidence - ml_confidence) > 0.05)
        
        return {
            'category': category,
            'category_name': category_name,
            'confidence': confidence,
            'all_probabilities': ml_prediction['all_probabilities'],
            'adjustment_reason': reason,
            'ml_category': ml_category,
            'ml_confidence': ml_confidence,
            'was_adjusted': was_adjusted
        }


def adjust_classification_with_patterns(question_text, ml_prediction):
    """Convenience function for English pattern adjustment"""
    adjuster = EnglishBloomAdjuster()
    return adjuster.adjust_classification(question_text, ml_prediction)