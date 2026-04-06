import pytest
from src.validation.validator import DataValidator

def test_validator_basic():
    validator = DataValidator()
    dataset = [
        {
            "subcategory": "SS",
            "score": 50,
            "total": 100,
            "extraction_confidence": 0.9,
            "source_file": "test.jpg",
            "institute_name": "IIT",
            "institute_id": "123",
            "year": "2023"
        }
    ]

    validated, manual_review = validator.validate(dataset)

    assert len(validated) == 1
    # It should have a manual review entry because other subcategories are missing
    assert len(manual_review) > 0
    assert any("Missing subcategories" in r.get("extraction_notes", "") for r in manual_review)

def test_validator_low_confidence():
    validator = DataValidator()
    dataset = [
        {
            "subcategory": "SS",
            "score": 50,
            "total": 100,
            "extraction_confidence": 0.5, # Low
            "source_file": "test.jpg"
        }
    ]

    validated, manual_review = validator.validate(dataset)

    # The record itself should be in manual review due to low confidence
    assert any("Low confidence" in r.get("extraction_notes", "") for r in manual_review if r.get("subcategory") == "SS")

def test_validator_invalid_score():
    validator = DataValidator()
    dataset = [
        {
            "subcategory": "SS",
            "score": "INVALID",
            "total": 100,
            "extraction_confidence": 0.9,
            "source_file": "test.jpg"
        }
    ]

    validated, manual_review = validator.validate(dataset)
    assert any("Invalid score" in r.get("extraction_notes", "") for r in manual_review if r.get("subcategory") == "SS")
