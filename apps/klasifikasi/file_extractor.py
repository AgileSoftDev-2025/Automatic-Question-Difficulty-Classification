# apps/klasifikasi/file_extractor.py - ULTRA-ACCURATE BILINGUAL EXTRACTOR

"""
ULTRA-AGGRESSIVE bilingual question extractor
Focus: Extract EVERY question, handle both Indonesian and English
Strategy: Multiple extraction methods + validation
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from collections import OrderedDict

logger = logging.getLogger(__name__)

# Only PyPDF2 - unstructured causes duplicates
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
    ULTRA-AGGRESSIVE bilingual question extractor
    Handles: Indonesian, English, mixed formats
    Strategy: Multi-pass extraction + smart validation
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt', '.doc']
        
        # Question indicators (Indonesian + English)
        self.question_indicators = [
            # English
            r'\bwhat\b', r'\bwhich\b', r'\bwho\b', r'\bwhere\b', r'\bwhen\b',
            r'\bwhy\b', r'\bhow\b', r'\bdefine\b', r'\bexplain\b', r'\bdescribe\b',
            r'\bidentify\b', r'\banalyze\b', r'\bevaluate\b', r'\bcreate\b',
            r'\bdesign\b', r'\bcalculate\b', r'\bcompare\b', r'\bapply\b',
            r'\bcritique\b', r'\bjustify\b', r'\bdevelop\b',
            
            # Indonesian
            r'\bapa\b', r'\bbagaimana\b', r'\bmengapa\b', r'\bsiapa\b',
            r'\bdimana\b', r'\bkapan\b', r'\bjelaskan\b', r'\bsebutkan\b',
            r'\bidentifikasi\b', r'\btentukan\b', r'\bhitunglah\b',
            r'\banalisis\b', r'\bevaluasi\b', r'\brancang\b', r'\bbuatlah\b',
        ]
        
    def extract_questions(self, file_path: str) -> List[str]:
        """
        Extract questions with MULTI-PASS strategy
        
        Strategy:
        1. Extract raw text
        2. Clean duplicates (your PDF has them)
        3. Try numbered extraction (1., 2., 3.)
        4. Try lettered extraction (A., B., C. at start)
        5. Try header extraction (Q1, Question 1, etc.)
        6. Validate each question
        7. Return ALL valid questions
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {extension}")
        
        try:
            logger.info(f"=== EXTRACTING FROM {file_path.name} ===")
            
            # Step 1: Get raw text
            raw_text = self._extract_text(file_path, extension)
            logger.info(f"Raw text: {len(raw_text)} chars")
            
            # Step 2: Clean (remove duplicates, metadata)
            cleaned_text = self._clean_text(raw_text)
            logger.info(f"After cleaning: {len(cleaned_text)} chars")
            
            # Step 3: MULTI-PASS EXTRACTION
            questions_dict = OrderedDict()
            
            # Pass 1: Numbered questions (1., 2., 3.)
            numbered = self._extract_numbered_questions(cleaned_text)
            logger.info(f"Pass 1 (numbered): Found {len(numbered)} questions")
            questions_dict.update(numbered)
            
            # Pass 2: Header-based (Question 1, Q1, etc.)
            if len(questions_dict) < 5:  # If numbered didn't work well
                header_based = self._extract_header_questions(cleaned_text)
                logger.info(f"Pass 2 (header): Found {len(header_based)} questions")
                questions_dict.update(header_based)
            
            # Pass 3: Sentence-based (questions ending with ?)
            if len(questions_dict) < 5:  # Still not enough
                sentence_based = self._extract_sentence_questions(cleaned_text)
                logger.info(f"Pass 3 (sentence): Found {len(sentence_based)} questions")
                questions_dict.update(sentence_based)
            
            # Step 4: Clean and validate
            final_questions = []
            for num in sorted(questions_dict.keys()):
                question = self._clean_question(questions_dict[num])
                
                # Validate
                if question and self._is_valid_question(question):
                    final_questions.append(question)
                    logger.debug(f"✓ Q{num}: {question[:60]}...")
                else:
                    logger.warning(f"✗ Q{num} REJECTED: {question[:60] if question else 'empty'}...")
            
            logger.info(f"=== EXTRACTED {len(final_questions)} VALID QUESTIONS ===")
            
            # If we got less than expected, log warning
            if len(final_questions) < len(questions_dict) * 0.8:
                logger.warning(
                    f"Only {len(final_questions)}/{len(questions_dict)} questions passed validation. "
                    f"Check validation rules."
                )
            
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
    
    def _clean_text(self, text: str) -> str:
        """
        AGGRESSIVE cleaning to remove duplicates and noise
        
        Your PDF has duplicates, so we need to:
        1. Remove consecutive duplicate lines
        2. Remove metadata (headers, footers, page numbers)
        3. Normalize whitespace
        4. Keep "Answer:" sections for validation
        """
        lines = text.split('\n')
        
        cleaned = []
        prev_line = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty
            if not line:
                continue
            
            # Skip metadata
            if self._is_metadata(line):
                continue
            
            # Skip exact duplicates
            if prev_line and line == prev_line:
                logger.debug(f"SKIP DUPLICATE: {line[:50]}")
                continue
            
            # Skip very similar lines (90%+ similarity)
            if prev_line and self._similarity(line, prev_line) > 0.90:
                logger.debug(f"SKIP SIMILAR: {line[:50]}")
                continue
            
            cleaned.append(line)
            prev_line = line
        
        # Join and normalize
        full_text = "\n".join(cleaned)
        
        return full_text.strip()
    
    def _extract_numbered_questions(self, text: str) -> OrderedDict:
        """
        Extract questions numbered as: 1., 2., 3., etc.
        
        Pattern: Number + period + space + text
        Stops at: Answer:, next number, or end of text
        """
        questions = OrderedDict()
        
        # Split by pattern: digit(s) + period + space
        # Use lookahead to keep the number
        parts = re.split(r'(?=\d+\.\s)', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if starts with number pattern
            match = re.match(r'^(\d+)\.\s+(.+)', part, re.DOTALL)
            if not match:
                continue
            
            num = int(match.group(1))
            content = match.group(2).strip()
            
            # Extract question part (before "Answer:")
            # Split by "Answer:" and take first part
            question_parts = re.split(r'\s*Answer\s*:', content, flags=re.IGNORECASE)
            question_text = question_parts[0].strip()
            
            if question_text:
                questions[num] = question_text
                logger.debug(f"Numbered Q{num}: {question_text[:60]}...")
        
        return questions
    
    def _extract_header_questions(self, text: str) -> OrderedDict:
        """
        Extract questions with headers like:
        - Question 1:
        - Q1:
        - Item 1:
        - Soal 1:
        """
        questions = OrderedDict()
        
        # Pattern: (Question|Q|Item|Soal) + number + colon/period + text
        pattern = r'(?:Question|Q|Item|Soal)\s*(\d+)\s*[:.]\s*(.+?)(?=(?:Question|Q|Item|Soal)\s*\d+|Answer\s*:|$)'
        
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            num = int(match.group(1))
            content = match.group(2).strip()
            
            # Clean up
            content = re.sub(r'\s+', ' ', content)
            
            if content:
                questions[num] = content
                logger.debug(f"Header Q{num}: {content[:60]}...")
        
        return questions
    
    def _extract_sentence_questions(self, text: str) -> OrderedDict:
        """
        Extract questions based on sentence patterns
        
        For texts without clear numbering, find sentences that:
        1. End with ?
        2. Start with question words
        3. Have question indicators
        """
        questions = OrderedDict()
        
        # Split by sentence
        sentences = re.split(r'[.!?]\s+', text)
        
        question_num = 1
        for sentence in sentences:
            sentence = sentence.strip()
            
            if not sentence:
                continue
            
            # Must be substantial
            if len(sentence) < 20:
                continue
            
            # Check for question indicators
            sentence_lower = sentence.lower()
            has_indicator = any(
                re.search(pattern, sentence_lower) 
                for pattern in self.question_indicators
            )
            
            if has_indicator or sentence.endswith('?'):
                questions[question_num] = sentence
                question_num += 1
        
        return questions
    
    def _clean_question(self, text: str) -> str:
        """
        Clean a single question
        
        Remove:
        - Answer choices (A. B. C. D. E.)
        - "Answer:" sections
        - Multiple choice options
        - Extra whitespace
        - Trailing punctuation
        """
        if not text:
            return ""
        
        # Step 1: Remove "Answer:" and everything after
        text = re.split(r'\s*Answer\s*:', text, flags=re.IGNORECASE)[0]
        
        # Step 2: Remove multiple choice options
        # Pattern 1: "A. text B. text C. text"
        # Find first occurrence of standalone letter option
        match = re.search(r'\s+[A-E]\.\s+[A-Z]', text)
        if match:
            text = text[:match.start()]
        
        # Pattern 2: Options on separate lines
        # Look for pattern: letter + period at start of line
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # If line starts with "A." or "B." etc., it's an option
            if re.match(r'^[A-E]\.\s+', line):
                break  # Stop at first option
            cleaned_lines.append(line)
        
        text = ' '.join(cleaned_lines)
        
        # Step 3: Remove trailing dots and ellipsis
        text = re.sub(r'\.{2,}$', '', text)
        text = re.sub(r'\s*…\s*$', '', text)
        text = text.rstrip('.')
        
        # Step 4: Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Step 5: Remove answer letters at end (e.g., "question? A")
        text = re.sub(r'\s+[A-E]$', '', text)
        
        return text.strip()
    
    def _is_valid_question(self, text: str) -> bool:
        """
        STRICT validation for questions
        
        Valid question must:
        - Be 15-600 characters (adjusted from 10-500)
        - Have 3+ words
        - Not be all caps (headers)
        - Not start with answer choice letter
        - Have meaningful content
        - Have question indicators (Indonesian or English)
        """
        if not text:
            return False
        
        # Length check (more lenient)
        if len(text) < 15 or len(text) > 600:
            logger.debug(f"REJECT: Length {len(text)}")
            return False
        
        # Word count
        words = text.split()
        if len(words) < 3:
            logger.debug(f"REJECT: Only {len(words)} words")
            return False
        
        # Not all caps (but allow some caps for acronyms)
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.6 and len(text) > 20:
            logger.debug(f"REJECT: Too many caps ({caps_ratio:.2f})")
            return False
        
        # Doesn't start with answer choice
        if re.match(r'^[A-E]\.\s', text):
            logger.debug(f"REJECT: Starts with answer choice")
            return False
        
        # Has letters
        letter_count = sum(1 for c in text if c.isalpha())
        if letter_count < 10:
            logger.debug(f"REJECT: Only {letter_count} letters")
            return False
        
        # Not just metadata
        text_lower = text.lower()
        metadata_keywords = ['copyright', 'page', 'halaman', 'header', 'footer']
        if any(kw in text_lower for kw in metadata_keywords):
            logger.debug(f"REJECT: Contains metadata keyword")
            return False
        
        # Must have question indicators (Indonesian OR English)
        has_indicator = any(
            re.search(pattern, text_lower) 
            for pattern in self.question_indicators
        )
        
        # OR ends with question mark
        ends_with_question = text.rstrip().endswith('?')
        
        if not (has_indicator or ends_with_question):
            logger.debug(f"REJECT: No question indicators")
            return False
        
        return True
    
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
            r'^\d+\s+of\s+\d+',
            r'^(?:header|footer|copyright)',
            r'^c\d+\s*-\s*',  # "C1 -", "C2 -" etc.
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
        short_count = sum(1 for q in questions if len(q) < 30)
        
        quality = 'high'
        if avg_length < 40:
            quality = 'medium'
        if avg_length < 25:
            quality = 'low'
        
        # Language detection
        indonesian_count = sum(1 for q in questions if self._is_indonesian(q))
        english_count = len(questions) - indonesian_count
        
        return {
            'valid': True,
            'count': len(questions),
            'avg_length': avg_length,
            'quality': quality,
            'indonesian': indonesian_count,
            'english': english_count,
            'short_questions': short_count
        }
    
    def _is_indonesian(self, text: str) -> bool:
        """Quick check if text is Indonesian"""
        text_lower = text.lower()
        indonesian_words = ['yang', 'adalah', 'dari', 'untuk', 'dengan', 'apa', 'bagaimana']
        return sum(1 for word in indonesian_words if word in text_lower) >= 2


def extract_questions_from_file(file_path: str) -> List[str]:
    """Convenience function"""
    extractor = QuestionExtractor()
    return extractor.extract_questions(file_path)