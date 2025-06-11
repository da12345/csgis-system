import os
import re
import json
import psycopg2
import pandas as pd
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv("path/to/env")

DB = {
    "dbname": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT"),
}

conn = psycopg2.connect(**DB)
cursor = conn.cursor()

cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='combined_sentiment_analysis' AND column_name='textblob_sentiment'
        ) THEN
            ALTER TABLE combined_sentiment_analysis ADD COLUMN textblob_sentiment JSONB;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='combined_sentiment_analysis' AND column_name='textblob_sentiment_label'
        ) THEN
            ALTER TABLE combined_sentiment_analysis ADD COLUMN textblob_sentiment_label VARCHAR;
        END IF;
    END$$;
""")
conn.commit()

df = pd.read_sql("""
    SELECT location_id, combined_response
    FROM combined_sentiment_analysis
    WHERE textblob_sentiment IS NULL OR textblob_sentiment_label IS NULL
""", conn)

def get_textblob_data(text):
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 2)
    subjectivity = round(blob.sentiment.subjectivity, 2)
    if polarity > 0.1:
        label = "positive"
    elif polarity < -0.1:
        label = "negative"
    else:
        label = "neutral"
    return polarity, subjectivity, label

for _, row in df.iterrows():
    text = row["combined_response"]
    if not text or text.strip() == "":
        continue

    polarity, subjectivity, label = get_textblob_data(text)

    cursor.execute("""
        UPDATE combined_sentiment_analysis
        SET textblob_sentiment = %s,
            textblob_sentiment_label = %s
        WHERE location_id = %s
    """, (
        json.dumps({"polarity": polarity, "subjectivity": subjectivity}),
        label,
        row["location_id"]
    ))

conn.commit()
cursor.close()
conn.close()