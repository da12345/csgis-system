import sys
import os
import psycopg2
import json
from textblob import TextBlob
from dotenv import load_dotenv

ENV_PATH = "path/to/env"
load_dotenv(ENV_PATH)

def get_textblob_scores(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def predict_textblob_sentiment(text):
    polarity, subjectivity = get_textblob_scores(text)
    return polarity, subjectivity

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
        WHERE textblob_sentiment IS NULL
    """)
    rows = cur.fetchall()

    for id, text in rows:
        if not text or text.strip() == "":
            continue
        polarity, subjectivity = predict_textblob_sentiment(text)
        cur.execute("""
            UPDATE combined_sentiment_analysis
            SET textblob_sentiment = %s
            WHERE location_id = %s
        """, (json.dumps({
            "polarity": round(polarity, 2),
            "subjectivity": round(subjectivity, 2)
        }), id))

    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        polarity, subjectivity = predict_textblob_sentiment(input_text)
        print(json.dumps({
            "polarity": round(polarity, 2),
            "subjectivity": round(subjectivity, 2)
        }))
    else:
        analyze_database()
