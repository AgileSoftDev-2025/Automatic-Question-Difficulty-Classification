# apps/klasifikasi/file_extractor.py - NUCLEAR OPTION: MAXIMUM ACCURACY

import re
import logging
from pathlib import Path
from typing import List, Dict
from collections import OrderedDict

logger = logging.getLogger(__name__)

# Only PyPDF2 - unstructured is causing duplicates
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.error("PyPDF2 not available!")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

logger.info(f"PyPDF2: {PYPDF2_AVAILABLE}, python-docx: {DOCX_AVAILABLE}")


class QuestionExtractor:
    """
    ULTRA-AGGRESSIVE question extractor
    Focus: REMOVE DUPLICATES and get CLEAN questions only
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt', '.doc']
        
    def extract_questions(self, file_path: str) -> List[str]:
        """
        Extract questions with ZERO TOLERANCE for duplicates
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {extension}")
        
        try:
            logger.info(f"=== EXTRACTING FROM {file_path.name} ===")
            
            # Step 1: Get raw text (PDF ONLY - no unstructured!)
            raw_text = self._extract_text(file_path, extension)
            logger.info(f"Raw text: {len(raw_text)} chars")
            
            # Step 2: NUCLEAR DEDUPLICATION
            cleaned_text = self._nuclear_clean(raw_text)
            logger.info(f"After deduplication: {len(cleaned_text)} chars")
            
            # Step 3: Extract numbered questions
            questions_dict = self._extract_numbered_questions(cleaned_text)
            logger.info(f"Found {len(questions_dict)} numbered blocks")
            
            # Step 4: Clean and validate each question
            final_questions = []
            for num in sorted(questions_dict.keys()):
                question = self._clean_question(questions_dict[num])
                if question and self._is_valid_question(question):
                    final_questions.append(question)
                    logger.debug(f"Q{num}: {question[:60]}...")
                else:
                    logger.warning(f"Q{num} REJECTED")
            
            logger.info(f"=== EXTRACTED {len(final_questions)} VALID QUESTIONS ===")
            return final_questions
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            raise
    
    def _extract_text(self, file_path: Path, extension: str) -> str:
        """Extract text - PDF only with PyPDF2"""
        if extension == '.pdf':
            if not PYPDF2_AVAILABLE:
                raise RuntimeError("PyPDF2 not installed")
            
            with open(file_path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                text = ""
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    logger.debug(f"Page {i+1}: {len(page_text)} chars")
                return text
        
        elif extension == '.docx':
            if not DOCX_AVAILABLE:
                raise RuntimeError("python-docx not installed")
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        
        elif extension == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        raise ValueError(f"Cannot extract from {extension}")
    
    def _nuclear_clean(self, text: str) -> str:
        """
        NUCLEAR DEDUPLICATION
        
        Problem: Your PDF has every line duplicated
        Solution: Remove consecutive duplicate lines aggressively
        """
        lines = text.split('\n')
        
        # Step 1: Remove exact consecutive duplicates
        cleaned = []
        prev_line = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip metadata
            if self._is_metadata(line):
                continue
            
            # Skip if exact duplicate of previous
            if prev_line and line == prev_line:
                logger.debug(f"SKIP EXACT DUP: {line[:50]}")
                continue
            
            # Skip if 90%+ similar to previous (fuzzy duplicate)
            if prev_line and self._similarity(line, prev_line) > 0.90:
                logger.debug(f"SKIP FUZZY DUP: {line[:50]}")
                continue
            
            cleaned.append(line)
            prev_line = line
        
        # Step 2: Join and normalize whitespace
        full_text = " ".join(cleaned)
        full_text = re.sub(r'\s+', ' ', full_text)
        
        # Step 3: Remove "Jawaban:" sections entirely
        # Pattern: "Jawaban: X. text" appears after each question
        full_text = re.sub(r'Jawaban:\s*[A-E]\.\s+[^\d]+(?=\d+\.|\Z)', '', full_text, flags=re.IGNORECASE)
        
        return full_text.strip()
    
    def _is_metadata(self, line: str) -> bool:
        """Check if line is metadata/header/footer"""
        line_lower = line.lower().strip()
        
        # Too short
        if len(line) < 3:
            return True
        
        # Just numbers
        if re.match(r'^\d+$', line):
            return True
        
        # Headers/footers
        metadata_patterns = [
            r'^page\s+\d+',
            r'^halaman\s+\d+',
            r'^soal\s+pilihan\s+ganda',
            r'^\d+\s+of\s+\d+',
            r'^(?:header|footer|copyright)',
        ]
        
        for pattern in metadata_patterns:
            if re.match(pattern, line_lower):
                return True
        
        return False
    
    def _similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts"""
        # Normalize
        t1 = re.sub(r'[^\w\s]', '', text1.lower())
        t2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        if not t1 or not t2:
            return 0.0
        
        # Simple word-based similarity
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_numbered_questions(self, text: str) -> Dict[int, str]:
        """
        Extract questions by number (1., 2., 3., etc.)
        Returns OrderedDict: {1: "question text", 2: "question text", ...}
        """
        # Split by question numbers
        # Pattern: digit(s) followed by period and space
        pattern = r'(\d+)\.\s+'
        
        parts = re.split(pattern, text)
        
        questions = OrderedDict()
        current_num = None
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Is this a question number?
            if re.match(r'^\d+$', part):
                current_num = int(part)
            elif current_num is not None:
                # This is the question text for current_num
                questions[current_num] = part
                current_num = None
        
        return questions
    
    def _clean_question(self, text: str) -> str:
        """
        Clean a single question block
        
        Remove:
        - Answer choices (A. B. C. D. E.)
        - "Jawaban:" sections
        - Trailing dots
        - Extra whitespace
        """
        # Remove "Jawaban:" and everything after
        text = re.split(r'(?:jawaban|answer)\s*:', text, flags=re.IGNORECASE)[0]
        
        # Remove answer choices
        # Pattern 1: "A. text B. text C. text"
        text = re.sub(r'\s+[A-E]\.\s+[^\n]+', '', text)
        
        # Pattern 2: Find first "A." and cut everything after
        match = re.search(r'\b[A-E]\.\s+', text)
        if match:
            text = text[:match.start()]
        
        # Remove trailing punctuation
        text = re.sub(r'\.{2,}$', '', text)
        text = re.sub(r'\s*…\s*$', '', text)
        text = text.rstrip('.')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _is_valid_question(self, text: str) -> bool:
        """
        Strict validation
        
        Valid question must:
        - Be 10-500 characters
        - Have 3+ words
        - Not be all caps (headers)
        - Not start with answer choice
        - Have meaningful content
        """
        if not text:
            return False
        
        # Length check
        if len(text) < 10 or len(text) > 500:
            return False
        
        # Word count
        words = text.split()
        if len(words) < 3:
            return False
        
        # Not all caps
        if text.isupper() and len(text) > 15:
            return False
        
        # Doesn't start with answer choice
        if re.match(r'^[A-E]\.\s', text):
            return False
        
        # Has letters
        if sum(1 for c in text if c.isalpha()) < 5:
            return False
        
        # Not just metadata
        if any(kw in text.lower() for kw in ['copyright', 'page', 'halaman', 'header']):
            return False
        
        return True
    
    def validate_questions(self, questions: List[str]) -> Dict:
        """Validate extracted questions"""
        if not questions:
            return {
                'valid': False,
                'error': 'No questions found',
                'count': 0,
            }
        
        if len(questions) < 3:
            return {
                'valid': False,
                'error': f'Only {len(questions)} questions found',
                'count': len(questions),
            }
        
        # Quality metrics
        avg_length = sum(len(q) for q in questions) / len(questions)
        short_count = sum(1 for q in questions if len(q) < 20)
        
        quality = 'high'
        if avg_length < 30:
            quality = 'medium'
        if avg_length < 20:
            quality = 'low'
        
        return {
            'valid': True,
            'count': len(questions),
            'avg_length': avg_length,
            'quality': quality
        }


def extract_questions_from_file(file_path: str) -> List[str]:
    """Convenience function"""
    extractor = QuestionExtractor()
    return extractor.extract_questions(file_path)