import pandas as pd
from src.config import CATEGORY_WEIGHTS

class DatasetAggregator:
    def aggregate_wide(self, long_dataset):
        """
        Aggregate long-format data into a wide-format summary.
        Includes duplicate detection (P5).
        """
        if not long_dataset:
            return [], []

        df = pd.DataFrame(long_dataset)

        # P5: Explicit duplicate detection
        duplicates = df[df.duplicated(subset=["institute_id", "year", "subcategory"], keep=False)]

        # Pivot the data, but handle duplicates by taking the highest confidence one if exists
        # or just the first if multiple exist after cleanup.
        # However, for wide summary, we should exclude them if they are conflicting.

        # Filter out duplicates for the main wide summary to ensure clean data
        clean_df = df.drop_duplicates(subset=["institute_id", "year", "subcategory"], keep='first')

        wide_df = clean_df.pivot_table(
            index=["institute_name", "institute_id", "year"],
            columns="subcategory",
            values="score",
            aggfunc='first'
        ).reset_index()

        return wide_df.to_dict(orient="records"), duplicates.to_dict(orient="records")

    def aggregate_category_summary(self, long_dataset):
        """
        Aggregate TLR, RP, GO, OI, PR per institute-year (P10.1).
        """
        if not long_dataset:
            return []

        df = pd.DataFrame(long_dataset)
        category_summary = df.groupby(["institute_name", "institute_id", "year", "category"])["score"].sum().reset_index()

        # Pivot to have categories as columns
        summary_wide = category_summary.pivot_table(
            index=["institute_name", "institute_id", "year"],
            columns="category",
            values="score",
            aggfunc='first'
        ).reset_index()

        return summary_wide.to_dict(orient="records")

    def calculate_final_scores(self, category_summary_data):
        """
        Calculate weighted final score (P10.2).
        """
        if not category_summary_data:
            return []

        df = pd.DataFrame(category_summary_data)

        def calculate_weighted(row):
            total_score = 0
            for cat, weight in CATEGORY_WEIGHTS.items():
                total_score += row.get(cat, 0) * weight
            return round(total_score, 4)

        df["final_score"] = df.apply(calculate_weighted, axis=1)
        return df.to_dict(orient="records")

    def generate_quality_report(self, long_dataset):
        """
        Generate extraction quality report (P10.3).
        """
        if not long_dataset:
            return []

        df = pd.DataFrame(long_dataset)
        quality = df.groupby(["source_file", "institute_id", "year"]).agg({
            "extraction_confidence": "mean",
            "extraction_notes": lambda x: "; ".join([n for n in x if n])
        }).reset_index()

        return quality.to_dict(orient="records")
