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

goemotions_labels = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion",
    "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
    "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
    "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"
]

label_mapping = {
    "admiration": "joy",
    "amusement": "joy",
    "anger": "anger",
    "annoyance": "anger",
    "approval": "joy",
    "caring": "joy",
    "confusion": "neutral",
    "curiosity": "neutral",
    "desire": "joy",
    "disappointment": "sadness",
    "disapproval": "anger",
    "disgust": "disgust",
    "embarrassment": "sadness",
    "excitement": "joy",
    "fear": "fear",
    "gratitude": "joy",
    "grief": "sadness",
    "joy": "joy",
    "love": "joy",
    "nervousness": "fear",
    "optimism": "joy",
    "pride": "joy",
    "realization": "neutral",
    "relief": "joy",
    "remorse": "sadness",
    "sadness": "sadness",
    "surprise": "surprise",
    "neutral": "neutral"
}

final_labels = ['joy', 'anger', 'sadness', 'fear', 'disgust', 'surprise', 'neutral']

def predict_7class_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1).detach().numpy()[0]

    emotion_scores = {label: 0.0 for label in final_labels}
    for i, prob in enumerate(probs):
        mapped = label_mapping[goemotions_labels[i]]
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
        WHERE goemotions_sentiment IS NULL
    """)
    rows = cur.fetchall()

    for location_id, text in rows:
        if not text or text.strip() == "":
            continue
        top_emotion, _ = predict_7class_emotion(text)
        cur.execute("""
            UPDATE combined_sentiment_analysis
            SET goemotions_sentiment = %s
            WHERE location_id = %s
        """, (top_emotion, location_id))

    cur.close()
    conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        emotion, scores = predict_7class_emotion(input_text)
        print(f"Predicted Emotion: {emotion}")
        print("Scores:")
        for k, v in scores.items():
            print(f"{k}: {v:.4f}")
    else:
        analyze_database()
