import pandas as pd

class DatasetAggregator:
    def aggregate_wide(self, long_dataset):
        """
        Aggregate long-format data into a wide-format summary (one row per institute-year).
        """
        if not long_dataset:
            return []

        df = pd.DataFrame(long_dataset)

        # Check if we have necessary columns
        required_cols = ["institute_name", "institute_id", "year", "subcategory", "score"]
        if not all(col in df.columns for col in required_cols):
            return []

        # Pivot the data
        # We might have duplicates if something went wrong with extraction.
        # Use first as an aggregator.
        wide_df = df.pivot_table(
            index=["institute_name", "institute_id", "year"],
            columns="subcategory",
            values="score",
            aggfunc='first'
        ).reset_index()

        # Calculate category totals if needed (simplified)
        # Category scores are sums of subcategory scores
        # Category totals (e.g. TLR Total) can be added here as columns.

        return wide_df.to_dict(orient="records")
