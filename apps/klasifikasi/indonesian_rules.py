# apps/klasifikasi/indonesian_rules.py

"""
Indonesian-specific pattern recognition for Bloom's Taxonomy classification
Adjusts ML model predictions based on question structure and keywords
"""

import re
import logging

logger = logging.getLogger(__name__)


class IndonesianBloomAdjuster:
    """
    Adjusts Bloom's Taxonomy classifications based on Indonesian question patterns
    """
    
    # Question patterns mapped to Bloom levels
    PATTERNS = {
        'C1': {
            'keywords': [
                'sebutkan', 'tuliskan', 'identifikasi', 'definisi', 'pengertian',
                'apa itu', 'apa yang dimaksud', 'jelaskan pengertian',
                'nama', 'jenis-jenis', 'macam-macam', 'contoh',
                'siapa', 'kapan', 'dimana', 'berapa',
                'salah satu', 'komponen', 'unsur', 'bagian dari',
                'istilah', 'maksud dari', 'arti dari'
            ],
            'patterns': [
                r'^sebutkan',
                r'^tuliskan',
                r'^apa\s+(yang\s+dimaksud|itu|pengertian)',
                r'definisi.+adalah',
                r'pengertian.+adalah',
                r'^identifikasi',
                r'salah\s+satu\s+(komponen|faktor|kategori)',
                r'yang\s+dimaksud\s+dengan.+adalah'
            ],
            'confidence_boost': 0.15
        },
        'C2': {
            'keywords': [
                'jelaskan', 'uraikan', 'deskripsikan', 'gambarkan',
                'bedakan', 'perbedaan', 'persamaan', 'hubungan',
                'mengapa', 'bagaimana', 'klasifikasi',
                'interpretasi', 'maksud', 'tujuan dari',
                'fungsi', 'kegunaan', 'manfaat',
                'kesimpulan dari', 'ringkasan'
            ],
            'patterns': [
                r'^jelaskan(?!\s+cara)',  # "Jelaskan" but not "Jelaskan cara"
                r'^uraikan',
                r'^deskripsikan',
                r'^bedakan',
                r'perbedaan\s+antara',
                r'apa\s+fungsi',
                r'mengapa',
                r'bagaimana(?!\s+(cara|membuat|merancang))',
                r'hubungan\s+antara'
            ],
            'confidence_boost': 0.12
        },
        'C3': {
            'keywords': [
                'gunakan', 'terapkan', 'implementasikan', 'praktikkan',
                'demonstrasikan', 'hitunglah', 'buatlah perhitungan',
                'aplikasikan', 'selesaikan', 'operasikan',
                'jelaskan cara', 'bagaimana cara', 'lakukan',
                'eksekusi', 'jalankan', 'konfigurasi',
                'tahap', 'langkah-langkah', 'prosedur'
            ],
            'patterns': [
                r'^gunakan',
                r'^terapkan',
                r'^implementasikan',
                r'^aplikasikan',
                r'^hitunglah',
                r'^selesaikan',
                r'jelaskan\s+cara',
                r'bagaimana\s+cara',
                r'langkah-langkah',
                r'tahap.+dalam'
            ],
            'confidence_boost': 0.10
        },
        'C4': {
            'keywords': [
                'analisis', 'analisislah', 'bandingkan', 'kontras',
                'bedakan', 'kategorikan', 'klasifikasikan',
                'organisasi', 'susun', 'strukturkan',
                'pisahkan', 'uraikan komponen', 'identifikasi penyebab',
                'hubungan sebab akibat', 'faktor yang mempengaruhi',
                'mengapa terjadi', 'penyebab', 'akibat dari'
            ],
            'patterns': [
                r'^analisis',
                r'^analisislah',
                r'^bandingkan',
                r'perbedaan.+dan.+perbedaan',
                r'faktor.+mempengaruhi',
                r'penyebab.+tidak',
                r'mengapa.+(terjadi|tidak|gagal)',
                r'identifikasi\s+penyebab',
                r'hubungan\s+sebab'
            ],
            'confidence_boost': 0.10
        },
        'C5': {
            'keywords': [
                'evaluasi', 'nilai', 'kritik', 'berikan penilaian',
                'apakah efektif', 'apakah tepat', 'keunggulan dan kelemahan',
                'pro dan kontra', 'setuju atau tidak', 'justifikasi',
                'rekomendasikan', 'putuskan', 'pilih yang terbaik',
                'beri pendapat', 'kriteria', 'prioritaskan',
                'efektivitas', 'efisiensi', 'validitas'
            ],
            'patterns': [
                r'^evaluasi',
                r'^nilai',
                r'keunggulan\s+dan\s+kelemahan',
                r'apakah\s+(efektif|tepat|sesuai|valid)',
                r'setuju\s+atau\s+tidak',
                r'pro\s+dan\s+kontra',
                r'berikan\s+penilaian',
                r'efektivitas.+(dibandingkan|versus)'
            ],
            'confidence_boost': 0.08
        },
        'C6': {
            'keywords': [
                'rancang', 'rancanglah', 'buatlah', 'ciptakan',
                'kembangkan', 'desain', 'susunlah', 'konstruksi',
                'formulasikan', 'rencanakan', 'kreasikan',
                'hasilkan', 'produksi', 'bangun', 'integrasikan',
                'rancang sistem', 'buat rancangan', 'desain arsitektur',
                'kembangkan model', 'susun strategi'
            ],
            'patterns': [
                r'^rancang',
                r'^buatlah\s+(rancangan|desain|sistem|model|algoritma|strategi)',
                r'^desain',
                r'^kembangkan',
                r'^susunlah\s+(strategi|rencana|sistem)',
                r'^ciptakan',
                r'rancang\s+(sistem|algoritma|database|arsitektur)',
                r'buat\s+rancangan',
                r'kembangkan\s+(aplikasi|sistem|model)'
            ],
            'confidence_boost': 0.08
        }
    }
    
    def __init__(self):
        self.compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency"""
        compiled = {}
        for level, data in self.PATTERNS.items():
            compiled[level] = {
                'patterns': [re.compile(p, re.IGNORECASE) for p in data['patterns']],
                'keywords': data['keywords'],
                'boost': data['confidence_boost']
            }
        return compiled
    
    def adjust_classification(self, question_text, ml_prediction):
        """
        Adjust ML classification based on Indonesian patterns
        
        Args:
            question_text: Original question text in Indonesian
            ml_prediction: Dict with 'category', 'confidence', 'all_probabilities'
        
        Returns:
            Adjusted prediction dict with same structure
        """
        # Clean and normalize question
        question_lower = question_text.lower().strip()
        
        # Get pattern matches for each level
        level_scores = {}
        for level, data in self.compiled_patterns.items():
            score = self._calculate_pattern_score(question_lower, data)
            level_scores[level] = score
        
        # Find best matching level
        best_pattern_level = max(level_scores.items(), key=lambda x: x[1])
        
        # Decide whether to override ML prediction
        ml_level = ml_prediction['category']
        ml_confidence = ml_prediction['confidence']
        
        # Apply adjustment logic
        adjusted = self._apply_adjustment_logic(
            question_lower,
            ml_level,
            ml_confidence,
            best_pattern_level,
            ml_prediction['all_probabilities']
        )
        
        logger.debug(
            f"Q: '{question_text[:50]}...' | "
            f"ML: {ml_level}({ml_confidence:.2f}) -> "
            f"Adjusted: {adjusted['category']}({adjusted['confidence']:.2f}) | "
            f"Pattern: {best_pattern_level[0]}({best_pattern_level[1]:.2f})"
        )
        
        return adjusted
    
    def _calculate_pattern_score(self, question_lower, pattern_data):
        """Calculate how well question matches patterns for a level"""
        score = 0.0
        
        # Check regex patterns (high weight)
        for pattern in pattern_data['patterns']:
            if pattern.search(question_lower):
                score += 0.3
        
        # Check keywords (medium weight)
        for keyword in pattern_data['keywords']:
            if keyword in question_lower:
                score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _apply_adjustment_logic(self, question_lower, ml_level, ml_confidence, 
                                best_pattern, all_probs):
        """
        Apply logic to decide whether to adjust ML prediction
        
        Strategy:
        1. If pattern match is strong (>0.5) and ML confidence is low (<0.7), use pattern
        2. If pattern level is adjacent to ML level and confidence is medium, blend
        3. Otherwise keep ML prediction but boost confidence if pattern agrees
        """
        pattern_level, pattern_score = best_pattern
        
        # Case 1: Strong pattern match with low ML confidence
        if pattern_score > 0.5 and ml_confidence < 0.7:
            return self._create_adjusted_prediction(
                pattern_level,
                min(ml_confidence + self.compiled_patterns[pattern_level]['boost'], 0.95),
                all_probs,
                reason="strong_pattern_low_ml"
            )
        
        # Case 2: Pattern strongly suggests C1 (recall) and ML says higher
        if pattern_level == 'C1' and pattern_score > 0.4 and ml_level in ['C2', 'C3', 'C4', 'C5', 'C6']:
            if self._is_recall_question(question_lower):
                return self._create_adjusted_prediction(
                    'C1',
                    min(0.85 + pattern_score * 0.1, 0.95),
                    all_probs,
                    reason="clear_recall_pattern"
                )
        
        # Case 3: Pattern matches ML prediction - boost confidence
        if pattern_level == ml_level and pattern_score > 0.3:
            boosted_confidence = min(
                ml_confidence + self.compiled_patterns[pattern_level]['boost'],
                0.98
            )
            return self._create_adjusted_prediction(
                ml_level,
                boosted_confidence,
                all_probs,
                reason="pattern_confirms_ml"
            )
        
        # Case 4: Pattern suggests adjacent level with good score
        if pattern_score > 0.4:
            level_distance = abs(int(pattern_level[1]) - int(ml_level[1]))
            if level_distance == 1:  # Adjacent levels
                # Blend: if ML is confident, keep it; if not, consider pattern
                if ml_confidence < 0.6:
                    return self._create_adjusted_prediction(
                        pattern_level,
                        0.70,
                        all_probs,
                        reason="adjacent_pattern_low_ml"
                    )
        
        # Default: Keep ML prediction
        return {
            'category': ml_level,
            'confidence': ml_confidence,
            'all_probabilities': all_probs,
            'category_name': self._get_category_name(ml_level),
            'adjustment_reason': 'ml_prediction_kept'
        }
    
    def _is_recall_question(self, question_lower):
        """Check if question is clearly asking for recall/definition"""
        recall_indicators = [
            'apa yang dimaksud',
            'pengertian',
            'definisi',
            'apa itu',
            'sebutkan',
            'tuliskan',
            'salah satu'
        ]
        return any(ind in question_lower for ind in recall_indicators)
    
    def _create_adjusted_prediction(self, level, confidence, all_probs, reason="adjusted"):
        """Create adjusted prediction dict"""
        return {
            'category': level,
            'confidence': confidence,
            'all_probabilities': all_probs,
            'category_name': self._get_category_name(level),
            'adjustment_reason': reason
        }
    
    def _get_category_name(self, code):
        """Get category full name"""
        names = {
            'C1': 'Remember',
            'C2': 'Understand',
            'C3': 'Apply',
            'C4': 'Analyze',
            'C5': 'Evaluate',
            'C6': 'Create'
        }
        return names.get(code, code)


def adjust_classification_with_patterns(question_text, ml_prediction):
    """
    Convenience function to adjust classification
    
    Args:
        question_text: Indonesian question text
        ml_prediction: ML model prediction dict
    
    Returns:
        Adjusted prediction dict
    """
    adjuster = IndonesianBloomAdjuster()
    return adjuster.adjust_classification(question_text, ml_prediction)