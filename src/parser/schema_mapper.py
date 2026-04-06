from src.config import CATEGORIES

class SchemaMapper:
    def __init__(self, categories=CATEGORIES):
        self.categories = categories
        # Invert category map for easy lookup
        self.subcategory_to_category = {
            sub: cat for cat, subs in categories.items() for sub in subs
        }

    def map_to_schema(self, extracted_tokens, metadata):
        """
        Map extracted tokens to a structured long format.
        """
        long_format_data = []

        for token in extracted_tokens:
            subcategory = token.get("subcategory")
            category = self.subcategory_to_category.get(subcategory, "Unknown")

            row = {
                "source_file": metadata.get("source_file"),
                "institute_name": metadata.get("institute_name"),
                "institute_id": metadata.get("institute_id"),
                "year": metadata.get("year"),
                "category": category,
                "subcategory": subcategory,
                "score": token.get("score"),
                "total": token.get("total"),
                "normalized_score": self.calculate_normalized(token.get("score"), token.get("total")),
                "extraction_confidence": token.get("confidence"),
                "extraction_notes": ""
            }
            long_format_data.append(row)

        return long_format_data

    def calculate_normalized(self, score, total):
        """
        Normalize scores (score / total).
        """
        if total and total > 0:
            # P7: normalized_score = score / total (NOT multiplied by 100)
            return round((score / total), 4)
        return None
