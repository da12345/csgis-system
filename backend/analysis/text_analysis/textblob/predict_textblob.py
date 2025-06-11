import os
import re
import sys
import pickle
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

load_dotenv("path/to/env")

DB = {
    "dbname": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT")
}

model_path = "sentiment_model/textblob_model.pkl"
vectorizer_path = "sentiment_model/tfidf_vectorizer.pkl"

with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(vectorizer_path, "rb") as f:
    vectorizer = pickle.load(f)

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"[^a-zA-Z\s]", "", text.lower()).strip()

def predict_sentiment(text):
    clean = clean_text(text)
    X = vectorizer.transform([clean])
    return model.predict(X)[0]

def batch_predict_and_update():
    conn = psycopg2.connect(**DB)
    cursor = conn.cursor()

    df = pd.read_sql("""
        SELECT location_id, free_text_response
        FROM free_text_responses
        WHERE textblob_sentiment_label IS NULL
    """, conn)

    updates = 0
    for _, row in df.iterrows():
        text = row["free_text_response"]
        if not text or text.strip() == "":
            continue
        label = predict_sentiment(text)
        cursor.execute("""
            UPDATE free_text_responses
            SET textblob_sentiment_label = %s
            WHERE location_id = %s
        """, (label, row["location_id"]))
        updates += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Batch sentiment prediction complete. Updated {updates} rows.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        batch_predict_and_update()
    else:
        input_text = sys.argv[1]
        predicted = predict_sentiment(input_text)
        print(f"Predicted sentiment: {predicted}")
