# NIRF Extraction Pipeline

A production-grade image-to-dataset extraction pipeline for NIRF-style institute score tables.

## Project Overview

This tool automates the extraction of structured score data from NIRF table images. It follows a modular pipeline:
1.  **OCR Extraction:** Uses `pytesseract` to extract raw text.
2.  **Text Parsing:** Cleans text and extracts subcategory scores using fuzzy matching.
3.  **Schema Mapping:** Maps tokens to a canonical long-format schema.
4.  **Validation:** Validates scores, totals, and flags issues for manual review.
5.  **Export:** Generates CSV and JSON datasets.

## Setup Instructions

### Prerequisites

- Python 3.8+
- Tesseract OCR engine

#### Install Tesseract

- **Ubuntu:** `sudo apt-get install tesseract-ocr`
- **macOS:** `brew install tesseract`
- **Windows:** Download and install from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).

### Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run CLI

Place your image files in `data/raw/` and run:

```bash
python3 -m src.main --input-dir data/raw --output-dir data/processed
```

### CLI Arguments

- `--input-dir`: Path to folder containing jpg/png images (default: `data/raw`).
- `--output-dir`: Path for generated datasets (default: `data/processed`).
- `--ocr-engine`: Choice of `tesseract` or `paddle` (default: `tesseract`).
- `--export-json`: Export intermediate extraction results as JSON files.
- `--log-level`: Set logging level (e.g., INFO, DEBUG).

## Sample Output

The pipeline produces the following files in the output directory:

1.  `master_long_dataset.csv`: Complete dataset in long format.
2.  `wide_summary.csv`: Pivot-ready summary (one row per institute-year).
3.  `manual_review.csv`: Records flagged for low confidence or missing data.
4.  `failed_files.csv`: List of images that could not be processed.
5.  `processing.log`: Detailed execution log.

## Domain Schema

The pipeline expects the following NIRF categories and subcategories:

- **TLR** (Teaching, Learning & Resources): SS, FSR, FQE, FRU
- **RP** (Research and Professional Practice): PU, QP, FPPP
- **GO** (Graduation Outcomes): GPH, GUE, MS
- **OI** (Outreach and Inclusivity): RD, WD, ESCS, PCS
- **PR** (Perception): PR

## Known Limitations

- OCR accuracy depends on image quality.
- Complex table layouts may require custom preprocessing.
- Multi-page tables are not supported in the current version.

## Future Improvements

- Integrate PaddleOCR for improved accuracy on complex backgrounds.
- Add support for PDF inputs.
- Implement more sophisticated table-region detection.
