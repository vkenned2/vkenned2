#!/usr/bin/env python3
"""
prep_photo.py
Preprocesses input photograph for ASCII conversion:
- Corrects EXIF orientation
- Auto-crops around face and shoulders (using OpenCV Haar cascades if available, or smart upper crop)
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

def crop_face_shoulders(img: Image.Image) -> Image.Image:
    """
    Detects face using OpenCV Haar Cascade or falls back to smart head/shoulders crop.
    """
    w, h = img.size
    
    if HAS_CV2:
        try:
            # Convert PIL to OpenCV BGR image
            np_img = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(np_img, cv2.COLOR_BGR2GRAY)
            
            # Load default OpenCV frontal face cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                face_cascade = cv2.CascadeClassifier(cascade_path)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
                
                if len(faces) > 0:
                    # Pick largest face
                    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                    fx, fy, fw, fh = faces[0]
                    print(f"Face detected at ({fx}, {fy}, {fw}, {fh})")

                    # Expand bounding box to include hair and shoulders
                    cx, cy = fx + fw // 2, fy + fh // 2
                    size = int(max(fw, fh) * 2.2) # Expand size
                    
                    left = max(0, cx - size // 2)
                    top = max(0, cy - int(size * 0.45))
                    right = min(w, cx + size // 2)
                    bottom = min(h, cy + int(size * 0.75))
                    
                    print(f"Cropping face/shoulders region: ({left}, {top}, {right}, {bottom})")
                    return img.crop((left, top, right, bottom))
        except Exception as e:
            print(f"Face detection fallback: {e}", file=sys.stderr)

    # Fallback smart crop: if portrait format (height > width), crop upper 60%
    print("Using upper head/shoulders crop fallback...")
    crop_bottom = int(h * 0.65)
    return img.crop((0, 0, w, crop_bottom))

def prep_image(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input photo not found at: {input_path}")

    print(f"Loading input photo from {input_path}...")
    raw_img = Image.open(input_path)

    # Fix EXIF orientation (e.g. camera rotation)
    img = ImageOps.exif_transpose(raw_img).convert("RGBA")

    # Step 1: Crop around face and shoulders
    img = crop_face_shoulders(img)

    # Step 2: Remove background if rembg is installed
    if HAS_REMBG:
        print("Removing background using rembg...")
        try:
            img_no_bg = remove(img)
        except Exception as e:
            print(f"rembg warning: {e}. Using original cropped image.", file=sys.stderr)
            img_no_bg = img
    else:
        print("rembg not installed, using cropped image directly...")
        img_no_bg = img

    # Composite onto white background
    white_bg = Image.new("RGBA", img_no_bg.size, (255, 255, 255, 255))
    composite = Image.alpha_composite(white_bg, img_no_bg).convert("RGB")

    # Step 3: Convert to grayscale & OpenCV numpy array for CLAHE
    np_img = np.array(composite)
    gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY) if HAS_CV2 else np.array(composite.convert("L"))

    # Step 4: Apply CLAHE contrast enhancement
    if HAS_CV2:
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)
    else:
        enhanced_pil = ImageOps.autocontrast(Image.fromarray(gray), cutoff=2)
        enhanced_gray = np.array(enhanced_pil)

    # Step 5: Normalize & enhance contrast with PIL
    res_pil = Image.fromarray(enhanced_gray)
    enhancer = ImageEnhance.Contrast(res_pil)
    final_img = enhancer.enhance(1.25)

    final_img.save(output_path, "PNG")
    print(f"Successfully saved prepped photo to {output_path}")

def main():
    if len(sys.argv) < 3:
        input_path = "source-photo.JPG"
        if not os.path.exists(input_path) and os.path.exists("source-photo.jpg"):
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
