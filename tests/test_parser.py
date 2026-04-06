import pytest
from src.parser.text_parser import TextParser

def test_parse_text_basic():
    parser = TextParser()
    sample_text = """
    NIRF 2023 DATA
    SS 50.5 100
    FSR 40 100
    FQE 30 100
    FRU 20 100
    """
    results = parser.parse_text(sample_text)

    # Check if we got results for subcategories
    subcategories = [r['subcategory'] for r in results]
    assert "SS" in subcategories
    assert "FSR" in subcategories
    assert "FQE" in subcategories
    assert "FRU" in subcategories

    # Check values
    ss_row = next(r for r in results if r['subcategory'] == "SS")
    assert ss_row['score'] == 50.5
    assert ss_row['total'] == 100.0

def test_parse_text_fuzzy():
    parser = TextParser()
    sample_text = "S.S. 45.0 100" # Slightly different from SS
    results = parser.parse_text(sample_text)
    assert any(r['subcategory'] == "SS" for r in results)

def test_extract_metadata():
    parser = TextParser()
    text = "IIT MADRAS\nNIRF 2023"
    filename = "IR-E-U-0123_2023.jpg"
    metadata = parser.extract_metadata(text, filename)

    assert metadata["institute_id"] == "IR-E-U-0123"
    assert metadata["year"] == "2023"
    assert "IIT MADRAS" in metadata["institute_name"]
