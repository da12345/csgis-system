import os
import numpy as np
from PIL import Image
import torch
import matplotlib.pyplot as plt
from transformers import (
    AutoImageProcessor,
    Mask2FormerForUniversalSegmentation,
    AutoConfig,
)

# Constants and model setup
MODEL = "facebook/mask2former-swin-large-cityscapes-semantic"
cfg = AutoConfig.from_pretrained(MODEL)
id2label = cfg.id2label
VEG_ID = {8}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
processor = AutoImageProcessor.from_pretrained(MODEL)
model = Mask2FormerForUniversalSegmentation.from_pretrained(MODEL).to(device)

UPLOAD_DIR = "path/to/input"
SEGMENTED_DIR = "path/to/output"
os.makedirs(SEGMENTED_DIR, exist_ok=True)
SUPPORTED = {".jpg", ".jpeg", ".png"}

def save_segmentation_image(seg_map: np.ndarray, filename: str):
    num_classes = max(id2label.keys()) + 1
    cmap = plt.get_cmap("tab20", num_classes)
    colored = (cmap(seg_map / num_classes)[..., :3] * 255).astype(np.uint8)
    seg_img = Image.fromarray(colored)
    seg_img.save(os.path.join(SEGMENTED_DIR, filename.replace(".", "_segmented.")))

def gvi(path: str) -> float:
    img = Image.open(path).convert("RGB")
    inputs = processor(img, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    seg_map = processor.post_process_semantic_segmentation(
        outputs, target_sizes=[img.size[::-1]]
    )[0].cpu().numpy()

    save_segmentation_image(seg_map, os.path.basename(path))

    gvi_percentage = np.isin(seg_map, list(VEG_ID)).sum() / seg_map.size * 100
    return gvi_percentage

def main():
    fnames = [f for f in os.listdir(UPLOAD_DIR) if os.path.splitext(f)[1].lower() in SUPPORTED]

    for f in sorted(fnames):
        full_path = os.path.join(UPLOAD_DIR, f)
        try:
            val = gvi(full_path)
            print(f"{f}: GVI = {val:.2f}%")
        except Exception as e:
            print(f"Error processing {f}: {e}")

if __name__ == "__main__":
    main()
