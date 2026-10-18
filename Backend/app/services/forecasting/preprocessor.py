"""
=========================================================
MUGONEXT
Dataset Preprocessor
=========================================================

Cleans and prepares uploaded datasets before forecasting.

Responsibilities:
    - remove completely empty rows/columns
    - normalize column names
    - convert date columns
    - convert target columns to numeric
    - remove invalid target/date rows
    - remove duplicate rows
    - sort chronologically
    - return processing statistics

Author:
MUGONEXT
"""

from __future__ import annotations

import re

import pandas as pd


class DatasetPreprocessor:
    """
    Prepares business datasets for forecasting.
    """

    # =====================================================
    # PUBLIC API
    # =====================================================

    def process(
        self,
        dataframe: pd.DataFrame,
        target_column: str,
        date_column: str | None = None,
    ) -> tuple[pd.DataFrame, dict]:
        """
        Clean and prepare a dataframe for forecasting.

        Returns:
            (
                processed_dataframe,
                processing_metadata,
            )
        """

        if dataframe is None:
            raise ValueError(
                "Dataset cannot be None."
            )

        if dataframe.empty:
            raise ValueError(
                "Dataset is empty."
            )

        df = dataframe.copy()

        original_rows = len(df)
        original_columns = len(df.columns)

        # =================================================
        # NORMALIZE COLUMN NAMES
        # =================================================

        normalized_columns = {}

        for column in df.columns:
            original_name = str(column)

            normalized_name = (
                original_name
                .strip()
                .lower()
            )

            normalized_name = re.sub(
                r"\s+",
                "_",
                normalized_name,
            )

            normalized_name = re.sub(
                r"[^a-zA-Z0-9_]",
                "",
                normalized_name,
            )

            normalized_name = re.sub(
                r"_+",
                "_",
                normalized_name,
            ).strip("_")

            if not normalized_name:
                normalized_name = (
                    f"column_{len(normalized_columns) + 1}"
                )

            normalized_columns[original_name] = (
                normalized_name
            )

        df = df.rename(
            columns=normalized_columns
        )

        # =================================================
        # NORMALIZE REQUESTED COLUMN NAMES
        # =================================================

        target_column = self._normalize_column_name(
            target_column
        )

        if date_column is not None:
            date_column = (
                self._normalize_column_name(
                    date_column
                )
            )

        if target_column not in df.columns:
            raise ValueError(
                f"Target column '{target_column}' "
                "does not exist after column normalization."
            )

        if (
            date_column is not None
            and date_column not in df.columns
        ):
            raise ValueError(
                f"Date column '{date_column}' "
                "does not exist after column normalization."
            )

        # =================================================
        # REMOVE EMPTY COLUMNS
        # =================================================

        empty_columns = [
            column
            for column in df.columns
            if df[column].isna().all()
        ]

        if empty_columns:
            df = df.drop(
                columns=empty_columns
            )

        # =================================================
        # REMOVE COMPLETELY EMPTY ROWS
        # =================================================

        rows_before_empty_removal = len(df)

        df = df.dropna(
            how="all"
        )

        empty_rows_removed = (
            rows_before_empty_removal
            - len(df)
        )

        # =================================================
        # TARGET CONVERSION
        # =================================================

        df[target_column] = pd.to_numeric(
            df[target_column],
            errors="coerce",
        )

        # =================================================
        # DATE CONVERSION
        # =================================================

        invalid_date_rows_removed = 0

        if date_column is not None:

            parsed_dates = pd.to_datetime(
                df[date_column],
                errors="coerce",
            )

            invalid_date_rows_removed = int(
                parsed_dates.isna().sum()
            )

            df[date_column] = parsed_dates

        # =================================================
        # REMOVE INVALID TARGET ROWS
        # =================================================

        invalid_target_rows_removed = int(
            df[target_column].isna().sum()
        )

        required_columns = [
            target_column
        ]

        if date_column is not None:
            required_columns.append(
                date_column
            )

        rows_before_required_cleanup = len(df)

        df = df.dropna(
            subset=required_columns
        )

        required_rows_removed = (
            rows_before_required_cleanup
            - len(df)
        )

        # =================================================
        # DUPLICATES
        # =================================================

        duplicate_rows_removed = int(
            df.duplicated().sum()
        )

        if duplicate_rows_removed > 0:
            df = df.drop_duplicates()

        # =================================================
        # CHRONOLOGICAL SORT
        # =================================================

        if date_column is not None:
            df = (
                df.sort_values(
                    date_column
                )
                .reset_index(drop=True)
            )

        else:
            df = df.reset_index(
                drop=True
            )

        # =================================================
        # RESET INDEX
        # =================================================

        df = df.reset_index(
            drop=True
        )

        # =================================================
        # PROCESSING METADATA
        # =================================================

        metadata = {
            "original_rows": original_rows,
            "original_columns": original_columns,
            "processed_rows": int(len(df)),
            "processed_columns": int(
                len(df.columns)
            ),
            "empty_columns_removed": len(
                empty_columns
            ),
            "empty_rows_removed": int(
                empty_rows_removed
            ),
            "invalid_target_rows_removed": int(
                invalid_target_rows_removed
            ),
            "invalid_date_rows_removed": int(
                invalid_date_rows_removed
            ),
            "required_rows_removed": int(
                required_rows_removed
            ),
            "duplicate_rows_removed": int(
                duplicate_rows_removed
            ),
            "target_column": target_column,
            "date_column": date_column,
        }

        return df, metadata

    # =====================================================
    # COLUMN NORMALIZATION
    # =====================================================

    @staticmethod
    def _normalize_column_name(
        column_name: str,
    ) -> str:
        """
        Normalize a requested column name in the
        same way dataframe columns are normalized.
        """

        normalized = (
            str(column_name)
            .strip()
            .lower()
        )

        normalized = re.sub(
            r"\s+",
            "_",
            normalized,
        )

        normalized = re.sub(
            r"[^a-zA-Z0-9_]",
            "",
            normalized,
        )

        normalized = re.sub(
            r"_+",
            "_",
            normalized,
        ).strip("_")

        return normalized

    # =====================================================
    # DATA QUALITY SCORE
    # =====================================================

    @staticmethod
    def calculate_quality_score(
        dataframe: pd.DataFrame,
    ) -> float:
        """
        Calculate a simple 0-100 data quality score.

        Factors:
            - missing values
            - duplicate rows
        """

        if dataframe.empty:
            return 0.0

        total_cells = (
            len(dataframe)
            * len(dataframe.columns)
        )

        if total_cells == 0:
            return 0.0

        missing_cells = int(
            dataframe.isna().sum().sum()
        )

        duplicate_rows = int(
            dataframe.duplicated().sum()
        )

        missing_rate = (
            missing_cells / total_cells
        )

        duplicate_rate = (
            duplicate_rows / len(dataframe)
        )

        score = 100.0

        score -= (
            missing_rate * 60.0
        )

        score -= (
            duplicate_rate * 40.0
        )

        return round(
            max(
                0.0,
                min(
                    100.0,
                    score,
                ),
            ),
            2,
        )