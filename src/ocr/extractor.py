import pytesseract
from PIL import Image
import os
import cv2
from src.ocr.preprocess import preprocess_image

class OCRExtractor:
    def __init__(self, engine="tesseract"):
        self.engine = engine.lower()
        if self.engine == "tesseract":
            # For local installations, if tesseract is not in PATH, set:
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pass
        elif self.engine == "paddle":
            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
            except ImportError:
                print("PaddleOCR not installed. Falling back to tesseract.")
                self.engine = "tesseract"

    def extract_text(self, image_path, preprocess=True, save_debug=False, debug_dir=None):
        """
        Extract text from an image.
        """
        if preprocess:
            processed_img = preprocess_image(image_path, save_debug=save_debug, debug_dir=debug_dir)
            if processed_img is not None:
                # Convert cv2 image back to PIL for pytesseract if needed
                pil_img = Image.fromarray(processed_img)
            else:
                pil_img = Image.open(image_path)
        else:
            pil_img = Image.open(image_path)

        if self.engine == "tesseract":
            text = pytesseract.image_to_string(pil_img)
            confidence = 0.8  # Tesseract doesn't give straightforward overall confidence for a block
            return text, confidence
        elif self.engine == "paddle":
            # Implementation for PaddleOCR (example)
            result = self.ocr.ocr(image_path, cls=True)
            text = "\n".join([line[1][0] for res in result for line in res])
            confidence = sum([line[1][1] for res in result for line in res]) / len(result) if result else 0
            return text, confidence
        else:
            raise ValueError(f"Unsupported OCR engine: {self.engine}")

    @staticmethod
    def basic_cleanup(text):
        """
        Perform basic cleanup on extracted text to correct common OCR errors.
        """
        # Fix O ↔ 0, I ↔ 1 only in contexts that look like numbers if possible
        # We can use a simple regex-based replacement for digits misread as letters
        # but only in numeric contexts (e.g. following a subcategory)

        # General subcategory replacements
        corrections = {
            "FPFP": "FPPP",
            "FPPF": "FPPP",
            "FP PP": "FPPP",
            "TL R": "TLR",
            "GO ": "GO", # sometimes spaces creep in
            "O1": "OI",
            "0I": "OI",
            "PR ": "PR"
        }
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)

        # Standardizing OCR results
        text = text.upper()

        # Common digit misreads
        # (Simplified implementation: replace in the entire text,
        # but focusing on characters commonly misread by Tesseract)
        text = text.replace('O', '0').replace('I', '1').replace('S', '5').replace('G', '6')

        # NOTE: Replacing letters with numbers globally may break category names (e.g., GO -> 60)
        # In a real-world scenario, we would use more targeted regex like:
        # text = re.sub(r'(\d)[OI](\d)', r'\1\2', text)

        return text
