import pytesseract
from PIL import Image
import os
import cv2
import re
from src.ocr.preprocess import preprocess_image

class OCRExtractor:
    def __init__(self, engine="tesseract"):
        self.engine = engine.lower()
        if self.engine == "tesseract":
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
        Extract text from header and table regions of an image.
        Returns (header_text, table_text, overall_confidence)
        """
        if preprocess:
            header_img, table_img = preprocess_image(image_path, save_debug=save_debug, debug_dir=debug_dir)
            if header_img is not None and table_img is not None:
                pil_header = Image.fromarray(header_img)
                pil_table = Image.fromarray(table_img)
            else:
                # Fallback to simple load if preprocess fails
                img = Image.open(image_path)
                return self._extract_full_text(img)
        else:
            img = Image.open(image_path)
            return self._extract_full_text(img)

        if self.engine == "tesseract":
            header_text = pytesseract.image_to_string(pil_header)
            table_text = pytesseract.image_to_string(pil_table)

            # Simplified confidence (Tesseract doesn't provide it directly here)
            # A production-ready version would use image_to_data
            confidence = 0.85
            return header_text, table_text, confidence

        elif self.engine == "paddle":
            # Simplified example for PaddleOCR on regions
            res_header = self.ocr.ocr(cv2.cvtColor(header_img, cv2.COLOR_GRAY2BGR), cls=True)
            res_table = self.ocr.ocr(cv2.cvtColor(table_img, cv2.COLOR_GRAY2BGR), cls=True)

            header_text = "\n".join([line[1][0] for res in res_header for line in res]) if res_header else ""
            table_text = "\n".join([line[1][0] for res in res_table for line in res]) if res_table else ""

            conf_h = sum([line[1][1] for res in res_header for line in res]) / len(res_header) if res_header else 0.8
            conf_t = sum([line[1][1] for res in res_table for line in res]) / len(res_table) if res_table else 0.8

            return header_text, table_text, (conf_h + conf_t) / 2
        else:
            raise ValueError(f"Unsupported OCR engine: {self.engine}")

    def _extract_full_text(self, pil_img):
        """Helper to extract text from a full image."""
        if self.engine == "tesseract":
            return "", pytesseract.image_to_string(pil_img), 0.8
        return "", "", 0.0

    @staticmethod
    def basic_cleanup(text):
        """Deprecated: use context_aware_cleanup instead."""
        return OCRExtractor.context_aware_cleanup(text)

    @staticmethod
    def context_aware_cleanup(text):
        """
        Perform context-aware cleanup on extracted text.
        Preserves original OCR text while applying targeted corrections.
        """
        if not text:
            return ""

        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # 1. Standardize spacing and casing
            line = line.strip().upper()

            # 2. Targeted subcategory label correction (FPPP commonly misread)
            line = re.sub(r'FP[FSP][FP]', 'FPPP', line)
            line = re.sub(r'TL[ \-]R', 'TLR', line)

            # 3. Context-aware digit correction using regex
            # Only replace O with 0 or I with 1 when they are adjacent to digits
            # and within a numeric context (e.g., 5O.5 -> 50.5)
            line = re.sub(r'(\d)[O0o](\d)', r'\1 0 \2', line) # temporarily separate to avoid multiple replacements
            line = line.replace(' 0 ', '0')
            line = re.sub(r'(\d)[O0o]', r'\1 0', line)
            line = line.replace(' 0', '0')
            line = re.sub(r'[O0o](\d)', r'0 \1', line)
            line = line.replace('0 ', '0')

            line = re.sub(r'(\d)[I1l](\d)', r'\1 1 \2', line)
            line = line.replace(' 1 ', '1')
            line = re.sub(r'(\d)[I1l]', r'\1 1', line)
            line = line.replace(' 1', '1')
            line = re.sub(r'[I1l](\d)', r'1 \1', line)
            line = line.replace('1 ', '1')

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)
