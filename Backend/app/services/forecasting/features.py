from __future__ import annotations

import numpy as np
import pandas as pd


class ForecastFeatureEngineer:
    """
    Feature engineering for MUGONEXT time-series forecasting.

    Creates forecasting-safe features:

        - trend/time index
        - calendar features
        - cyclical calendar features
        - lag features
        - rolling statistics
        - polynomial trend

    Raw external numeric columns such as quantity, price, cost,
    revenue, etc. are preserved in the dataframe but are NOT
    automatically treated as future forecasting features unless
    future values are explicitly supplied.
    """

    def __init__(
        self,
        lags: tuple[int, ...] = (1, 7, 14, 30),
        rolling_windows: tuple[int, ...] = (7, 14, 30),
    ):
        self.lags = lags
        self.rolling_windows = rolling_windows

    # =========================================================
    # ENGINEERED FEATURE NAMES
    # =========================================================

    def get_engineered_feature_columns(self) -> list[str]:
        """
        Return the features that MUGONEXT can generate for
        both historical data and future forecast dates.
        """

        columns = [
            "time_index",
            "day_of_week",
            "day_of_month",
            "month",
            "quarter",
            "week_of_year",
            "day_of_year",
            "day_of_week_sin",
            "day_of_week_cos",
            "month_sin",
            "month_cos",
            "day_of_year_sin",
            "day_of_year_cos",
            "time_index_squared",
        ]

        for lag in self.lags:
            columns.append(f"lag_{lag}")

        for window in self.rolling_windows:
            columns.append(f"rolling_mean_{window}")
            columns.append(f"rolling_std_{window}")

        return columns

    # =========================================================
    # PUBLIC API
    # =========================================================

    def create_features(
        self,
        dataframe: pd.DataFrame,
        date_column: str,
        target_column: str,
        include_target: bool = True,
    ) -> pd.DataFrame:

        if date_column not in dataframe.columns:
            raise ValueError(
                f"Date column '{date_column}' not found."
            )

        if target_column not in dataframe.columns:
            raise ValueError(
                f"Target column '{target_column}' not found."
            )

        df = dataframe.copy()

        # -----------------------------------------------------
        # CLEAN DATE / TARGET
        # -----------------------------------------------------

        df[date_column] = pd.to_datetime(
            df[date_column],
            errors="coerce",
        )

        df[target_column] = pd.to_numeric(
            df[target_column],
            errors="coerce",
        )

        df = df.dropna(
            subset=[
                date_column,
                target_column,
            ]
        )

        if len(df) < 2:
            raise ValueError(
                "At least two valid observations are required."
            )

        # -----------------------------------------------------
        # SORT CHRONOLOGICALLY
        # -----------------------------------------------------

        df = (
            df.sort_values(date_column)
            .reset_index(drop=True)
        )

        # -----------------------------------------------------
        # TIME INDEX
        # -----------------------------------------------------

        df["time_index"] = np.arange(
            len(df),
            dtype=float,
        )

        # -----------------------------------------------------
        # CALENDAR FEATURES
        # -----------------------------------------------------

        df["day_of_week"] = (
            df[date_column].dt.dayofweek
        )

        df["day_of_month"] = (
            df[date_column].dt.day
        )

        df["month"] = (
            df[date_column].dt.month
        )

        df["quarter"] = (
            df[date_column].dt.quarter
        )

        df["week_of_year"] = (
            df[date_column]
            .dt.isocalendar()
            .week
            .astype(int)
        )

        df["day_of_year"] = (
            df[date_column].dt.dayofyear
        )

        # -----------------------------------------------------
        # CYCLICAL FEATURES
        # -----------------------------------------------------

        df["day_of_week_sin"] = np.sin(
            2 * np.pi * df["day_of_week"] / 7
        )

        df["day_of_week_cos"] = np.cos(
            2 * np.pi * df["day_of_week"] / 7
        )

        df["month_sin"] = np.sin(
            2 * np.pi * df["month"] / 12
        )

        df["month_cos"] = np.cos(
            2 * np.pi * df["month"] / 12
        )

        df["day_of_year_sin"] = np.sin(
            2 * np.pi * df["day_of_year"] / 365.25
        )

        df["day_of_year_cos"] = np.cos(
            2 * np.pi * df["day_of_year"] / 365.25
        )

        # -----------------------------------------------------
        # LAG FEATURES
        # -----------------------------------------------------

        for lag in self.lags:
            df[f"lag_{lag}"] = (
                df[target_column].shift(lag)
            )

        # -----------------------------------------------------
        # ROLLING FEATURES
        # -----------------------------------------------------

        shifted_target = (
            df[target_column].shift(1)
        )

        for window in self.rolling_windows:

            df[f"rolling_mean_{window}"] = (
                shifted_target
                .rolling(
                    window=window,
                    min_periods=1,
                )
                .mean()
            )

            df[f"rolling_std_{window}"] = (
                shifted_target
                .rolling(
                    window=window,
                    min_periods=2,
                )
                .std()
                .fillna(0)
            )

        # -----------------------------------------------------
        # TREND
        # -----------------------------------------------------

        df["time_index_squared"] = (
            df["time_index"] ** 2
        )

        # -----------------------------------------------------
        # REMOVE ROWS WITHOUT REQUIRED LAGS
        # -----------------------------------------------------

        if self.lags:

            max_lag = max(self.lags)

            if len(df) > max_lag:
                df = (
                    df.iloc[max_lag:]
                    .reset_index(drop=True)
                )

        # -----------------------------------------------------
        # CLEAN NUMERIC FEATURES
        # -----------------------------------------------------

        numeric_columns = (
            df.select_dtypes(
                include=[np.number]
            ).columns
        )

        df[numeric_columns] = (
            df[numeric_columns]
            .replace(
                [np.inf, -np.inf],
                np.nan,
            )
        )

        # Only engineered features are required to be complete.
        engineered_columns = (
            self.get_engineered_feature_columns()
        )

        available_engineered = [
            column
            for column in engineered_columns
            if column in df.columns
        ]

        df = (
            df.dropna(
                subset=available_engineered
            )
            .reset_index(drop=True)
        )

        # -----------------------------------------------------
        # KEEP / REMOVE TARGET
        # -----------------------------------------------------

        if not include_target:
            df = df.drop(
                columns=[target_column]
            )

        return df

    # =========================================================
    # FEATURE COLUMN DISCOVERY
    # =========================================================

    def get_feature_columns(
        self,
        dataframe: pd.DataFrame,
        date_column: str,
        target_column: str,
    ) -> list[str]:
        """
        Return only forecasting-safe engineered features.

        IMPORTANT:
        Raw numeric columns such as quantity, price, cost, etc.
        are intentionally excluded because their future values
        are unknown unless explicitly provided.
        """

        engineered_columns = (
            self.get_engineered_feature_columns()
        )

        return [
            column
            for column in engineered_columns
            if column in dataframe.columns
            and pd.api.types.is_numeric_dtype(
                dataframe[column]
            )
        ]

    # =========================================================
    # FUTURE CALENDAR FEATURES
    # =========================================================

    def create_calendar_features(
        self,
        dates: pd.DatetimeIndex | list[pd.Timestamp],
        start_time_index: int = 0,
    ) -> pd.DataFrame:

        dates = pd.DatetimeIndex(
            pd.to_datetime(dates)
        )

        df = pd.DataFrame(
            {
                "date": dates,
            }
        )

        df["time_index"] = np.arange(
            start_time_index,
            start_time_index + len(df),
            dtype=float,
        )

        df["day_of_week"] = (
            df["date"].dt.dayofweek
        )

        df["day_of_month"] = (
            df["date"].dt.day
        )

        df["month"] = (
            df["date"].dt.month
        )

        df["quarter"] = (
            df["date"].dt.quarter
        )

        df["week_of_year"] = (
            df["date"]
            .dt.isocalendar()
            .week
            .astype(int)
        )

        df["day_of_year"] = (
            df["date"].dt.dayofyear
        )

        # -----------------------------------------------------
        # CYCLICAL FEATURES
        # -----------------------------------------------------

        df["day_of_week_sin"] = np.sin(
            2 * np.pi * df["day_of_week"] / 7
        )

        df["day_of_week_cos"] = np.cos(
            2 * np.pi * df["day_of_week"] / 7
        )

        df["month_sin"] = np.sin(
            2 * np.pi * df["month"] / 12
        )

        df["month_cos"] = np.cos(
            2 * np.pi * df["month"] / 12
        )

        df["day_of_year_sin"] = np.sin(
            2 * np.pi * df["day_of_year"] / 365.25
        )

        df["day_of_year_cos"] = np.cos(
            2 * np.pi * df["day_of_year"] / 365.25
        )

        df["time_index_squared"] = (
            df["time_index"] ** 2
        )

        return df