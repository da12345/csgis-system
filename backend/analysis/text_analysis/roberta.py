import sys
import psycopg2
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
from dotenv import load_dotenv
import sys

load_dotenv(dotenv_path="path/to/env")

model_name = "SamLowe/roberta-base-go_emotions"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

labels = [label for _, label in sorted(model.config.id2label.items())]

def classify_text(model, tokenizer, text, labels, threshold=0.7):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)

    if model.config.problem_type == "multi_label_classification" or outputs.logits.shape[1] > 1:
        probs = torch.sigmoid(outputs.logits)[0]
    else:
        probs = torch.softmax(outputs.logits, dim=1)[0]

    top_idx = torch.argmax(probs).item()
    top_prob = probs[top_idx].item()
    top_label = labels[top_idx]

    return top_label if top_prob >= threshold else None


def ensure_column_exists(cur):
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='combined_sentiment_analysis' AND column_name='roberta_sentiment';
    """)
    if cur.fetchone() is None:
        cur.execute("""
            ALTER TABLE combined_sentiment_analysis ADD COLUMN roberta_sentiment TEXT;
        """)

def analyze_database():
    conn = psycopg2.connect(
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT")
    )
    conn.autocommit = True
    cur = conn.cursor()

    ensure_column_exists(cur)

    cur.execute("""
        SELECT location_id, combined_response
        FROM combined_sentiment_analysis
        WHERE roberta_sentiment IS NULL OR roberta_sentiment = ''
    """)
    rows = cur.fetchall()

    for location_id, text in rows:
        if not text or text.strip() == "":
            continue
        sentiment = classify_text(model, tokenizer, text, labels, threshold=0.7)
        if sentiment is not None:
            cur.execute("""
                UPDATE combined_sentiment_analysis
                SET roberta_sentiment = %s
                WHERE location_id = %s
            """, (sentiment, location_id))

    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        sentiment = classify_text(input_text)
        print(sentiment)
    else:
        analyze_database()
