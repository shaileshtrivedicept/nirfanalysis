from src.validation.rules import get_expected_subcategories, validate_score, validate_total

class DataValidator:
    def __init__(self):
        self.expected_subcategories = get_expected_subcategories()

    def validate(self, dataset):
        """
        Validate a list of extracted rows.
        Returns (validated_dataset, manual_review_needed).
        """
        validated_dataset = []
        manual_review = []

        found_subcategories = set()

        for row in dataset:
            issues = []

            # Check for subcategory validity
            if row["subcategory"] not in self.expected_subcategories:
                issues.append(f"Unknown subcategory: {row['subcategory']}")
            else:
                found_subcategories.add(row["subcategory"])

            # Check scores
            if not validate_score(row["score"]):
                issues.append(f"Invalid score: {row['score']}")

            if row["total"] is not None and not validate_total(row["total"]):
                issues.append(f"Invalid total: {row['total']}")

            # Confidence-based flagging
            if row["extraction_confidence"] < 0.8:
                issues.append(f"Low confidence ({row['extraction_confidence']})")

            if issues:
                row["extraction_notes"] = "; ".join(issues)
                manual_review.append(row)

            validated_dataset.append(row)

        # Check for missing subcategories
        missing = set(self.expected_subcategories) - found_subcategories
        if missing:
            # We don't have a specific row for missing ones,
            # so we might add dummy rows or just log it.
            # For manual_review, let's create a notification row.
            manual_review.append({
                "source_file": dataset[0]["source_file"] if dataset else "Unknown",
                "extraction_notes": f"Missing subcategories: {', '.join(missing)}"
            })

        return validated_dataset, manual_review

    def calculate_confidence(self, row):
        """
        Final confidence score for a record.
        """
        base_confidence = row.get("extraction_confidence", 0)
        # Deduct if validation fails
        if row.get("extraction_notes"):
            return max(0, base_confidence - 0.2)
        return base_confidence
