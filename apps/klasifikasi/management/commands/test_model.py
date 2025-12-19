from django.core.management.base import BaseCommand
from apps.klasifikasi.ml_model import get_classifier  # Changed this line

class Command(BaseCommand):
    help = 'Test the Bloom classifier model'

    def handle(self, *args, **options):
        classifier = get_classifier()
        
        # Test model info
        info = classifier.get_model_info()
        self.stdout.write(self.style.SUCCESS(f"Model info: {info}"))
        
        # Test single prediction
        test_question = "Apa yang dimaksud dengan variabel dalam pemrograman?"
        result = classifier.predict_single(test_question)
        
        self.stdout.write(self.style.SUCCESS(f"\nTest Question: {test_question}"))
        self.stdout.write(self.style.SUCCESS(f"Predicted Category: {result['category']} ({result['category_name']})"))
        self.stdout.write(self.style.SUCCESS(f"Confidence: {result['confidence']:.2%}"))
        
        # Show all probabilities
        self.stdout.write(self.style.SUCCESS("\nAll Category Probabilities:"))
        for category, data in result['all_probabilities'].items():
            self.stdout.write(f"  {category:12s}: {data['probability']:.2%}")