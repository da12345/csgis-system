import os, torch, numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from mmseg.apis import init_model, inference_model
from mmseg.utils import register_all_modules

CFG_FILE  = 'pspnet_r50-d8_512x1024_40k_cityscapes.py'
CKPT_FILE = 'pspnet_r50-d8_512x1024_40k_cityscapes_20200605_003338-2966598c.pth'

IMAGE_DIR = '/Users/danielaxlid/Documents/Documents - Daniel’s MacBook Air/Universitet/V2025/csgis-app/frontend/public/comparison'
OUT_DIR   = 'pspnet_outputs'
os.makedirs(OUT_DIR, exist_ok=True)

VEG_ID    = 8          

def colorize(mask, n_cls=19):
    cmap = plt.get_cmap('tab20', n_cls)
    rgb  = (cmap(mask / n_cls)[..., :3] * 255).astype(np.uint8)
    return Image.fromarray(rgb)

register_all_modules()
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model  = init_model(CFG_FILE, CKPT_FILE, device=device)

for fname in sorted(os.listdir(IMAGE_DIR)):
    if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue

    img_path = os.path.join(IMAGE_DIR, fname)
    result   = inference_model(model, img_path)
    seg      = result.pred_sem_seg.data.squeeze().cpu().numpy()

    colorize(seg).save(os.path.join(OUT_DIR, fname.replace('.', '_pspnet.')))

    gvi = round((seg == VEG_ID).sum() / seg.size * 100, 2)
    print(f'{fname}: GVI = {gvi}%')
