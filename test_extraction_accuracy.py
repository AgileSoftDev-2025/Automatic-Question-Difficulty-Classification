#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script untuk mengukur akurasi ekstraksi soal
Gunakan dengan: python test_extraction_accuracy.py <pdf_path>
"""

import sys
import logging
from pathlib import Path
from apps.klasifikasi.file_extractor import QuestionExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_extraction(file_path):
    """Test ekstraksi dan tampilkan statistik"""
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ File tidak ditemukan: {file_path}")
        return
    
    print(f"\n{'='*70}")
    print(f"📄 Testing Extraction: {file_path.name}")
    print(f"{'='*70}\n")
    
    try:
        extractor = QuestionExtractor()
        questions = extractor.extract_questions(str(file_path))
        
        # Validation
        validation = extractor.validate_questions(questions)
        
        # Display results
        print(f"✅ Extraction Results:")
        print(f"   Total Questions Extracted: {len(questions)}")
        print(f"   Validation Status: {validation['valid']}")
        print(f"   Average Length: {validation.get('avg_length', 0):.0f} chars")
        print(f"   Quality: {validation.get('quality', 'unknown')}")
        
        # If 100 expected, calculate accuracy
        if len(questions) >= 88:
            accuracy = (len(questions) / 100) * 100
            print(f"\n📊 Accuracy: {accuracy:.1f}% ({len(questions)}/100)")
            
            if len(questions) >= 90:
                print(f"✅ TARGET ACHIEVED! ≥ 90% accuracy reached!")
            else:
                print(f"⚠️  Still below 90%. Missing ~{100 - len(questions)} questions.")
        else:
            print(f"\n⚠️  Only {len(questions)} questions extracted (target: 90+)")
        
        # Display first 5 and last 5 questions
        print(f"\n📋 First 5 Questions:")
        for i, q in enumerate(questions[:5], 1):
            print(f"   {i}. {q[:70]}{'...' if len(q) > 70 else ''}")
        
        print(f"\n📋 Last 5 Questions:")
        for i, q in enumerate(questions[-5:], len(questions)-4):
            print(f"   {i}. {q[:70]}{'...' if len(q) > 70 else ''}")
        
        print(f"\n{'='*70}\n")
        
        return questions
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_extraction_accuracy.py <pdf_path>")
        print("\nExample:")
        print("  python test_extraction_accuracy.py 'soal soal audit.pdf'")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    test_extraction(pdf_path)
