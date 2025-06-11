import numpy as np
import tensorflow as tf
from PIL import Image
import os
import psycopg2
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv(dotenv_path="path/to/env")

MODEL = "2.tflite"
IMAGE_DIR = "path/to/input"

OUTPUT_DIR = "path/to/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

interpreter = tf.lite.Interpreter(model_path=MODEL)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# here is where the GVI actually is calculated
def calculate_gvi(mask, offset_x, offset_y, img_width, img_height):
    cropped_mask = mask[offset_y:offset_y + img_height, offset_x:offset_x + img_width]
    green_pixels = np.sum(cropped_mask == 8)
    total_pixels = cropped_mask.size
    return green_pixels / total_pixels if total_pixels > 0 else 0

def preprocess_image(image_path):
    target_width, target_height = 2049, 1025
    image = Image.open(image_path).convert("RGB")
    original_width, original_height = image.size
    scale = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    offset_x = (target_width - new_width) // 2
    offset_y = (target_height - new_height) // 2
    padded_image = Image.new("RGB", (target_width, target_height))
    padded_image.paste(resized, (offset_x, offset_y))
    input_data = np.expand_dims(np.array(padded_image, dtype=np.float32) / 255.0, axis=0)

    return input_data, padded_image, (offset_x, offset_y, new_width, new_height)

# only needed for visualization
def decode_segmentation_mask(mask):
    label_colors = [
        (128, 64,128), (244, 35,232), (70, 70, 70), (102,102,156),
        (190,153,153), (153,153,153), (250,170,30), (220,220,0),
        (107,142,35), (152,251,152), (70,130,180), (220,20,60),
        (255, 0, 0), (0, 0,142), (0, 0,70), (0, 60,100),
        (0, 80,100), (0, 0,230), (119, 11, 32)
    ]
    height, width = mask.shape
    color_mask = np.zeros((height, width, 3), dtype=np.uint8)
    for label_id, color in enumerate(label_colors):
        color_mask[mask == label_id] = color
    return color_mask

conn = psycopg2.connect(
    dbname=os.getenv("DATABASE_NAME"),
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    port=os.getenv("DATABASE_PORT")
)

cur = conn.cursor()

for file in os.listdir(IMAGE_DIR):
    if not file.lower().endswith((".jpg", ".jpeg", ".png")):
        continue
    image_path = os.path.join(IMAGE_DIR, file)

    input_data, padded_image, (offset_x, offset_y, img_width, img_height) = preprocess_image(image_path)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    mask = np.squeeze(np.argmax(output_data, axis=-1)).astype(np.uint8)
    gvi = calculate_gvi(mask, offset_x, offset_y, img_width, img_height)

    color_mask = decode_segmentation_mask(mask)
    output_image = Image.fromarray(color_mask)
    output_image.save(os.path.join(OUTPUT_DIR, file))

    cur.execute("""
        SELECT id FROM locations 
        WHERE image ILIKE %s
        ORDER BY date_time DESC 
        LIMIT 1
    """, (f"%/uploads/{file}",))
    
    result = cur.fetchone()

    if not result:
        continue

    if result:
        location_id = result[0]
        full_url = f"https://csgis.idi.ntnu.no/uploads/{file}"

        cur.execute("""
            INSERT INTO image_analysis (location_id, deeplab_gvi, image_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (location_id) DO UPDATE SET 
                deeplab_gvi = EXCLUDED.deeplab_gvi,
                image_name = EXCLUDED.image_name
        """, (location_id, round(gvi * 100, 2), full_url))

        conn.commit()

cur.close()
conn.close()
