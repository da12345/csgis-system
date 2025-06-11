import sys
import psycopg2
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="path/to/env")

model_name = "joeddav/distilbert-base-uncased-go-emotions-student"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

goemotions_labels = [label for _, label in sorted(model.config.id2label.items())]

goemotions_to_ekman = {
    # JOY
    "admiration": "joy",
    "amusement": "joy",
    "desire": "joy",
    "excitement": "joy",
    "joy": "joy",
    "love": "joy",
    "pride": "joy",
    "approval": "joy",
    "caring": "joy",
    "curiosity": "joy",
    "gratitude": "joy",
    "optimism": "joy",

    # NEUTRAL
    "neutral": "neutral",
    "realization": "neutral",
    "relief": "neutral",
    "confusion": "neutral",
    "disappointment": "neutral",

    # SADNESS
    "embarrassment": "sadness",
    "grief": "sadness",
    "remorse": "sadness",
    "sadness": "sadness",

    # FEAR
    "fear": "fear",
    "nervousness": "fear",

    # SURPRISE
    "surprise": "surprise",

    # ANGER
    "anger": "anger",
    "annoyance": "anger",
    "disapproval": "anger",

    # DISGUST
    "disgust": "disgust"
}

def predict_sentiment(text, threshold=0.1):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits[0]

    if model.config.problem_type == "multi_label_classification":
        probs = torch.sigmoid(logits)
    else:
        probs = torch.softmax(logits, dim=0)

    label_scores = {goemotions_labels[i]: float(probs[i]) for i in range(len(goemotions_labels)) if probs[i] >= threshold}
    if not label_scores:
        return None

    ekman_scores = {}
    for label, score in label_scores.items():
        ekman = goemotions_to_ekman.get(label)
        if ekman:
            ekman_scores[ekman] = ekman_scores.get(ekman, 0.0) + score

    return max(ekman_scores.items(), key=lambda x: x[1])[0] if ekman_scores else None

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
        WHERE distilbert_ekman_sentiment IS NULL OR distilbert_ekman_sentiment = ''
    """)
    rows = cur.fetchall()

    for id, text in rows:
        if not text or not text.strip():
            continue
        sentiment = predict_sentiment(text)
        if sentiment is not None:
            cur.execute("""
                UPDATE combined_sentiment_analysis
                SET distilbert_ekman_sentiment = %s
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
