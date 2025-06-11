import os
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import re
from dotenv import load_dotenv

# Setup
nltk.download('punkt')
nltk.download('stopwords')
load_dotenv("../../../backend/.env.production")

# DB connection
DB = {
    "dbname": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT")
}

# Custom stopwords
stop_words = set(stopwords.words("english"))
stop_words.update({
    "place", "area", "thing", "space", "something", "someone",
    "location", "lot", "get", "got", "like", "use", "go", "come"
})

def clean_and_tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    tokens = word_tokenize(text)
    return [word for word in tokens if word not in stop_words and len(word) > 2]

def generate_wordcloud(words, filename):
    if not words:
        return
    wordcloud = WordCloud(width=1600, height=800, background_color='white').generate(" ".join(words))
    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(filename, dpi=300)
    plt.close()

conn = psycopg2.connect(**DB)
df = pd.read_sql("""
    SELECT c.location_id, c.combined_response, c.textblob_sentiment_label, l.gender, l.age_group_id
    FROM combined_sentiment_analysis c
    LEFT JOIN locations l ON c.location_id = l.id
    WHERE c.combined_response IS NOT NULL
""", conn)
conn.close()

output_dir = "wordclouds"
os.makedirs(output_dir, exist_ok=True)

tasks = {
    "wordcloud_all.png": df,
}

genders = df["gender"].dropna().unique()
for gender in genders:
    filename = f"wordcloud_gender_{gender.lower()}.png"
    tasks[filename] = df[df["gender"] == gender]

age_groups = df["age_group_id"].dropna().unique()
for age in sorted(age_groups):
    filename = f"wordcloud_agegroup_{age}.png"
    tasks[filename] = df[df["age_group_id"] == age]

for filename, subset in tasks.items():
    texts = subset["combined_response"].dropna().astype(str).tolist()
    all_tokens = []
    for text in texts:
        all_tokens.extend(clean_and_tokenize(text))
    output_path = os.path.join(output_dir, filename)
    generate_wordcloud(all_tokens, output_path)
