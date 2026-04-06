import pytest
from src.validation.validator import DataValidator

def test_validator_strict():
    validator = DataValidator()
    dataset = [
        {
            "subcategory": "SS",
            "score": 105, # Invalid: Score > Total
            "total": 100,
            "extraction_confidence": 0.9,
            "source_file": "test.jpg",
            "institute_name": "IIT",
            "institute_id": "123",
            "year": "2023"
        }
    ]

    validated, manual_review = validator.validate(dataset)

    assert any("Score (105) > Total (100)" in r.get("extraction_notes", "") for r in manual_review)

def test_duplicate_detection():
    validator = DataValidator()
    dataset = [
        {"subcategory": "SS", "score": 50, "total": 100, "source_file": "test.jpg"},
        {"subcategory": "SS", "score": 55, "total": 100, "source_file": "test.jpg"}
    ]

    validated, manual_review = validator.validate(dataset)
    assert any("Duplicate found for SS" in r.get("extraction_notes", "") for r in manual_review)

def test_missing_subcategories():
    validator = DataValidator()
    dataset = [{"subcategory": "SS", "score": 50, "total": 100, "source_file": "test.jpg"}]

    validated, manual_review = validator.validate(dataset)
    assert any("Missing subcategories" in r.get("extraction_notes", "") for r in manual_review)
