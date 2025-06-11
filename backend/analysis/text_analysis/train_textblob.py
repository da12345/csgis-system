import os
import re
import pickle
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

load_dotenv("path/to/env")

DB = {
    "dbname": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT")
}

conn = psycopg2.connect(**DB)
query = """
    SELECT combined_response, textblob_sentiment_label
    FROM combined_sentiment_analysis
    WHERE textblob_sentiment_label IS NOT NULL
"""
df = pd.read_sql(query, conn)
conn.close()

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"[^a-z\s]", "", text.lower()).strip()

df["clean_text"] = df["combined_response"].apply(clean_text)

min_samples = 2
label_counts = df["textblob_sentiment_label"].value_counts()
valid_labels = label_counts[label_counts >= min_samples].index
df = df[df["textblob_sentiment_label"].isin(valid_labels)]

vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df["clean_text"])
y = df["textblob_sentiment_label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, test_size=0.2, random_state=42
)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

os.makedirs("sentiment_model", exist_ok=True)

with open("sentiment_model/textblob_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("sentiment_model/tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)