import streamlit as st
import pandas as pd
import os
import tempfile
import numpy as np
from PIL import Image
from src.ocr.extractor import OCRExtractor
from src.parser.text_parser import TextParser
from src.parser.schema_mapper import SchemaMapper
from src.validation.validator import DataValidator
from src.output.aggregator import DatasetAggregator

st.set_page_config(page_title="NIRF Extraction Pipeline", layout="wide")

st.title("📊 NIRF Score Table Extraction")
st.markdown("Upload NIRF institute score table images to extract structured datasets.")

@st.cache_resource
def load_extractor():
    return OCRExtractor(engine="tesseract")

@st.cache_resource
def load_parser():
    return TextParser()

@st.cache_resource
def load_mapper():
    return SchemaMapper()

@st.cache_resource
def load_validator():
    return DataValidator()

@st.cache_resource
def load_aggregator():
    return DatasetAggregator()

# Sidebar options
st.sidebar.header("Options")
show_regions = st.sidebar.checkbox("Show Preprocessed Regions", value=False)
full_fallback = st.sidebar.checkbox("Full Image Fallback (if region fails)", value=True)

uploaded_files = st.file_uploader("Upload images (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner("Initializing extraction components..."):
        extractor = load_extractor()
        text_parser = load_parser()
        mapper = load_mapper()
        validator = load_validator()
        aggregator = load_aggregator()

    master_long_data = []
    all_manual_review = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, uploaded_file in enumerate(uploaded_files):
        filename = uploaded_file.name
        status_text.text(f"Processing {filename}...")

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            # 1. OCR Extraction
            header_text, table_text, ocr_confidence, (h_img, t_img) = extractor.extract_text(tmp_path)

            if show_regions and h_img is not None and t_img is not None:
                with st.expander(f"Preprocessed Regions: {filename}"):
                    st.image(h_img, caption="Header Region")
                    st.image(t_img, caption="Table Region")

            cleaned_header = extractor.context_aware_cleanup(header_text)
            cleaned_table = extractor.context_aware_cleanup(table_text)

            # 2. Text Parsing
            extracted_tokens = text_parser.parse_text(cleaned_table)

            # P10 Fallback: if region extraction yields nothing, try full image (if enabled)
            if not extracted_tokens and full_fallback:
                status_text.text(f"Region extraction failed for {filename}, trying full image...")
                _, full_text, _ = extractor._extract_full_text(Image.open(tmp_path))
                cleaned_full = extractor.context_aware_cleanup(full_text)
                extracted_tokens = text_parser.parse_text(cleaned_full)

            metadata = text_parser.extract_metadata(cleaned_header, filename)
            metadata["source_file"] = filename

            # 3. Schema Mapping
            institute_dataset = mapper.map_to_schema(extracted_tokens, metadata)

            # 4. Validation
            validated_data, manual_review = validator.validate(institute_dataset)

            master_long_data.extend(validated_data)
            all_manual_review.extend(manual_review)

        except Exception as e:
            st.error(f"Error processing {filename}: {e}")
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        progress_bar.progress((i + 1) / len(uploaded_files))

    status_text.text("Processing complete!")

    if master_long_data:
        st.subheader("📋 Extracted Data Preview")
        df_long = pd.DataFrame(master_long_data)
        st.dataframe(df_long)

        # Aggregation
        wide_data, duplicate_conflicts = aggregator.aggregate_wide(master_long_data)
        category_summary = aggregator.aggregate_category_summary(master_long_data)
        final_scores = aggregator.calculate_final_scores(category_summary)
        quality_report = aggregator.generate_quality_report(master_long_data)

        # Download Section
        st.subheader("📥 Download Datasets")
        col1, col2, col3 = st.columns(3)

        def to_csv(data):
            return pd.DataFrame(data).to_csv(index=False).encode('utf-8')

        with col1:
            st.download_button("Master Long (CSV)", to_csv(master_long_data), "master_long_dataset.csv", "text/csv", key="dl_master")
            st.download_button("Wide Summary (CSV)", to_csv(wide_data), "wide_summary.csv", "text/csv", key="dl_wide")

        with col2:
            st.download_button("Category Summary (CSV)", to_csv(category_summary), "category_summary.csv", "text/csv", key="dl_cat")
            st.download_button("Final Scores (CSV)", to_csv(final_scores), "final_score.csv", "text/csv", key="dl_final")

        with col3:
            st.download_button("Manual Review (CSV)", to_csv(all_manual_review), "manual_review.csv", "text/csv", key="dl_manual")
            st.download_button("Quality Report (CSV)", to_csv(quality_report), "extraction_quality_report.csv", "text/csv", key="dl_quality")

        if duplicate_conflicts:
            st.warning(f"⚠️ {len(duplicate_conflicts)} Duplicate conflicts detected.")
            st.download_button("Duplicate Conflicts (CSV)", to_csv(duplicate_conflicts), "duplicate_conflicts.csv", "text/csv", key="dl_duplicates")

    else:
        st.warning("No data extracted. Ensure the uploaded images are NIRF score tables.")
else:
    st.info("Please upload one or more images to begin extraction.")
