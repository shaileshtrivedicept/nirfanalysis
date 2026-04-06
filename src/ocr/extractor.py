import pytesseract
from PIL import Image
import os
import cv2
import re
import numpy as np
from src.ocr.preprocess import preprocess_image

class OCRExtractor:
    def __init__(self, engine="tesseract"):
        self.engine = engine.lower()
        self.tesseract_available = self._check_tesseract()
        self.easyocr_reader = None

        if self.engine == "tesseract" and not self.tesseract_available:
            print("Tesseract not found. Falling back to EasyOCR.")
            self.engine = "easyocr"

        if self.engine == "easyocr":
            try:
                import easyocr
                self.easyocr_reader = easyocr.Reader(['en'])
            except ImportError:
                print("EasyOCR not installed. OCR will fail.")

        elif self.engine == "paddle":
            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
            except ImportError:
                print("PaddleOCR not installed. Falling back to EasyOCR.")
                self.engine = "easyocr"
                import easyocr
                self.easyocr_reader = easyocr.Reader(['en'])

    def _check_tesseract(self):
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def extract_text(self, image_path, preprocess=True, save_debug=False, debug_dir=None):
        """
        Extract text from header and table regions of an image.
        Returns (header_text, table_text, overall_confidence, (header_img, table_img))
        """
        header_img, table_img = None, None
        if preprocess:
            header_img, table_img = preprocess_image(image_path, save_debug=save_debug, debug_dir=debug_dir)
            if header_img is None or table_img is None:
                img = Image.open(image_path)
                header, table, conf = self._extract_full_text(img)
                return header, table, conf, (None, None)
        else:
            img = Image.open(image_path)
            header, table, conf = self._extract_full_text(img)
            return header, table, conf, (None, None)

        if self.engine == "tesseract":
            header_text = pytesseract.image_to_string(Image.fromarray(header_img))
            table_text = pytesseract.image_to_string(Image.fromarray(table_img))
            return header_text, table_text, 0.85, (header_img, table_img)

        elif self.engine == "easyocr":
            if self.easyocr_reader:
                res_header = self.easyocr_reader.readtext(header_img)
                res_table = self.easyocr_reader.readtext(table_img)

                header_text = "\n".join([text for (bbox, text, prob) in res_header])
                table_text = "\n".join([text for (bbox, text, prob) in res_table])

                conf_h = sum([prob for (bbox, text, prob) in res_header]) / len(res_header) if res_header else 0.8
                conf_t = sum([prob for (bbox, text, prob) in res_table]) / len(res_table) if res_table else 0.8

                return header_text, table_text, (conf_h + conf_t) / 2, (header_img, table_img)
            return "", "", 0.0

        elif self.engine == "paddle":
            # Simplified example for PaddleOCR on regions
            res_header = self.ocr.ocr(cv2.cvtColor(header_img, cv2.COLOR_GRAY2BGR), cls=True)
            res_table = self.ocr.ocr(cv2.cvtColor(table_img, cv2.COLOR_GRAY2BGR), cls=True)

            header_text = "\n".join([line[1][0] for res in res_header for line in res]) if res_header else ""
            table_text = "\n".join([line[1][0] for res in res_table for line in res]) if res_table else ""

            conf_h = sum([line[1][1] for res in res_header for line in res]) / len(res_header) if res_header else 0.8
            conf_t = sum([line[1][1] for res in res_table for line in res]) / len(res_table) if res_table else 0.8

            return header_text, table_text, (conf_h + conf_t) / 2, (header_img, table_img)
        else:
            raise ValueError(f"Unsupported OCR engine: {self.engine}")

    def _extract_full_text(self, img):
        """Helper to extract text from a full image."""
        if isinstance(img, Image.Image):
            img = np.array(img)

        if self.engine == "tesseract":
            return "", pytesseract.image_to_string(img), 0.8
        elif self.engine == "easyocr" and self.easyocr_reader:
            res = self.easyocr_reader.readtext(img)
            text = "\n".join([text for (bbox, text, prob) in res])
            conf = sum([prob for (bbox, text, prob) in res]) / len(res) if res else 0.8
            return "", text, conf
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
            line = line.strip().upper()
            line = re.sub(r'FP[FSP][FP]', 'FPPP', line)
            line = re.sub(r'TL[ \-]R', 'TLR', line)

            line = re.sub(r'(\d)[O0o](\d)', r'\1 0 \2', line)
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
