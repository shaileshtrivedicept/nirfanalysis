import re
from rapidfuzz import process, fuzz
from src.config import CATEGORIES

class TextParser:
    def __init__(self, categories=CATEGORIES):
        self.categories = categories
        self.all_subcategories = [sub for subs in categories.values() for sub in subs]
        self.all_categories = list(categories.keys())

    def parse_text(self, text):
        """
        Extract numerical scores and subcategories from text.
        """
        results = []
        lines = text.split('\n')

        # We need a robust strategy. OCR text is often messy.
        # NIRF format usually has subcategory names and scores next to each other.

        # Simple extraction logic:
        # 1. Search for subcategory name in line (fuzzy)
        # 2. Extract numbers in that line

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for subcategories
            # Using WRatio for better fuzzy matching on short strings
            match, score, index = process.extractOne(
                line, self.all_subcategories, scorer=fuzz.WRatio
            )

            # Confidence threshold for fuzzy matching
            if score > 60: # Lowered threshold slightly for WRatio and short subcategories
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if numbers:
                    # Taking the first number as score and the second as total if available
                    extracted_score = float(numbers[0])
                    extracted_total = float(numbers[1]) if len(numbers) > 1 else None

                    results.append({
                        "subcategory": match,
                        "score": extracted_score,
                        "total": extracted_total,
                        "confidence": score / 100
                    })

        return results

    def extract_metadata(self, text, filename):
        """
        Try to extract institute name, ID, and year.
        """
        metadata = {
            "institute_name": "Unknown",
            "institute_id": "Unknown",
            "year": "Unknown"
        }

        # Check filename for ID and Year
        # Example: IR-E-U-0123_2023.jpg
        id_match = re.search(r"IR-[A-Z]-[A-Z]-\d+", filename)
        if id_match:
            metadata["institute_id"] = id_match.group(0)

        year_match = re.search(r"20\d{2}", filename)
        if year_match:
            metadata["year"] = year_match.group(0)

        # Name is harder from messy OCR, often first few lines
        # This is very naive but provides a starting point
        lines = [l for l in text.split('\n') if l.strip()]
        if lines:
            metadata["institute_name"] = lines[0][:100]

        return metadata
