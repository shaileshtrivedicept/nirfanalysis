from src.ocr.extractor import OCRExtractor
import numpy as np

def test_ocr_extractor_fallback():
    # In this environment, tesseract is not installed, so it should fallback to EasyOCR
    extractor = OCRExtractor(engine="tesseract")
    assert extractor.engine == "easyocr"
    assert extractor.easyocr_reader is not None

def test_ocr_extraction_dummy():
    extractor = OCRExtractor()
    # Create a dummy white image
    dummy_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    # Just check if it runs without crashing
    header, table, conf = extractor._extract_full_text(dummy_img)
    assert isinstance(header, str)
    assert isinstance(table, str)
