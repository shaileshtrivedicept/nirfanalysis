import re
from rapidfuzz import process, fuzz
from src.config import CATEGORIES

class TextParser:
    def __init__(self, categories=CATEGORIES):
        self.categories = categories
        self.all_subcategories = [sub for subs in categories.values() for sub in subs]

        # Define flat order for NIRF categories
        self.subcategory_order = []
        for cat in ["TLR", "RP", "GO", "OI", "PR"]:
            self.subcategory_order.extend(categories.get(cat, []))

        # Dictionary of long names for better fuzzy matching
        self.subcategory_long_names = {
            "SS": "Student Strength",
            "FSR": "Faculty Student Ratio",
            "FQE": "Faculty Quality and Experience",
            "FRU": "Financial Resources and Their Utilisation",
            "PU": "Publications",
            "QP": "Quality of Publications",
            "FPPP": "Footprint of Projects and Professional Practice",
            "GPH": "Graduation Post Graduate and Higher Studies",
            "GUE": "University Examinations",
            "MS": "Median Salary",
            "RD": "Region Diversity",
            "WD": "Women Diversity",
            "ESCS": "Economically and Socially Challenged Students",
            "PCS": "Facilities for Physically Challenged Students",
            "PR": "Peer Perception"
        }

    def parse_text(self, table_text):
        """
        Structure-aware parsing:
        1. Identify "Score" and "Total" rows.
        2. Extract numbers in sequence.
        3. Map to subcategories based on order.
        """
        results = []
        lines = table_text.split('\n')

        score_numbers = []
        total_numbers = []

        for line in lines:
            line = line.strip().upper()
            if not line:
                continue

            # Extract all numbers from the line
            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)

            # Simple heuristic: Identify if line is a "Score" or "Total" row
            # Usually NIRF tables have rows labeled "Score" and "Total"
            # Handling common misreads: 5CORE, 707AL, etc.
            # Using broader keyword list and ensuring it's not a subcategory label line
            if any(kw in line for kw in ["SCORE", "5CORE", "SC0RE", "SCRE", "POINTS"]) and not any(sub in line for sub in self.all_subcategories):
                 score_numbers.extend([float(n) for n in numbers])
            elif any(kw in line for kw in ["TOTAL", "707AL", "T0TAL", "TOT", "TTL"]) and not any(sub in line for sub in self.all_subcategories):
                 total_numbers.extend([float(n) for n in numbers])

            # Fallback: if a line contains a subcategory name AND numbers
            # (Merged line case)
            match, score, index = process.extractOne(
                line, self.all_subcategories, scorer=fuzz.WRatio
            )
            if score > 80: # Using WRatio with slightly higher threshold for better label matching
                # If we haven't found a separate Score row, we can use these
                if numbers:
                    extracted_score = float(numbers[0])
                    extracted_total = float(numbers[1]) if len(numbers) > 1 else None
                    results.append({
                        "subcategory": match,
                        "score": extracted_score,
                        "total": extracted_total,
                        "confidence": score / 100
                    })

        # If we found separate Score and Total sequences, map them by order
        if score_numbers and not results:
             for i, sub in enumerate(self.subcategory_order):
                 if i < len(score_numbers):
                     total = total_numbers[i] if i < len(total_numbers) else None
                     results.append({
                         "subcategory": sub,
                         "score": score_numbers[i],
                         "total": total,
                         "confidence": 0.9
                     })

        # Global Search fallback: if we still have nothing, try finding all keywords and the next number
        if not results:
             all_text = table_text.replace('\n', ' ')
             # track consumed content to avoid re-reading same numbers
             last_idx = 0
             for sub in self.subcategory_order:
                 long_name = self.subcategory_long_names.get(sub, "").upper()
                 best_idx = -1
                 # Try short code then long name
                 for term in [sub, long_name]:
                     if not term: continue
                     # Use word boundary search for short codes
                     if len(term) <= 4:
                         match = re.search(r'\b' + re.escape(term) + r'\b', all_text[last_idx:])
                         idx = match.start() + last_idx if match else -1
                     else:
                         idx = all_text.find(term, last_idx)

                     if idx != -1:
                         best_idx = idx
                         break

                 if best_idx != -1:
                     # Find numbers after this index but BEFORE next keyword if possible
                     search_area = all_text[best_idx:]
                     numbers = re.findall(r"[-+]?\d*\.\d+|\d+", search_area)
                     if numbers:
                         results.append({
                             "subcategory": sub,
                             "score": float(numbers[0]),
                             "total": float(numbers[1]) if len(numbers) > 1 else None,
                             "confidence": 0.7
                         })
                         # Update last_idx to consume this part of text
                         # This avoids reading the first column values for all labels
                         # Find position of the first number in the search_area
                         num_match = re.search(re.escape(numbers[0]), search_area)
                         if num_match:
                             last_idx = best_idx + num_match.end()

        return results

    def extract_metadata(self, header_text, filename):
        """
        Improved metadata extraction:
        1. Detect institute name from header/full text.
        2. Fallback to filename.
        3. Extract ID/Year from path or text.
        """
        metadata = {
            "institute_name": "Unknown",
            "institute_id": "Unknown",
            "year": "Unknown"
        }

        # Ensure header_text is string
        header_text = str(header_text or "")

        # 1. Year extraction (Path or Text)
        year_match = re.search(r"20\d{2}", filename + " " + header_text)
        if year_match:
            metadata["year"] = year_match.group(0)

        # 2. Institute ID (regex)
        id_match = re.search(r"IR-[A-Z]-[A-Z]-\d+", header_text + " " + filename)
        if id_match:
            metadata["institute_id"] = id_match.group(0)

        # 3. Institute Name (from header/full text)
        lines = [l.strip() for l in header_text.split('\n') if l.strip()]
        if lines:
            # Search for institute name in early lines, avoiding common noise
            for line in lines[:10]:
                if len(line) > 8 and not any(kw in line for kw in ["NIRF", "NATIONAL", "RANKING", "SCORE", "TOTAL", "PARAMETER", "CATEGORY"]):
                    metadata["institute_name"] = line
                    break

        # Fallback for Name from filename
        if metadata["institute_name"] == "Unknown":
            name_from_file = os.path.basename(filename).split('_')[0]
            metadata["institute_name"] = name_from_file

        return metadata
