import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from PIL import Image
from zensvi.cv import ClassifierPlaces365

upload_dir = "path/to/input"
output_dir = os.path.join(os.getcwd(), "scene_classification_results")
summary_dir = os.path.join(output_dir, "summary")

# Create output directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(summary_dir, exist_ok=True)

for filename in os.listdir(upload_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        path = os.path.join(upload_dir, filename)
        try:
            img = Image.open(path)
            if img.mode != "RGB":
                img = img.convert("RGB")
                img.save(path)
                print(f"Converted {filename} to RGB.")
        except Exception as e:
            print(e)

classifier = ClassifierPlaces365(device="cpu")
classifier.classify(
    upload_dir,
    dir_image_output=output_dir,
    dir_summary_output=summary_dir
)

load_dotenv("../../../.env.production")
DB = {
    "dbname": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT")
}

conn = psycopg2.connect(**DB)
cursor = conn.cursor()
image_df = pd.read_sql("SELECT DISTINCT image FROM locations WHERE image IS NOT NULL", conn)
existing_images = set(image_df["image"])

summary_csv_path = os.path.join(summary_dir, "results.csv")
df_long = pd.read_csv(summary_csv_path)
print("Available columns in results.csv:", df_long.columns.tolist())

df = df_long.pivot(index=["filename_key", "environment_type"], columns="variable", values="value").reset_index()

def match_existing_image_url(filename_key, db_images):
    base = f"https://csgis.idi.ntnu.no/uploads/{filename_key}"
    jpg = f"{base}.jpg"
    jpeg = f"{base}.jpeg"
    if jpg in db_images:
        return jpg
    elif jpeg in db_images:
        return jpeg
    return None

df["filename"] = df["filename_key"].apply(lambda x: match_existing_image_url(x, existing_images))
df = df.dropna(subset=["filename"])

update_count = 0
for _, row in df.iterrows():
    filename = row["filename"]
    scene_type = row["environment_type"]

    cursor.execute("""
        UPDATE locations
        SET scene_type = %s
        WHERE image = %s
    """, (scene_type, filename))

    if cursor.rowcount > 0:
        update_count += 1

conn.commit()
cursor.close()
conn.close()