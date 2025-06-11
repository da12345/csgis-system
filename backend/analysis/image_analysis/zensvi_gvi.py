from pathlib import Path
import json
import os
import psycopg2
from dotenv import load_dotenv
from tqdm import tqdm
from zensvi.cv import Segmenter
from PIL import Image

ENV_PATH      = "path/to/env"
load_dotenv(ENV_PATH)

DB_CFG = dict(
    dbname   = os.getenv("DATABASE_NAME"),
    user     = os.getenv("DATABASE_USER"),
    password = os.getenv("DATABASE_PASSWORD"),
    host     = os.getenv("DATABASE_HOST"),
    port     = os.getenv("DATABASE_PORT"),
)

UPLOADS_DIR   = Path("path/to/input")
OUTPUT_DIR    = Path("path/to/output")
SUMMARY_DIR   = OUTPUT_DIR / "summary"
SEGMENTED_DIR = OUTPUT_DIR / "segmented"
SUMMARY_JSON  = SUMMARY_DIR / "pixel_ratios.json"
GREEN_LABELS  = {"vegetation"}

SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
SEGMENTED_DIR.mkdir(parents=True, exist_ok=True)

segmenter = Segmenter(dataset="cityscapes", task="semantic")

def load_summary() -> dict:
    return json.loads(SUMMARY_JSON.read_text()) if SUMMARY_JSON.exists() else {}


def save_summary(d: dict) -> None:
    SUMMARY_JSON.write_text(json.dumps(d, indent=0, separators=(",", ":")))


def vegetation_pct(entry) -> float | None:
    """Return percentage of green pixels for one photo entry (0–100)."""
    if entry is None:
        return None
    if isinstance(entry, dict):
        return round(entry.get("vegetation", 0.0) * 100, 2)
    if isinstance(entry, list):
        ratio = sum(r["ratio"] for r in entry if r.get("label") in GREEN_LABELS)
        return round(ratio * 100, 2)
    return None


def ensure_summary_for(photo_key: str, img_path: Path, summary: dict) -> dict:
    """Guarantee summary[photo_key] exists; run segmenter once if not."""
    if photo_key in summary:
        return summary

    segmenter.segment(
        img_path.parent,
        dir_summary_output=SUMMARY_DIR,
        dir_image_output=SEGMENTED_DIR,
    )
    summary.update(load_summary())
    return summary


def db_connect():
    return psycopg2.connect(**DB_CFG)


def ensure_image_row(cur, filename: str) -> None:
    """Insert a stub row if image_name not present in image_analysis."""
    cur.execute("SELECT 1 FROM image_analysis WHERE image_name ILIKE %s",
                (f"%{filename}",))
    if cur.fetchone() is None:
        url = f"https://csgis.idi.ntnu.no/uploads/{filename}"
        cur.execute("INSERT INTO image_analysis (image_name) VALUES (%s)", (url,))

def main() -> None:
    conn = db_connect()
    cur  = conn.cursor()
    cur.execute(
        "ALTER TABLE image_analysis "
        "ADD COLUMN IF NOT EXISTS zensvi_gvi NUMERIC(5,2);"
    )
    conn.commit()

    summary = load_summary()
    images  = sorted(list(UPLOADS_DIR.glob("*.[jJpP][pPnN]*[gG]")) +
                     list(UPLOADS_DIR.glob("*.png")))

    for img_path in tqdm(images, desc="Processing images"):
        filename   = img_path.name
        photo_key  = img_path.stem

        summary    = ensure_summary_for(photo_key, img_path, summary)
        gvi        = vegetation_pct(summary.get(photo_key))

        if gvi is None:
            print(f"{filename}: no vegetation data")
            continue

        print(f"{filename}: {gvi:5.2f}% green")

        ensure_image_row(cur, filename)
        cur.execute(
            "UPDATE image_analysis "
            "SET zensvi_gvi = %s "
            "WHERE image_name ILIKE %s",
            (gvi, f"%{filename}")
        )
        conn.commit()

    cur.close()
    conn.close()
    save_summary(summary)


if __name__ == "__main__":
    main()
