from src.config import CATEGORIES

def get_expected_subcategories():
    """
    Flat list of all valid subcategories.
    """
    return [sub for subs in CATEGORIES.values() for sub in subs]

def validate_score(score):
    """
    Score must be numeric and >= 0.
    """
    try:
        val = float(score)
        return val >= 0
    except (TypeError, ValueError):
        return False

def validate_total(total):
    """
    Total must be numeric and > 0.
    """
    try:
        val = float(total)
        return val > 0
    except (TypeError, ValueError):
        return False
