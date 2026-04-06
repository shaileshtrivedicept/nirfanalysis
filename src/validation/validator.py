from src.validation.rules import (
    get_expected_subcategories, validate_numeric, validate_score_total_consistency
)
from src.config import CATEGORIES

class DataValidator:
    def __init__(self):
        self.expected_subcategories = get_expected_subcategories()

    def validate(self, dataset):
        """
        Validate extracted rows with strict rules:
        - Exact subcategory set (no duplicates, no missing)
        - Numeric scores/totals
        - Score <= Total
        - Category completeness
        """
        validated_dataset = []
        manual_review = []

        found_subcategories = {} # subcategory -> count

        for row in dataset:
            issues = []
            sub = row["subcategory"]
            found_subcategories[sub] = found_subcategories.get(sub, 0) + 1

            # 1. Numeric check
            if not validate_numeric(row["score"]):
                issues.append(f"Invalid score: {row['score']}")

            if row["total"] is not None:
                 if not validate_numeric(row["total"]):
                     issues.append(f"Invalid total: {row['total']}")
                 elif not validate_score_total_consistency(row["score"], row["total"]):
                     issues.append(f"Score ({row['score']}) > Total ({row['total']})")

            # 2. Multi-factor confidence scoring
            row["numeric_confidence"] = self.calculate_confidence(row, issues)

            if issues:
                row["extraction_notes"] = "; ".join(issues)
                manual_review.append(row)
            else:
                row["extraction_notes"] = ""

            validated_dataset.append(row)

        # 3. Duplicate detection
        for sub, count in found_subcategories.items():
            if count > 1:
                # Flag duplicates
                for row in validated_dataset:
                    if row["subcategory"] == sub:
                        if "Duplicate found" not in row.get("extraction_notes", ""):
                            row["extraction_notes"] = f"Duplicate found for {sub}; " + row.get("extraction_notes", "")
                            if row not in manual_review:
                                manual_review.append(row)

        # 4. Missing subcategories
        missing = set(self.expected_subcategories) - set(found_subcategories.keys())
        if missing:
             manual_review.append({
                "source_file": dataset[0]["source_file"] if dataset else "Unknown",
                "extraction_notes": f"Missing subcategories: {', '.join(missing)}"
            })

        return validated_dataset, manual_review

    def calculate_confidence(self, row, issues):
        """
        Multi-factor confidence score (0-1):
        - Base confidence (OCR level)
        - Validation success
        - Row completeness (score and total present)
        """
        score = row.get("extraction_confidence", 0.8) # Base OCR confidence

        if issues:
            score -= 0.2
        if row.get("total") is None:
            score -= 0.1
        if row.get("subcategory") not in self.expected_subcategories:
            score -= 0.3

        return max(0, min(1.0, score))
