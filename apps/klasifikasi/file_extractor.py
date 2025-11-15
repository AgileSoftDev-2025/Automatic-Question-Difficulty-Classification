# apps/klasifikasi/file_extractor.py - UNIVERSAL VERSION

import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import PyPDF2
from docx import Document

logger = logging.getLogger(__name__)


class QuestionExtractor:
    """Universal question extractor for various file formats and question styles"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt', '.csv']
    
    def extract_questions(self, file_path: str) -> List[str]:
        """Extract questions from file based on extension"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {extension}")
        
        try:
            if extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif extension == '.docx':
                return self._extract_from_docx(file_path)
            elif extension == '.txt':
                return self._extract_from_txt(file_path)
            elif extension == '.csv':
                return self._extract_from_csv(file_path)
        except Exception as e:
            logger.error(f"Error extracting from {file_path}: {str(e)}", exc_info=True)
            raise
    
    def _extract_from_pdf(self, file_path: Path) -> List[str]:
        """Extract text from PDF and parse questions"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                logger.info(f"Extracted {len(full_text)} characters from PDF")
                
                # Auto-detect and clean duplicate text if present
                full_text = self._auto_clean_duplicates(full_text)
                
                questions = self._parse_questions_from_text(full_text)
                return questions
                
        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to read PDF file: {str(e)}")
    
    def _extract_from_docx(self, file_path: Path) -> List[str]:
        """Extract text from DOCX and parse questions"""
        try:
            doc = Document(file_path)
            full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            
            logger.info(f"Extracted {len(full_text)} characters from DOCX")
            questions = self._parse_questions_from_text(full_text)
            return questions
            
        except Exception as e:
            logger.error(f"Error reading DOCX: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to read DOCX file: {str(e)}")
    
    def _extract_from_txt(self, file_path: Path) -> List[str]:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                full_text = file.read()
            
            logger.info(f"Extracted {len(full_text)} characters from TXT")
            questions = self._parse_questions_from_text(full_text)
            return questions
            
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    full_text = file.read()
                questions = self._parse_questions_from_text(full_text)
                return questions
            except Exception as e:
                logger.error(f"Error reading TXT: {str(e)}", exc_info=True)
                raise ValueError(f"Failed to read TXT file: {str(e)}")
        except Exception as e:
            logger.error(f"Error reading TXT: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to read TXT file: {str(e)}")
    
    def _extract_from_csv(self, file_path: Path) -> List[str]:
        """Extract questions from CSV file"""
        try:
            import csv
            questions = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader, None)  # Skip header
                
                for row in csv_reader:
                    if row:
                        question = ' '.join([cell.strip() for cell in row if cell.strip()])
                        if question:
                            question = self._clean_question_text(question)
                            if len(question) > 10:
                                questions.append(question)
            
            logger.info(f"Extracted {len(questions)} questions from CSV")
            return questions
            
        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to read CSV file: {str(e)}")
    
    def _auto_clean_duplicates(self, text: str) -> str:
        """
        Auto-detect and remove duplicate text in documents
        Only applies cleaning if significant duplication is detected
        """
        lines = text.split('\n')
        cleaned_lines = []
        duplicate_count = 0
        total_lines = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append('')
                continue
            
            total_lines += 1
            
            # Check if line contains duplicate text
            is_duplicate, cleaned_line = self._check_and_fix_duplicate_line(line)
            
            if is_duplicate:
                duplicate_count += 1
                cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)
        
        # Only apply cleaning if >30% of lines are duplicated
        if total_lines > 0 and (duplicate_count / total_lines) > 0.3:
            logger.info(f"Detected {duplicate_count}/{total_lines} duplicate lines, applying cleanup")
            return '\n'.join(cleaned_lines)
        
        return text
    
    def _check_and_fix_duplicate_line(self, line: str) -> Tuple[bool, str]:
        """
        Check if a line contains duplicate text and return cleaned version
        Returns: (is_duplicate: bool, cleaned_line: str)
        """
        if len(line) < 20:
            return False, line
        
        # Check if line is duplicated (text appears twice)
        half_len = len(line) // 2
        first_half = line[:half_len]
        second_half = line[half_len:half_len*2]
        
        # If both halves are identical or very similar
        if first_half == second_half:
            return True, first_half
        
        # Check for near-identical (90% similarity)
        if self._similarity(first_half, second_half) > 0.9:
            return True, first_half
        
        return False, line
    
    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate character-level similarity between two strings"""
        if not s1 or not s2:
            return 0.0
        
        matches = sum(c1 == c2 for c1, c2 in zip(s1, s2))
        return matches / max(len(s1), len(s2))
    
    def _parse_questions_from_text(self, text: str) -> List[str]:
        """
        Universal question parser - tries multiple methods and picks best result
        """
        text = text.strip()
        
        # Try different parsing strategies
        methods = [
            ('numbered_with_answers', self._extract_numbered_with_answers),
            ('numbered_simple', self._extract_numbered_simple),
            ('question_marks', self._extract_by_question_marks),
            ('paragraphs', self._extract_by_paragraphs),
        ]
        
        best_questions = []
        best_score = 0
        
        for method_name, method_func in methods:
            try:
                questions = method_func(text)
                score = self._score_extraction_quality(questions)
                
                logger.debug(f"Method '{method_name}': {len(questions)} questions, score: {score:.2f}")
                
                if score > best_score:
                    best_score = score
                    best_questions = questions
            except Exception as e:
                logger.warning(f"Method '{method_name}' failed: {e}")
        
        if best_questions:
            logger.info(f"Best extraction: {len(best_questions)} questions using score {best_score:.2f}")
            return best_questions
        
        logger.warning("No questions could be extracted from text")
        return []
    
    def _extract_numbered_with_answers(self, text: str) -> List[str]:
        """
        Extract numbered questions that may have answer choices
        Format: "1. Question text A. answer B. answer"
        """
        questions = []
        seen = set()
        
        # Pattern: number, dot/paren, question text until next number or answer section
        pattern = r'(\d+)[\.\)]\s*(.+?)(?=\n\s*\d+[\.\)]|\n\s*Jawaban|\n\s*Answer|$)'
        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            question_block = match.group(2).strip()
            
            # Remove answer choices
            question_only = self._remove_answer_choices(question_block)
            question_only = self._clean_question_text(question_only)
            
            if len(question_only) > 15 and question_only.lower() not in seen:
                questions.append(question_only)
                seen.add(question_only.lower())
        
        return questions
    
    def _extract_numbered_simple(self, text: str) -> List[str]:
        """
        Extract simple numbered questions without answer choices
        Format: "1. Question text\n2. Question text"
        """
        questions = []
        seen = set()
        
        lines = text.split('\n')
        current_question = ""
        
        for line in lines:
            line = line.strip()
            
            # New numbered question
            if re.match(r'^\d+[\.\)]\s+', line):
                # Save previous question
                if current_question:
                    cleaned = self._clean_question_text(current_question)
                    if len(cleaned) > 15 and cleaned.lower() not in seen:
                        questions.append(cleaned)
                        seen.add(cleaned.lower())
                
                # Start new question (remove number)
                current_question = re.sub(r'^\d+[\.\)]\s+', '', line)
            
            # Continue current question (not an answer choice)
            elif current_question and line and not re.match(r'^[A-E][\.\)]', line, re.IGNORECASE):
                if not self._is_header_or_footer(line):
                    current_question += " " + line
        
        # Add last question
        if current_question:
            cleaned = self._clean_question_text(current_question)
            if len(cleaned) > 15 and cleaned.lower() not in seen:
                questions.append(cleaned)
        
        return questions
    
    def _extract_by_question_marks(self, text: str) -> List[str]:
        """
        Extract questions ending with question marks
        Format: "What is X? How does Y?"
        """
        questions = []
        seen = set()
        
        # Split by sentences ending with ?
        pattern = r'([^.!?\n]+\?)'
        matches = re.findall(pattern, text)
        
        for match in matches:
            question = self._clean_question_text(match)
            if len(question) > 15 and question.lower() not in seen:
                questions.append(question)
                seen.add(question.lower())
        
        return questions
    
    def _extract_by_paragraphs(self, text: str) -> List[str]:
        """
        Extract questions by paragraphs
        Useful for essays or open-ended questions
        """
        questions = []
        seen = set()
        
        # Split by double newlines
        paragraphs = re.split(r'\n\s*\n+', text)
        
        for para in paragraphs:
            para = para.strip()
            
            # Remove leading numbers
            para = re.sub(r'^\d+[\.\)]\s*', '', para)
            
            # Clean
            para = self._clean_question_text(para)
            
            # Validate
            if (len(para) > 20 and 
                len(para) < 500 and 
                not self._is_header_or_footer(para) and
                para.lower() not in seen):
                questions.append(para)
                seen.add(para.lower())
        
        return questions
    
    def _remove_answer_choices(self, text: str) -> str:
        """
        Remove answer choices from question text
        Handles multiple formats: A. answer, A) answer, a. answer
        """
        # Split at first answer choice
        patterns = [
            r'\n\s*[A-E][\.\)]',  # Newline + A.
            r'\s+[A-E][\.\)]\s+',  # Space + A. + space
        ]
        
        question = text
        for pattern in patterns:
            parts = re.split(pattern, question, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) > 1:
                question = parts[0]
                break
        
        # Remove answer/jawaban sections
        question = re.sub(r'Jawaban\s*:.*$', '', question, flags=re.IGNORECASE | re.DOTALL)
        question = re.sub(r'Answer\s*:.*$', '', question, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove trailing ellipsis
        question = re.sub(r'\.{2,}$', '', question)
        
        return question.strip()
    
    def _clean_question_text(self, text: str) -> str:
        """Clean and normalize question text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading numbers if present
        text = re.sub(r'^\d+[\.\)]\s*', '', text)
        
        # Trim
        text = text.strip()
        
        # Remove trailing punctuation except ? and )
        text = re.sub(r'[^\w\s\?\)\]]+$', '', text)
        
        return text
    
    def _is_header_or_footer(self, line: str) -> bool:
        """Check if line is likely a header/footer/metadata"""
        line_lower = line.lower()
        
        # Page numbers, headers, etc.
        patterns = [
            r'^\d+$',
            r'^page\s+\d+',
            r'^\d+\s*/\s*\d+$',
            r'^[A-Z\s]{5,}$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # Common header/footer words
        markers = ['header', 'footer', 'copyright', '©', 'page', 'nama:', 'kelas:']
        if any(marker in line_lower for marker in markers):
            return True
        
        # Very short lines
        if len(line) < 5:
            return True
        
        return False
    
    def _score_extraction_quality(self, questions: List[str]) -> float:
        """
        Score the quality of extracted questions
        Higher score = better extraction
        """
        if not questions:
            return 0.0
        
        score = 0.0
        
        # Reward number of questions (up to a point)
        score += min(len(questions) / 10, 5.0)
        
        # Reward appropriate question length
        avg_length = sum(len(q) for q in questions) / len(questions)
        if 30 <= avg_length <= 200:
            score += 3.0
        elif 20 <= avg_length <= 300:
            score += 1.5
        
        # Reward variety in length (not all same length)
        lengths = [len(q) for q in questions]
        if len(set(lengths)) > len(questions) * 0.5:
            score += 2.0
        
        # Penalize very short or very long questions
        too_short = sum(1 for q in questions if len(q) < 15)
        too_long = sum(1 for q in questions if len(q) > 500)
        score -= (too_short + too_long) * 0.5
        
        # Reward questions with question words
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which',
                         'apa', 'bagaimana', 'mengapa', 'kapan', 'dimana', 'siapa']
        questions_with_words = sum(
            1 for q in questions 
            if any(word in q.lower() for word in question_words)
        )
        score += (questions_with_words / len(questions)) * 2.0
        
        return max(score, 0.0)
    
    def validate_questions(self, questions: List[str]) -> Dict:
        """Validate extracted questions"""
        if not questions:
            return {
                'valid': False,
                'error': 'No questions found in file',
                'count': 0
            }
        
        if len(questions) < 3:
            return {
                'valid': False,
                'error': f'Too few questions found ({len(questions)}). Minimum 3 required.',
                'count': len(questions)
            }
        
        # Check if questions are too short
        short_questions = [q for q in questions if len(q) < 10]
        if len(short_questions) > len(questions) * 0.5:
            return {
                'valid': False,
                'error': 'Many questions appear too short. Please check file format.',
                'count': len(questions)
            }
        
        return {
            'valid': True,
            'count': len(questions),
            'avg_length': sum(len(q) for q in questions) / len(questions)
        }


def extract_questions_from_file(file_path: str) -> List[str]:
    """
    Convenience function to extract questions from file
    
    Args:
        file_path: Path to file
        
    Returns:
        List of question strings
    """
    extractor = QuestionExtractor()
    return extractor.extract_questions(file_path)