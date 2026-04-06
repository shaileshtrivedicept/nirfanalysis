import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# Ensure directories exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Domain Schema
CATEGORIES = {
    "TLR": ["SS", "FSR", "FQE", "FRU"],
    "RP": ["PU", "QP", "FPPP"],
    "GO": ["GPH", "GUE", "MS"],
    "OI": ["RD", "WD", "ESCS", "PCS"],
    "PR": ["PR"]
}

CATEGORY_WEIGHTS = {
    "TLR": 0.30,
    "RP": 0.30,
    "GO": 0.20,
    "OI": 0.10,
    "PR": 0.10
}

# OCR Config
DEFAULT_OCR_ENGINE = "tesseract"
SUPPORTED_OCR_ENGINES = ["tesseract", "paddle"]

# Validation Rules
SCORE_PRECISION = 2

# Output Filenames
MASTER_LONG_FILENAME = "master_long_dataset.csv"
WIDE_SUMMARY_FILENAME = "wide_summary.csv"
MANUAL_REVIEW_FILENAME = "manual_review.csv"
FAILED_FILES_FILENAME = "failed_files.csv"
LOG_FILENAME = "processing.log"
