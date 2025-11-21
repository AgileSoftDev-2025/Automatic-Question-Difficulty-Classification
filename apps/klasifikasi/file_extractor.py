# apps/klasifikasi/file_extractor.py - FIXED: Better cleaning

import re
import logging
from pathlib import Path
from typing import List, Dict
from collections import OrderedDict

logger = logging.getLogger(__name__)

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
    ULTRA-AGGRESSIVE question extractor with IMPROVED CLEANING
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt', '.doc']
        
    def extract_questions(self, file_path: str) -> List[str]:
        """Extract questions with ZERO TOLERANCE for duplicates"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {extension}")
        
        try:
            logger.info(f"=== EXTRACTING FROM {file_path.name} ===")
            
            # Step 1: Get raw text
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
                    logger.warning(f"Q{num} REJECTED (len={len(question) if question else 0})")
            
            # === NEW: Post-processing to catch edge cases ===
            # Sometimes questions are split or merged incorrectly
            final_questions = self._post_process_questions(final_questions)
            
            logger.info(f"=== EXTRACTED {len(final_questions)} VALID QUESTIONS (after post-processing) ===")
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
        """NUCLEAR DEDUPLICATION - IMPROVED to preserve question separation"""
        lines = text.split('\n')
        
        # Step 1: Remove exact consecutive duplicates but PRESERVE spacing before content
        cleaned = []
        prev_line = None
        
        for line in lines:
            original_line = line
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
            
            # Skip metadata
            if self._is_metadata(line_stripped):
                continue
            
            # Skip if exact duplicate of previous
            if prev_line and line_stripped == prev_line:
                logger.debug(f"SKIP EXACT DUP: {line_stripped[:50]}")
                continue
            
            # Skip if 90%+ similar to previous (fuzzy duplicate)
            if prev_line and self._similarity(line_stripped, prev_line) > 0.90:
                logger.debug(f"SKIP FUZZY DUP: {line_stripped[:50]}")
                continue
            
            cleaned.append(line_stripped)  # Store stripped version for comparison
            prev_line = line_stripped
        
        # Step 2: Join with SINGLE SPACE (not multiple spaces)
        # This prevents "93.    Which" from becoming problematic
        full_text = " ".join(cleaned)
        
        # Step 3: Normalize whitespace BUT preserve the "NUMBER. " pattern
        # Split by number pattern, preserve numbers, clean spaces
        parts = re.split(r'(\d+\.)', full_text)
        result = []
        
        for i, part in enumerate(parts):
            if re.match(r'^\d+\.$', part):
                # It's a number - keep it
                result.append(part)
            else:
                # It's content - normalize but keep structure
                part = re.sub(r'\s+', ' ', part)  # Normalize multiple spaces to single
                result.append(part)
        
        full_text = " ".join(result)
        
        # Step 4: Remove "Jawaban:" sections entirely
        full_text = re.sub(r'Jawaban:\s*[A-E]\.\s+[^\d]+(?=\d+\.|\Z)', '', full_text, flags=re.IGNORECASE)
        
        # Step 5: Clean up double spaces created by joining
        full_text = re.sub(r'\s+', ' ', full_text)
        
        return full_text.strip()
    
    def _is_metadata(self, line: str) -> bool:
        """Check if line is metadata/header/footer"""
        line_lower = line.lower().strip()
        
        # FIXED: "1." is a valid question number, NOT metadata!
        # Only skip very short lines that are NOT question numbers
        if len(line) < 1:  # Only skip completely empty
            return True
        
        # DON'T skip single digits or "digit." - these are question numbers!
        # Skip only if it's JUST a bare number without dot
        if re.match(r'^[0-9]+$', line):  # "1", "12", "100" without dot
            return True
        
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
        t1 = re.sub(r'[^\w\s]', '', text1.lower())
        t2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        if not t1 or not t2:
            return 0.0
        
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_numbered_questions(self, text: str) -> Dict[int, str]:
        """Extract questions by number (1., 2., 3., etc.) - ULTRA-IMPROVED v3"""
        questions = OrderedDict()
        
        # === MULTI-PASS EXTRACTION ===
        # Pass 1: Standard pattern (1. Question text 2. Question text)
        questions.update(self._extract_by_pattern(text, r'(\d+)\.\s+'))
        
        # Pass 2: Alternative pattern with numbers at line start (formatting variant)
        if len(questions) < 95:
            alt_questions = self._extract_by_pattern(text, r'^\s*(\d+)\.\s+', multiline=True)
            for num, content in alt_questions.items():
                if num not in questions:
                    questions[num] = content
        
        # Pass 3: Look for outlier numbers (e.g., 93-100 if we only got 1-92)
        if len(questions) < 95:
            missing = self._find_missing_numbers(text, questions)
            questions.update(missing)
        
        # Check for large gaps and recover
        if questions:
            sorted_nums = sorted(questions.keys())
            max_num = sorted_nums[-1] if sorted_nums else 0
            
            if len(questions) < max_num * 0.88:
                logger.info(f"Gap detected: found {len(questions)} of {max_num} expected. Attempting recovery...")
                questions = self._recover_missing_questions(text, questions, max_num)
        
        return questions
    
    def _extract_by_pattern(self, text: str, pattern: str, multiline: bool = False) -> Dict[int, str]:
        """Extract questions using a specific regex pattern - IMPROVED for single/double digits"""
        flags = re.MULTILINE if multiline else 0
        
        # First, let's do a more robust extraction that handles both single and double digit numbers
        # Pattern explanation:
        # - (\d+)\. matches: 1. 2. ... 99. 100.
        # - (?=\s) ensures there's whitespace after the dot (lookahead)
        robust_pattern = r'(\d+)\.\s+'
        
        # Split text
        parts = re.split(robust_pattern, text, flags=flags)
        
        questions = OrderedDict()
        current_num = None
        
        for i, part in enumerate(parts):
            part = part.strip()
            
            if not part:
                continue
            
            # Check if this is a number (should be every other element after split)
            if re.match(r'^\d+$', part):
                current_num = int(part)
            elif current_num is not None:
                # This is the content following the number
                # FIXED: If we already have this question number, keep the LONGER version
                # (some question numbers might appear multiple times in text, e.g., "2." in Q2 and in Q92)
                if current_num not in questions or len(part) > len(questions[current_num]):
                    questions[current_num] = part
                current_num = None
        
        return questions
    
    def _find_missing_numbers(self, text: str, questions: Dict[int, str]) -> Dict[int, str]:
        """Find questions that might be at end of document with different spacing"""
        found = OrderedDict()
        
        # Look for high-numbered questions (e.g., 93-100) that might have weird formatting
        # Pattern: NUMBER. [possibly more spaces/newlines] TEXT starting with capital
        pattern = r'(\d{2,})\s*\.\s*([A-Z][^\n]*(?:\n(?!\d+\s*\.).*)*)'  
        
        for match in re.finditer(pattern, text):
            num = int(match.group(1))
            content = match.group(2).strip()
            
            # Only add if:
            # 1. Number not already found
            # 2. Content is substantial (> 20 chars)
            if num not in questions and len(content) > 20:
                current_max = max(questions.keys()) if questions else 0
                
                # Add if it's beyond what we have or if it's high-numbered
                if num > current_max or num > 80:
                    found[num] = content
                    logger.debug(f"Found outlier question {num}")
        
        return found
    
    def _recover_missing_questions(self, text: str, questions: Dict[int, str], expected_max: int) -> Dict[int, str]:
        """Try to recover missing questions by looking for edge cases"""
        # Look for questions that might have been missed due to formatting
        
        # Pattern 1: Questions with extra spacing/newlines
        alt_pattern = r'(\d+)\s*\.\s*\n+\s*'
        parts = re.split(alt_pattern, text)
        
        recovered = OrderedDict()
        current_num = None
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            if re.match(r'^\d+$', part):
                current_num = int(part)
            elif current_num is not None and current_num not in questions:
                recovered[current_num] = part
                current_num = None
        
        # Merge with original questions
        result = OrderedDict(questions)
        result.update(recovered)
        
        if recovered:
            logger.info(f"Recovered {len(recovered)} additional questions")
        
        return result
    
    def _post_process_questions(self, questions: List[str]) -> List[str]:
        """Post-process questions to catch edge cases and improve accuracy"""
        processed = []
        
        for i, q in enumerate(questions):
            # Skip if already processed
            if not q:
                continue
            
            # Check for accidentally merged questions (two questions in one)
            # Usually indicated by patterns like "...A. ... B. ..." or "...? ... Pertanyaan..."
            if self._seems_merged(q):
                split_questions = self._attempt_split_merged(q)
                processed.extend(split_questions)
                logger.debug(f"Split merged question into {len(split_questions)} questions")
            else:
                processed.append(q)
        
        return processed
    
    def _seems_merged(self, text: str) -> bool:
        """Detect if text seems to contain two questions merged together"""
        # Count question-ending patterns
        ends = len(re.findall(r'[?!]\s+[A-Z]', text))
        
        # If we see patterns like "? A." suggesting two Q's merged, it's likely merged
        return ends > 0
    
    def _attempt_split_merged(self, text: str) -> List[str]:
        """Attempt to split a merged question back into components"""
        # Split on patterns like "? " followed by capital letter (potential start of next question)
        parts = re.split(r'([?!])\s+(?=[A-Z])', text)
        
        result = []
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                # Combine text + punctuation
                segment = (parts[i] + parts[i + 1]).strip()
            else:
                segment = parts[i].strip()
            
            if segment and self._is_valid_question(segment):
                result.append(segment)
        
        # If splitting didn't help, return original
        return result if result else [text]
    
    def _clean_question(self, text: str) -> str:
        """
        Clean a single question block - IMPROVED v2
        
        Enhancements:
        - Better removal of multi-line answer blocks
        - Handle roman numerals and bullet points within questions
        - Better detection of where question ends
        - Preserve legitimate multi-line questions
        """
        # Remove "Jawaban:" and everything after (most aggressive)
        text = re.split(r'(?:jawaban|answer|pilihan|options?)\s*:', text, flags=re.IGNORECASE)[0]
        
        # Remove answer choices (A-E, potentially with explanations)
        # Match patterns like: "A. answer text" or "A) answer text"
        text = re.sub(r'\s+[A-E][.)]\s+[^\n]*(?:\n[^\d].*?)*', '', text, flags=re.MULTILINE)
        
        # Find first answer choice indicator and cut
        match = re.search(r'\b[A-E][.)]\s+', text)
        if match:
            text = text[:match.start()]
        
        # Remove common footer/metadata patterns
        text = re.sub(r'(?:^|\n)\s*(?:halaman|page)\s*\d+.*?$', '', text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r'(?:^|\n)\s*(?:©|copyright).*?$', '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # === IMPROVED: More aggressive dot/space removal ===
        # Remove trailing ". ." or ". . ." or multiple dots/spaces
        text = re.sub(r'[\.\s]*[\.\s]+[\.\s]*$', '', text)
        text = re.sub(r'\s+\.+\s*$', '', text)
        
        # Remove ellipsis patterns (including unicode)
        text = re.sub(r'\s*[…\.]{2,}\s*$', '', text)
        
        # Final cleanup: remove any remaining trailing punctuation
        text = text.rstrip('.').rstrip(';').rstrip(',').rstrip()
        
        # Normalize internal whitespace but preserve line breaks if legitimate
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # Remove lines that are clearly not part of the question
        cleaned_lines = []
        for line in lines:
            # Skip metadata
            if any(x in line.lower() for x in ['page', 'halaman', 'copyright', '©']):
                continue
            # Skip answer indicators at line start
            if re.match(r'^[A-E][.)]\s', line):
                continue
            cleaned_lines.append(line)
        
        text = ' '.join(cleaned_lines)
        
        # Final normalization
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _is_valid_question(self, text: str) -> bool:
        """Strict validation - IMPROVED v3 (more lenient for edge cases)"""
        if not text:
            return False
        
        # Length check - more lenient for multi-line questions
        if len(text) < 8 or len(text) > 1000:  # Increased max to 1000 for complex questions
            return False
        
        # Word count - allow for shorter legitimate questions
        words = text.split()
        if len(words) < 2:  # Reduced from 3 to 2 to catch shorter questions
            return False
        
        # Not all caps (but allow mixed case)
        if text.isupper() and len(text) > 15:
            return False
        
        # Doesn't start with answer choice
        if re.match(r'^[A-E][.)\]]\s', text):
            return False
        
        # Has letters (at least 3)
        if sum(1 for c in text if c.isalpha()) < 3:  # Reduced from 5 to 3
            return False
        
        # Not just metadata
        if any(kw in text.lower() for kw in ['copyright', 'header', 'footer']):
            return False
        
        # Additional: avoid page number remnants
        if re.match(r'^page\s+\d+', text.lower()) or re.match(r'^\d+\s+of\s+\d+', text.lower()):
            return False
        
        # Additional: avoid lines that are just headers or chapter titles
        if len(text) < 15 and text.isupper():
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

    def parse_question_and_answers(self, question_text: str) -> dict:
        """
        Parse question text to separate question stem from answer choices.
        
        Returns:
            dict: {
                'question': str (the question without answers),
                'answers': list of dict [{'choice': 'a', 'text': '...'}, ...],
                'is_multiple_choice': bool
            }
        """
        # Pattern to match answer choices: a. ... b. ... c. ... d. ...
        # Also handle variations like "a) ...", "a) ....", etc.
        
        lines = question_text.split('\n')
        
        # Find where answers start (looking for pattern like "a.", "a)", etc.)
        answer_pattern = r'^[a-d]\s*[\.\)]\s*'
        answer_start_idx = -1
        
        for i, line in enumerate(lines):
            if re.match(answer_pattern, line.strip()):
                answer_start_idx = i
                break
        
        # If no clear answer pattern found, try inline detection
        if answer_start_idx == -1:
            # Look for inline pattern in full text: "a. ... b. ... c. ... d."
            inline_pattern = r'\s[a-d]\.\s+[^a-d]{5,}'
            if re.search(inline_pattern, question_text):
                # Text has inline answers - try to split
                answer_match = re.search(r'\s+a[\.\)]\s+', question_text)
                if answer_match:
                    split_pos = answer_match.start()
                    question_part = question_text[:split_pos].strip()
                    answers_part = question_text[split_pos:].strip()
                    
                    answers = []
                    answer_blocks = re.findall(r'[a-d][\.\)]\s*([^a-d]*?)(?=[a-d][\.\)]|$)', answers_part)
                    
                    for i, block in enumerate(answer_blocks):
                        choice = chr(ord('a') + i)
                        answers.append({
                            'choice': choice,
                            'text': block.strip()
                        })
                    
                    return {
                        'question': question_part,
                        'answers': answers,
                        'is_multiple_choice': len(answers) >= 2
                    }
        else:
            # Split at answer start
            question_part = '\n'.join(lines[:answer_start_idx]).strip()
            answers_part = '\n'.join(lines[answer_start_idx:]).strip()
            
            answers = []
            choice_pattern = r'^[a-d]\s*[\.\)]\s*(.+?)$'
            
            for line in answers_part.split('\n'):
                line = line.strip()
                match = re.match(choice_pattern, line)
                if match:
                    choice = line[0]
                    text = match.group(1)
                    answers.append({
                        'choice': choice,
                        'text': text
                    })
            
            return {
                'question': question_part,
                'answers': answers,
                'is_multiple_choice': len(answers) >= 2
            }
        
        # No answer choices found - return full text as question
        return {
            'question': question_text,
            'answers': [],
            'is_multiple_choice': False
        }

    def extract_question_stem_only(self, question_text: str) -> str:
        """
        Extract ONLY the question stem (without answer choices).
        Removes all a., b., c., d. options.
        
        Returns:
            str: Clean question text without any answer choices
        """
        parsed = self.parse_question_and_answers(question_text)
        return parsed['question']


def extract_questions_from_file(file_path: str) -> List[str]:
    """Convenience function"""
    extractor = QuestionExtractor()
    return extractor.extract_questions(file_path)