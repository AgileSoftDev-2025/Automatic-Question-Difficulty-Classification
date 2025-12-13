"""
Question Regeneration Module
============================

Module untuk mentransformasi/regenerasi soal di berbagai tingkat Bloom's Taxonomy (C1-C6).

Components:
-----------
1. regenerate_utils.py - Main utility module dengan QuestionRegenerator class
2. regenerate_t5_lora/ - Direktori berisi pre-trained T5 model dengan LoRA adapters
3. regenerate_train_script.py - Script untuk fine-tuning model (referensi)
4. regenerate_test_script.py - Script untuk testing model (referensi)
5. regenerate_training_data.csv - Sample dataset untuk training

Penggunaan:
-----------
from .regenerate_utils import regenerate_question

result = regenerate_question(
    question="Apa itu fotosintesis?",  # C1 question
    source_level="C1",
    target_level="C3"
)

# Result: {
#     'success': True,
#     'original': 'Apa itu fotosintesis?',
#     'transformed': 'Bagaimana cara menerapkan konsep fotosintesis...',
#     'source_level': 'C1',
#     'target_level': 'C3',
#     'error': None
# }

Model Architecture:
-------------------
- Base Model: T5-Small
- Fine-tuning: LoRA (Low-Rank Adaptation)
- Inference: Beam search (num_beams=4)
- Input Format: "transform {source_level} to {target_level}: {question}"

Bloom's Taxonomy Levels:
-----------------------
- C1 (Remember): Recall facts and basic concepts
- C2 (Understand): Explain ideas or concepts
- C3 (Apply): Use information in new situations
- C4 (Analyze): Draw connections among ideas
- C5 (Evaluate): Justify a decision or course of action
- C6 (Create): Produce new or original work
"""
