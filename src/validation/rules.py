from src.config import CATEGORIES

def get_expected_subcategories():
    """
    Flat list of all valid subcategories in expected order.
    """
    expected = []
    for cat in ["TLR", "RP", "GO", "OI", "PR"]:
        expected.extend(CATEGORIES.get(cat, []))
    return expected

def validate_score_total_consistency(score, total):
    """
    Rule: Score <= Total.
    """
    if score is None or total is None:
        return True
    return score <= total

def validate_numeric(val):
    """
    Check if value is numeric and >= 0.
    """
    try:
        fval = float(val)
        return fval >= 0
    except (TypeError, ValueError):
        return False

def get_subcategory_sanity_range(subcategory):
    """
    Define sanity ranges for totals/scores (example).
    """
    # Most subcategories are out of 100 or 50.
    return (0, 101)
