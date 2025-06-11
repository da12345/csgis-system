import os
import sys
import psycopg2
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load DB credentials
load_dotenv("path/to/env")

# Initialize analyzer
analyzer = SentimentIntensityAnalyzer()

def predict_vader_sentiment(text):
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.05:
        return 'positive'
    elif compound <= -0.05:
        return 'negative'
    else:
        return 'neutral'

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

    # Ensure column exists (defensive programming)
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='free_text_responses' 
                AND column_name='vader_sentiment'
            ) THEN
                ALTER TABLE free_text_responses 
                ADD COLUMN vader_sentiment TEXT;
            END IF;
        END$$;
    """)

    # Fetch records that need VADER sentiment
    cur.execute("""
        SELECT location_id, free_text_response
        FROM free_text_responses
        WHERE vader_sentiment IS NULL OR vader_sentiment = ''
    """)
    rows = cur.fetchall()

    print(f"Found {len(rows)} records to label with VADER.")

    updates = 0
    for location_id, text in rows:
        if not text or text.strip() == "":
            continue
        sentiment = predict_vader_sentiment(text)
        cur.execute("""
            UPDATE free_text_responses
            SET vader_sentiment = %s
            WHERE location_id = %s
        """, (sentiment, location_id))
        updates += 1

    cur.close()
    conn.close()
    print(f"VADER sentiment labeling complete. Updated {updates} rows.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        sentiment = predict_vader_sentiment(input_text)
        print(f"Predicted sentiment: {sentiment}")
    else:
        analyze_database()
