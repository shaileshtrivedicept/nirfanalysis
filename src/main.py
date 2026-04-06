import argparse
import os
import sys
from src.config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR, DEFAULT_OCR_ENGINE,
    MASTER_LONG_FILENAME, WIDE_SUMMARY_FILENAME,
    MANUAL_REVIEW_FILENAME, FAILED_FILES_FILENAME, LOG_FILENAME
)
from src.utils.logger import setup_logger
from src.utils.file_utils import get_image_files, ensure_dir
from src.ocr.extractor import OCRExtractor
from src.parser.text_parser import TextParser
from src.parser.schema_mapper import SchemaMapper
from src.validation.validator import DataValidator
from src.output.writer import DatasetWriter
from src.output.aggregator import DatasetAggregator

def main():
    parser = argparse.ArgumentParser(description="NIRF Extraction Pipeline CLI")
    parser.add_argument("--input-dir", default=RAW_DATA_DIR, help="Path to input images")
    parser.add_argument("--output-dir", default=PROCESSED_DATA_DIR, help="Path for outputs")
    parser.add_argument("--ocr-engine", default=DEFAULT_OCR_ENGINE, choices=["tesseract", "paddle"], help="OCR engine to use")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--save-debug-crops", action="store_true", help="Save preprocessed images")
    parser.add_argument("--export-json", action="store_true", help="Export intermediate JSON")

    args = parser.parse_args()

    # Setup
    ensure_dir(args.output_dir)
    log_file = os.path.join(args.output_dir, LOG_FILENAME)
    logger = setup_logger(log_file=log_file, level=args.log_level)
    logger.info("Starting NIRF Extraction Pipeline")

    extractor = OCRExtractor(engine=args.ocr_engine)
    text_parser = TextParser()
    mapper = SchemaMapper()
    validator = DataValidator()
    writer = DatasetWriter(args.output_dir)
    aggregator = DatasetAggregator()

    image_files = get_image_files(args.input_dir)
    if not image_files:
        logger.warning(f"No image files found in {args.input_dir}")
        return

    master_long_data = []
    all_manual_review = []
    failed_files = []

    for img_path in image_files:
        filename = os.path.basename(img_path)
        logger.info(f"Processing {filename}...")

        try:
            # 1. OCR Extraction
            debug_dir = os.path.join(args.output_dir, "debug_crops") if args.save_debug_crops else None
            header_text, table_text, ocr_confidence, _ = extractor.extract_text(
                img_path, save_debug=args.save_debug_crops, debug_dir=debug_dir
            )
            cleaned_header = extractor.context_aware_cleanup(header_text)
            cleaned_table = extractor.context_aware_cleanup(table_text)

            # 2. Text Parsing
            extracted_tokens = text_parser.parse_text(cleaned_table)
            metadata = text_parser.extract_metadata(cleaned_header, filename)
            metadata["source_file"] = filename

            # 3. Schema Mapping
            institute_dataset = mapper.map_to_schema(extracted_tokens, metadata)

            # 4. Validation
            validated_data, manual_review = validator.validate(institute_dataset)

            master_long_data.extend(validated_data)
            all_manual_review.extend(manual_review)

            if args.export_json:
                writer.export_json(validated_data, f"{os.path.splitext(filename)[0]}.json")

        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            failed_files.append({"file": filename, "error": str(e)})

    # 5. Export
    logger.info("Exporting results...")
    writer.export_csv(master_long_data, MASTER_LONG_FILENAME)

    wide_data, duplicate_conflicts = aggregator.aggregate_wide(master_long_data)
    writer.export_csv(wide_data, WIDE_SUMMARY_FILENAME)
    writer.export_csv(duplicate_conflicts, "duplicate_conflicts.csv") # P5

    # P10: Benchmarking Outputs
    category_summary = aggregator.aggregate_category_summary(master_long_data)
    writer.export_csv(category_summary, "category_summary.csv")

    final_scores = aggregator.calculate_final_scores(category_summary)
    writer.export_csv(final_scores, "final_score.csv")

    quality_report = aggregator.generate_quality_report(master_long_data)
    writer.export_csv(quality_report, "extraction_quality_report.csv")

    writer.export_csv(all_manual_review, MANUAL_REVIEW_FILENAME)
    writer.export_csv(failed_files, FAILED_FILES_FILENAME)

    logger.info(f"Pipeline complete. Outputs saved to {args.output_dir}")

if __name__ == "__main__":
    main()
