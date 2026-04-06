import cv2
import numpy as np
import os

def preprocess_image(image_path, save_debug=False, debug_dir=None):
    """
    Apply preprocessing to the image for improved OCR results.
    """
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        return None

    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Thresholding (Otsu's binarization)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Contrast enhancement (optional but often beneficial)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    # Deskew (simplified logic)
    deskewed = desk_image(thresh)

    if save_debug and debug_dir:
        os.makedirs(debug_dir, exist_ok=True)
        filename = os.path.basename(image_path)
        cv2.imwrite(os.path.join(debug_dir, f"debug_{filename}"), deskewed)

    return deskewed

def desk_image(image):
    """
    Deskew the image.
    """
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]

    # the `cv2.minAreaRect` function returns values in the
    # range [-90, 0); as the rectangle rotates clockwise the
    # returned angle trends to 0 -- in this special case we
    # need to add 90 degrees to the angle
    if angle < -45:
        angle = -(90 + angle)
    # otherwise, just take the inverse of the angle to make
    # it positive
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

def deskew_image(image):
    """
    Deskew the image using Hough lines or minAreaRect.
    """
    # Simple version: just return original for now, but provide structure
    # Robust deskew logic can be complex
    return image
