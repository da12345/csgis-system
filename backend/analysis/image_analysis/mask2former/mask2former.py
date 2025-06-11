import os, sys, decimal
import numpy as np
from PIL import Image
import psycopg2
import torch
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from transformers import (
    AutoImageProcessor,
    Mask2FormerForUniversalSegmentation,
)
from dotenv import load_dotenv

load_dotenv(dotenv_path="path/to/env")

MODEL = "facebook/mask2former-swin-large-cityscapes-semantic"
IMAGE_DIR     = "path/to/input"

OUTPUT_DIR  = "path/to/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

VEG_ID = {8}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
processor = AutoImageProcessor.from_pretrained(MODEL)
model = Mask2FormerForUniversalSegmentation.from_pretrained(MODEL).to(device)

SUPPORTED_FORMATS      = {".jpg", ".jpeg", ".png"}

# not needed for gvi calculation, but used for making the images
def save_segmentation_image(seg_map: np.ndarray, filename: str):
    num_classes = model.config.num_labels
    cmap = plt.get_cmap("tab20", model.config.num_labels)
    colored = (cmap(seg_map / num_classes)[..., :3] * 255).astype(np.uint8)
    seg_img = Image.fromarray(colored)
    seg_img.save(os.path.join(OUTPUT_DIR, filename.replace(".", "_mask2former.")))

# here is where the GVI actually is calculated
def gvi(path: str) -> float:
    img = Image.open(path).convert("RGB")
    inputs = processor(images=img, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    seg_map = processor.post_process_semantic_segmentation(
        outputs, target_sizes=[img.size[::-1]]
    )[0].cpu().numpy()

    # save_segmentation_image(seg_map, os.path.basename(path))

    gvi_percentage = np.isin(seg_map, list(VEG_ID)).sum() / seg_map.size * 100
    
    return gvi_percentage

def db_connect():
    return psycopg2.connect(
        dbname = os.getenv("DATABASE_NAME"),
        user = os.getenv("DATABASE_USER"),
        password = os.getenv("DATABASE_PASSWORD"),
        host = os.getenv("DATABASE_HOST"),
        port = os.getenv("DATABASE_PORT"),
    )

def main():
    args = sys.argv[1:]

    if len(args) == 2:
        location_id, filename = args
        full_path = os.path.join(IMAGE_DIR, filename)
        if not os.path.exists(full_path):
            print(f"Not found")
            return

        try:
            conn = db_connect()
            cur = conn.cursor()

            cur.execute("ALTER TABLE image_analysis ADD COLUMN IF NOT EXISTS mask2former_gvi NUMERIC;")
            cur.execute("SELECT mask2former_gvi FROM image_analysis WHERE location_id = %s", (location_id,))

            result = cur.fetchone()
            if result and result[0] is not None:
                return

            value = gvi(full_path)
            cur.execute("""
                INSERT INTO image_analysis (location_id, image_name, mask2former_gvi)
                VALUES (%s, %s, %s)
                ON CONFLICT (location_id)
                DO UPDATE SET mask2former_gvi = EXCLUDED.mask2former_gvi;
            """, (location_id, f"https://csgis.idi.ntnu.no/uploads/{filename}", decimal.Decimal(f"{value:.2f}")))
            conn.commit()
            cur.close();
            conn.close()
        except Exception as e:
            print(f"Error, {e}")
        return

    elif len(args) == 0:
        conn = db_connect()
        cur = conn.cursor()

        cur.execute("ALTER TABLE image_analysis ADD COLUMN IF NOT EXISTS mask2former_gvi NUMERIC;")
        imgnames = [f for f in os.listdir(IMAGE_DIR) if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS]

        for i in sorted(imgnames):
            full_path = os.path.join(IMAGE_DIR, i)
            try:
                cur.execute("""
                    SELECT id FROM locations
                    WHERE image ILIKE %s
                    ORDER BY date_time DESC LIMIT 1
                """, (f"%/uploads/{i}",))
                result = cur.fetchone()
                if not result:
                    continue

                loc_id = result[0]
                cur.execute("SELECT mask2former_gvi FROM image_analysis WHERE location_id = %s", (loc_id,))
                existing = cur.fetchone()
                if existing and existing[0] is not None:
                    continue

                value = gvi(full_path)
                cur.execute("""
                    INSERT INTO image_analysis (location_id, image_name, mask2former_gvi)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (location_id)
                    DO UPDATE SET mask2former_gvi = EXCLUDED.mask2former_gvi;
                """, (loc_id, f"https://csgis.idi.ntnu.no/uploads/{i}", decimal.Decimal(f"{value:.2f}")))
                conn.commit()

            except Exception as e:
                conn.rollback()
                print(f"Error processing {f}: {e}")

        cur.close(); conn.close()
        return

if __name__ == "__main__":
    main()
