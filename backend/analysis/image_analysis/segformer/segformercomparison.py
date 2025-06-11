import os
import numpy as np
from PIL import Image
import torch
import matplotlib.pyplot as plt
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation

MODEL_NAME = "nvidia/segformer-b2-finetuned-cityscapes-1024-1024"
VEGETATION_CLASS = {8}
IMAGE_DIR = "path/to/input"
OUTPUT_DIR = "path/to/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
processor = SegformerImageProcessor.from_pretrained(MODEL_NAME)
model = SegformerForSemanticSegmentation.from_pretrained(MODEL_NAME).to(device)

def decode_segmentation(segmentation, num_classes):
    cmap = plt.get_cmap("tab20", num_classes)
    colored = (cmap(segmentation / num_classes)[..., :3] * 255).astype(np.uint8)
    return Image.fromarray(colored)

def calculate_gvi(seg_mask):
    veg_pixels = np.isin(seg_mask, list(VEGETATION_CLASS)).sum()
    total_pixels = seg_mask.size
    return round((veg_pixels / total_pixels) * 100, 2)

for fname in sorted(os.listdir(IMAGE_DIR)):
    if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    img_path = os.path.join(IMAGE_DIR, fname)
    image = Image.open(img_path).convert("RGB")

    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)

    segmentation = outputs.logits.argmax(dim=1)[0].cpu().numpy()

    gvi = calculate_gvi(segmentation)
    print(f"{fname}: GVI = {gvi}%")
