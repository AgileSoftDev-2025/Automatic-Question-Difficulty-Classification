import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import sigmoid

# Label dan threshold
LABEL_COLUMNS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
THRESHOLD = 0.5
MODEL_PATH = "."

def predict_text(text):
    # Load tokenizer dan model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

    # Tokenisasi input
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

    # Prediksi
    with torch.no_grad():
        outputs = model(**inputs)
        probs = sigmoid(outputs.logits).numpy()[0]

    # Konversi hasil ke dict
    results = {}
    for label, prob in zip(LABEL_COLUMNS, probs):
        results[label] = {
            "probability": float(prob),
            "predicted": prob >= THRESHOLD
        }

    return results


if __name__ == "__main__":
    # Coba prediksi
    sample = " Assess and synthesise diverse information about information and knowledge management technologies market and how to use implementation strategies to maximise their strengths and minimise their weaknesses."
    prediction = predict_text(sample)

    print("\n=== HASIL PREDIKSI ===")
    for label, info in prediction.items():
        status = "✅" if info["predicted"] else "❌"
        print(f"{label:10s} → {status} (prob={info['probability']:.3f})")
