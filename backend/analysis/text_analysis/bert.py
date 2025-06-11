from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch, os, psycopg2
from dotenv import load_dotenv
import sys

load_dotenv("path/to/env")

model_name = "monologg/bert-base-cased-goemotions-original"
tokenizer   = AutoTokenizer.from_pretrained(model_name)
model       = AutoModelForSequenceClassification.from_pretrained(model_name)

labels = [label for _, label in sorted(model.config.id2label.items())]
def classify_text(model, tokenizer, text, labels, threshold=0.7):
    """Return top label if its confidence ≥ threshold, else None."""
    inputs  = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)

    if model.config.problem_type == "multi_label_classification" \
       or outputs.logits.shape[1] > 1:
        probs = torch.sigmoid(outputs.logits)[0]      # multi-label
    else:
        probs = torch.softmax(outputs.logits, dim=1)[0]  # single-label

    top_idx   = torch.argmax(probs).item()
    top_prob  = probs[top_idx].item()
    top_label = labels[top_idx]

    return top_label if top_prob >= threshold else None

def analyze_database():
    conn = psycopg2.connect(
        dbname   = os.getenv("DATABASE_NAME"),
        user     = os.getenv("DATABASE_USER"),
        password = os.getenv("DATABASE_PASSWORD"),
        host     = os.getenv("DATABASE_HOST"),
        port     = os.getenv("DATABASE_PORT")
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("""
        SELECT location_id, combined_response
        FROM combined_sentiment_analysis
        WHERE bert_sentiment IS NULL OR bert_sentiment = ''
    """)
    rows = cur.fetchall()

    for loc_id, text in rows:
        if not text or not text.strip():
            continue
        sentiment = classify_text(model, tokenizer, text, labels, threshold=0.7)
        if sentiment:
            cur.execute("""
                UPDATE combined_sentiment_analysis
                SET bert_sentiment = %s
                WHERE location_id  = %s
            """, (sentiment, loc_id))

    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        top_label  = classify_text(model, tokenizer, input_text, labels, threshold=0.7)
        print(f"Top emotion: {top_label}")
    else:
        analyze_database()
