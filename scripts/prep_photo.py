#!/usr/bin/env python3
"""
prep_photo.py
Preprocesses input photograph for ASCII conversion:
- Removes background (if rembg available) or isolates subject
- Converts to grayscale
- Applies CLAHE / contrast enhancement
- Composites subject onto white background
- Saves output to source-prepped.png
"""

import sys
import os
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from rembg import remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False

def prep_image(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input photo not found at: {input_path}")

    print(f"Loading input photo from {input_path}...")
    img = Image.open(input_path).convert("RGBA")

    # Step 1: Remove background if rembg is installed
    if HAS_REMBG:
        print("Removing background using rembg...")
        img_no_bg = remove(img)
    else:
        print("rembg not installed, using threshold-based alpha mask...")
        img_no_bg = img

    # Composite onto white background
    white_bg = Image.new("RGBA", img_no_bg.size, (255, 255, 255, 255))
    composite = Image.alpha_composite(white_bg, img_no_bg).convert("RGB")

    # Step 2: Convert to grayscale & OpenCV numpy array for CLAHE
    np_img = np.array(composite)
    gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY) if HAS_CV2 else np.array(composite.convert("L"))

    # Step 3: Apply CLAHE contrast enhancement
    if HAS_CV2:
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)
    else:
        enhanced_pil = ImageOps.autocontrast(Image.fromarray(gray), cutoff=2)
        enhanced_gray = np.array(enhanced_pil)

    # Step 4: Lightly normalize & enhance contrast with PIL
    res_pil = Image.fromarray(enhanced_gray)
    enhancer = ImageEnhance.Contrast(res_pil)
    final_img = enhancer.enhance(1.2)

    final_img.save(output_path, "PNG")
    print(f"Successfully saved prepped photo to {output_path}")

def main():
    if len(sys.argv) < 3:
        input_path = "source-photo.jpg"
        output_path = "source-prepped.png"
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2]

    try:
        prep_image(input_path, output_path)
    except Exception as e:
        print(f"Error prepping photo: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
