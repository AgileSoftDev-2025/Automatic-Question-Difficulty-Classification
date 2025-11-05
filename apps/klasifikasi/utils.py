import os
import re

def extract_questions_from_text(text):
    """
    Extract questions from text using simple heuristics:
    - Split by numbers followed by dot/parenthesis
    - Split by newlines with empty lines
    - Filter out very short lines
    """
    # Clean the text first
    text = text.replace('\r', '\n')
    text = re.sub(r'\n\s+\n', '\n\n', text)
    
    # Try to split by numbered items first (e.g., "1.", "1)", "(1)")
    questions = re.split(r'\n\s*\d+[\.\)\]]\s*', text)
    
    if len(questions) <= 1:
        # If no numbered items found, try splitting by double newlines
        questions = [q.strip() for q in text.split('\n\n')]
    
    # Filter and clean the questions
    filtered_questions = []
    for q in questions:
        q = q.strip()
        # Only keep questions that are reasonable length and look like sentences
        if len(q) > 20 and any(q.endswith(x) for x in '.!?'):
            filtered_questions.append(q)
    
    return filtered_questions

def read_text_file(file_path):
    """Read content from .txt file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_csv_file(file_path):
    """Read content from .csv file - assuming questions are in rows"""
    questions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                questions.append(line)
    return '\n\n'.join(questions)

def read_file_content(file_path):
    """
    Read file content based on extension.
    Returns the text content of the file.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.txt':
        return read_text_file(file_path)
    elif ext == '.csv':
        return read_csv_file(file_path)
    else:
        # For unsupported formats, try reading as text
        try:
            return read_text_file(file_path)
        except UnicodeDecodeError:
            raise ValueError(f"Unsupported file format or binary file: {ext}")

def process_file(file_path):
    """
    Process a file and extract questions.
    Returns a list of questions found in the file.
    """
    try:
        content = read_file_content(file_path)
        questions = extract_questions_from_text(content)
        return questions
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return []