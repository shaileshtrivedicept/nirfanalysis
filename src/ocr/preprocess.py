import cv2
import numpy as np
import os

def preprocess_image(image_path, save_debug=False, debug_dir=None):
    """
    Apply robust preprocessing to the image for improved OCR results.
    """
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        return None

    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Adaptive Thresholding (better for uneven lighting)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Contrast enhancement (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    # Simple table region detection: isolate bottom half
    # In NIRF reports, the score table is typically in the bottom half
    h, w = gray.shape
    header_region = gray[0:int(h*0.3), 0:w] # Top 30%
    table_region = gray[int(h*0.3):h, 0:w] # Bottom 70%

    # Deskew (simplified logic using minAreaRect)
    deskewed_table = desk_image(table_region)

    if save_debug and debug_dir:
        os.makedirs(debug_dir, exist_ok=True)
        filename = os.path.basename(image_path)
        cv2.imwrite(os.path.join(debug_dir, f"header_{filename}"), header_region)
        cv2.imwrite(os.path.join(debug_dir, f"table_{filename}"), deskewed_table)

    return header_region, deskewed_table

def desk_image(image):
    """
    Deskew the image.
    """
    # Inverse threshold to find content
    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) == 0:
        return image

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated
