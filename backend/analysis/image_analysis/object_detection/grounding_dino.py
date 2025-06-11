import os
import json
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image
from tqdm import tqdm
from zensvi.cv import ObjectDetector

ENV_PATH = Path(__file__).resolve().parents[3] / ".env.production"
load_dotenv(ENV_PATH)

DB = {
    "dbname": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT")
}

UPLOADS_DIR = Path("path/to/input")
OUTPUT_DIR = Path("path/to/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GROUPED_JSON = OUTPUT_DIR / "detection_summary_grouped.json"

def clean_previous_outputs():
    if GROUPED_JSON.exists():
        GROUPED_JSON.unlink()

    for done_file in OUTPUT_DIR.glob("*.done"):
        done_file.unlink()

def convert_images_to_rgb(folder_path):
    for file in folder_path.iterdir():
        if file.is_file():
            try:
                with Image.open(file) as img:
                    if img.mode != "RGB":
                        img.convert("RGB").save(file)
            except Exception as e:
                print(e)

def connect():
    return psycopg2.connect(**DB)

def main():
    for file in OUTPUT_DIR.glob("*"):
        if file.suffix.lower() in {".json", ".jpg", ".jpeg", ".png"}:
            file.unlink()

    convert_images_to_rgb(UPLOADS_DIR)
    clean_previous_outputs()

    detector = ObjectDetector(
        text_prompt="tree . car .",
        box_threshold=0.35,
        text_threshold=0.25,
        verbosity=1
    )

    detector.detect_objects(
        dir_input=str(UPLOADS_DIR),
        dir_image_output=str(OUTPUT_DIR),
        dir_summary_output=str(OUTPUT_DIR),
        save_format="json",
        max_workers=2,
        group_by_object=True
    )

    if not GROUPED_JSON.exists():
        return

    with open(GROUPED_JSON) as f:
        raw_data = json.load(f)
        summary_data = {entry["filename"]: entry for entry in raw_data} if isinstance(raw_data, list) else raw_data

    conn = connect()
    cur = conn.cursor()

    for filename_key, counts in tqdm(summary_data.items(), desc="Updating DB"):
        num_trees = counts.get("tree", 0)
        num_cars = counts.get("car", 0)

        query = """
        SELECT id FROM locations
        WHERE image ILIKE %s
        OR image ILIKE %s
        OR image ILIKE %s
        OR image ILIKE %s
        """
        values = (f"%/{filename_key}",)
        cur.execute(query, values)
        result = cur.fetchone()

        if result:
            location_id = result[0]
            cur.execute("""
                UPDATE locations
                SET num_trees = %s,
                    num_cars = %s
                WHERE id = %s
            """, (num_trees, num_cars, location_id))
            conn.commit()
        else:
            print(f"no DB match")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
