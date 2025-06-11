import sys
import psycopg2
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

model_name = "joeddav/distilbert-base-uncased-go-emotions-student"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

from dotenv import load_dotenv

load_dotenv(dotenv_path="path/to/env")

labels = [label for _, label in sorted(model.config.id2label.items())]

def predict_sentiment(text, threshold=0.8):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.sigmoid(outputs.logits)[0]
    top_idx = torch.argmax(probs).item()
    top_prob = probs[top_idx].item()

    if top_prob >= threshold:
        return labels[top_idx]
    else:
        return None

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

    cur.execute("""
        SELECT location_id, combined_response
        FROM combined_sentiment_analysis
        WHERE bert_sentiment IS NULL OR bert_sentiment = ''
    """)
    rows = cur.fetchall()

    for id, text in rows:
        if not text:
            continue
        sentiment = predict_sentiment(text)
        if sentiment is not None:
            cur.execute("""
                UPDATE combined_sentiment_analysis
                SET bert_sentiment = %s
                WHERE location_id = %s
            """, (sentiment, id))

    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        sentiment = predict_sentiment(input_text)
        print(sentiment)
    else:
        analyze_database()
