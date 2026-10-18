import pandas as pd


class DatasetValidator:
    """
    Validates datasets before forecasting.
    """

    MIN_ROWS = 5

    def validate(
        self,
        dataframe: pd.DataFrame,
        target_column: str,
        date_column: str | None = None,
    ) -> dict:
        errors: list[str] = []
        warnings: list[str] = []

        if dataframe.empty:
            errors.append("Dataset is empty.")
            return self._result(
                errors,
                warnings,
                dataframe,
                target_column,
                date_column,
            )

        # -------------------------------------------------
        # TARGET COLUMN
        # -------------------------------------------------

        if target_column not in dataframe.columns:
            errors.append(
                f"Target column '{target_column}' does not exist."
            )
        else:
            target = dataframe[target_column]

            if not pd.api.types.is_numeric_dtype(target):
                errors.append(
                    f"Target column '{target_column}' must be numeric."
                )

            missing_target = int(target.isna().sum())

            if missing_target > 0:
                warnings.append(
                    f"Target column contains "
                    f"{missing_target} missing values."
                )

        # -------------------------------------------------
        # DATE COLUMN
        # -------------------------------------------------

        if date_column:
            if date_column not in dataframe.columns:
                errors.append(
                    f"Date column '{date_column}' does not exist."
                )
            else:
                parsed_dates = pd.to_datetime(
                    dataframe[date_column],
                    errors="coerce",
                )

                invalid_dates = int(parsed_dates.isna().sum())

                if invalid_dates > 0:
                    warnings.append(
                        f"Date column contains "
                        f"{invalid_dates} invalid dates."
                    )

        # -------------------------------------------------
        # ROW COUNT
        # -------------------------------------------------

        if len(dataframe) < self.MIN_ROWS:
            errors.append(
                f"Dataset must contain at least "
                f"{self.MIN_ROWS} rows."
            )

        # -------------------------------------------------
        # DUPLICATES
        # -------------------------------------------------

        duplicate_rows = int(
            dataframe.duplicated().sum()
        )

        if duplicate_rows > 0:
            warnings.append(
                f"Dataset contains "
                f"{duplicate_rows} duplicate rows."
            )

        return self._result(
            errors,
            warnings,
            dataframe,
            target_column,
            date_column,
        )

    def _result(
        self,
        errors: list[str],
        warnings: list[str],
        dataframe: pd.DataFrame,
        target_column: str,
        date_column: str | None,
    ) -> dict:
        missing_values = int(
            dataframe.isna().sum().sum()
        )

        duplicate_rows = int(
            dataframe.duplicated().sum()
        )

        validation_passed = len(errors) == 0

        return {
            "validation_passed": validation_passed,
            "errors": errors,
            "warnings": warnings,
            "rows": int(len(dataframe)),
            "columns": int(len(dataframe.columns)),
            "missing_values_count": missing_values,
            "duplicate_rows_count": duplicate_rows,
            "target_column": target_column,
            "date_column": date_column,
        }
