import os, sys, decimal
import numpy as np
from PIL import Image
import psycopg2
import torch
import matplotlib.pyplot as plt
from mmseg.apis.inference import init_model, inference_model
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../.env.production")

CONFIG = "checkpoints/pspnet_r50-d8_4xb2-40k_cityscapes-512x1024.py"
CHECKPOINT = "checkpoints/pspnet_r50-d8_512x1024_40k_cityscapes_20200605_003338-2966598c.pth"
model = init_model(CONFIG, CHECKPOINT, device='cuda' if torch.cuda.is_available() else 'cpu')

VEG_ID = 8

UPLOAD_DIR = "path/to/input"
SEGMENTED_DIR = "path/to/output"
os.makedirs(SEGMENTED_DIR, exist_ok=True)
SUPPORTED = {".jpg", ".jpeg", ".png"}

def save_segmentation_image(seg_map: np.ndarray, filename: str):
    cmap = plt.get_cmap("tab20", np.max(seg_map)+1)
    colored = (cmap(seg_map)[..., :3] * 255).astype(np.uint8)
    Image.fromarray(colored).save(os.path.join(SEGMENTED_DIR, filename.replace(".", "_pspnet.")))

def gvi(image_path: str) -> float:
    result = inference_model(model, image_path)[0]
    seg_map = np.array(result)
    save_segmentation_image(seg_map, os.path.basename(image_path))
    green_pct = (seg_map == VEG_ID).sum() / seg_map.size * 100
    return green_pct

def db_connect():
    return psycopg2.connect(
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
    )

def main():
    args = sys.argv[1:]
    if len(args) == 2:
        location_id, filename = args
        full_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(full_path):
            return
        try:
            conn = db_connect()
            cur = conn.cursor()
            cur.execute("SELECT pspnet_gvi FROM image_analysis WHERE location_id = %s", (location_id,))
            result = cur.fetchone()
            if result and result[0] is not None:
                return
            val = gvi(full_path)
            cur.execute("""
                INSERT INTO image_analysis (location_id, image_name, pspnet_gvi)
                VALUES (%s, %s, %s)
                ON CONFLICT (location_id)
                DO UPDATE SET pspnet_gvi = EXCLUDED.pspnet_gvi;
            """, (location_id, f"https://csgis.idi.ntnu.no/uploads/{filename}", decimal.Decimal(f"{val:.2f}")))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            print(e)
        return
    elif len(args) == 0:
        conn = db_connect()
        cur = conn.cursor()
        fnames = [f for f in os.listdir(UPLOAD_DIR) if os.path.splitext(f)[1].lower() in SUPPORTED]
        for f in sorted(fnames):
            full_path = os.path.join(UPLOAD_DIR, f)
            try:
                cur.execute("""
                    SELECT id FROM locations
                    WHERE image ILIKE %s
                    ORDER BY date_time DESC LIMIT 1
                """, (f"%/uploads/{f}",))
                row = cur.fetchone()
                if not row:
                    continue
                loc_id = row[0]
                cur.execute("SELECT pspnet_gvi FROM image_analysis WHERE location_id = %s", (loc_id,))
                existing = cur.fetchone()
                if existing and existing[0] is not None:
                    continue
                val = gvi(full_path)
                cur.execute("""
                    INSERT INTO image_analysis (location_id, image_name, pspnet_gvi)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (location_id)
                    DO UPDATE SET pspnet_gvi = EXCLUDED.pspnet_gvi;
                """, (loc_id, f"https://csgis.idi.ntnu.no/uploads/{f}", decimal.Decimal(f"{val:.2f}")))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(e)
        cur.close(); conn.close()
        return

if __name__ == "__main__":
    main()
