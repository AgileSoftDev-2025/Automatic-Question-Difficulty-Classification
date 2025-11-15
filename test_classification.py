# test_classification.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bloomers.settings')
django.setup()

from apps.klasifikasi.file_extractor import extract_questions_from_file
from apps.klasifikasi.ml_model import classify_questions_batch
from django.conf import settings

# Extract questions
test_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'test_questions.txt')
questions = extract_questions_from_file(test_file_path)

print(f"✅ Extracted {len(questions)} questions\n")

# Classify
predictions = classify_questions_batch(questions, translate=True, batch_size=8)

print("=" * 70)
print("CLASSIFICATION RESULTS")
print("=" * 70)

for i, (q, pred) in enumerate(zip(questions, predictions), 1):
    print(f"\n{i}. Question:")
    print(f"   {q}")
    print(f"   📊 Category: {pred['category']} ({pred['category_name']})")
    print(f"   💯 Confidence: {pred['confidence']*100:.1f}%")

print("\n" + "=" * 70)
print(f"✅ Successfully classified {len(predictions)} questions!")