import pytest
from src.parser.text_parser import TextParser

def test_parse_text_structured():
    parser = TextParser()
    sample_text = """
    SS FSR FQE FRU
    SCORE 50.5 40 30 20
    TOTAL 100 100 100 100
    """
    results = parser.parse_text(sample_text)

    # Check mapping by order
    ss_row = next(r for r in results if r['subcategory'] == "SS")
    assert ss_row['score'] == 50.5
    assert ss_row['total'] == 100.0

def test_parse_text_merged():
    parser = TextParser()
    sample_text = "SS 45.0 100"
    results = parser.parse_text(sample_text)
    assert any(r['subcategory'] == "SS" and r['score'] == 45.0 for r in results)

def test_extract_metadata_improved():
    parser = TextParser()
    header = "INDIAN INSTITUTE OF TECHNOLOGY MADRAS\nNIRF 2023"
    filename = "/2023/IITM/IR-E-U-0123.jpg"
    metadata = parser.extract_metadata(header, filename)

    assert metadata["institute_id"] == "IR-E-U-0123"
    assert metadata["year"] == "2023"
    assert "INDIAN INSTITUTE OF TECHNOLOGY" in metadata["institute_name"]
