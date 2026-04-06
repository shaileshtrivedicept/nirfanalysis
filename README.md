# NIRF Extraction Pipeline (Production Grade)

A robust, end-to-end image-to-dataset extraction pipeline for NIRF-style institute score tables.

## Pipeline Architecture

1.  **Preprocessing & Detection:**
    *   Adaptive thresholding for varied lighting.
    *   CLAHE for contrast enhancement.
    *   Table region isolation (bottom 70% of image).
    *   Hough line / minAreaRect-based deskewing.
2.  **OCR Extraction:**
    *   Separate OCR for Header (title) and Table regions.
    *   Context-aware cleanup (regex-based corrections for O/0, I/1, FPPP, etc.).
3.  **Structure-Aware Parsing:**
    *   Identifies "Score" and "Total" rows.
    *   Maps numeric sequences to subcategories based on expected NIRF order.
    *   Fallbacks for merged lines and partial OCR results.
4.  **Harden Validation:**
    *   Enforces Score <= Total.
    *   Detects duplicates and missing categories.
    *   Multi-factor confidence scoring (OCR level, validation success, completeness).
5.  **Benchmarking Exports:**
    *   Long-format CSV (`master_long_dataset.csv`).
    *   Wide summary with duplicate handling (`wide_summary.csv`).
    *   Category aggregated summary (`category_summary.csv`).
    *   Weighted final scores (`final_score.csv`).
    *   Extraction quality report (`extraction_quality_report.csv`).

## How to Run

```bash
python3 -m src.main --input-dir data/raw --output-dir data/processed --save-debug-crops
```

## Validation Rules

- `Score` and `Total` must be numeric.
- `Score` must be less than or equal to `Total`.
- All NIRF subcategories (TLR, RP, GO, OI, PR) must be present.
- Duplicates are flagged and logged in `duplicate_conflicts.csv`.

## Confidence Scoring

The `numeric_confidence` (0-1) is calculated based on:
- Average OCR confidence.
- Presence of validation issues (Score > Total).
- Row completeness (presence of both score and total).
- Correct mapping of subcategory labels.

## Benchmarking Outputs

- `final_score.csv`: Uses weights: TLR (0.3), RP (0.3), GO (0.2), OI (0.1), PR (0.1).
- `extraction_quality_report.csv`: Provides file-level average confidence and aggregated issues.
