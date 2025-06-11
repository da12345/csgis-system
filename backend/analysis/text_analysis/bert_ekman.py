from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
import psycopg2
import numpy as np
from dotenv import load_dotenv

load_dotenv(dotenv_path="path/to/env")

model_name = "monologg/bert-base-cased-goemotions-original"
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

final_labels = ['joy', 'anger', 'sadness', 'fear', 'disgust', 'surprise', 'neutral']

def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1).detach().numpy()[0]

    emotion_scores = {label: 0.0 for label in final_labels}
    for i, prob in enumerate(probs):
        mapped = goemotions_to_ekman[goemotions_labels[i]]
        emotion_scores[mapped] += prob

    top_emotion = max(emotion_scores, key=emotion_scores.get)
    return top_emotion, emotion_scores

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
        WHERE bert_ekman_sentiment IS NULL
    """)
    rows = cur.fetchall()

    for location_id, text in rows:
        if not text or text.strip() == "":
            continue
        top_emotion, _ = predict_sentiment(text)
        cur.execute("""
            UPDATE combined_sentiment_analysis
            SET bert_ekman_sentiment = %s
            WHERE location_id = %s
        """, (top_emotion, location_id))

    cur.close()
    conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        emotion, scores = predict_sentiment(input_text)
        print(f"Predicted Emotion: {emotion}")
        print("Scores:")
        for k, v in scores.items():
            print(f"{k}: {v:.4f}")
    else:
        analyze_database()
