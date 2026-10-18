
"""
=========================================================
MUGONEXT
Forecast Engine
=========================================================

Main forecasting engine responsible for:

    - Dataset loading
    - Data validation
    - Column resolution
    - Feature engineering
    - Automatic model selection
    - Chronological validation
    - Final model training
    - Recursive forecast generation
    - Confidence intervals
    - Feature importance
    - Forecast explanation

Author:
MUGONEXT
"""

from __future__ import annotations

from dataclasses import dataclass
import re

import numpy as np
import pandas as pd

from app.services.forecasting.confidence import (
    ForecastConfidenceCalculator,
)
from app.services.forecasting.features import (
    ForecastFeatureEngineer,
)
from app.services.forecasting.loader import (
    DatasetLoader,
)
from app.services.forecasting.model_selector import (
    ForecastModelSelector,
)


# =========================================================
# FORECAST RESULT
# =========================================================

@dataclass
class ForecastResult:
    """
    Complete result returned by ForecastEngine.
    """

    predictions: list[dict]
    model: str
    forecast_periods: int
    target_column: str
    date_column: str

    mae: float | None
    mse: float | None
    rmse: float | None
    mape: float | None
    r_squared: float | None

    accuracy_score: float | None
    confidence_score: float | None

    confidence_intervals: list[dict] | None
    feature_importance: dict | None

    ai_explanation: str


# =========================================================
# FORECAST ENGINE
# =========================================================

class ForecastEngine:
    """
    Main MUGONEXT forecasting engine.

    Pipeline:

        Dataset
            ↓
        Column resolution
            ↓
        Data cleaning
            ↓
        Feature engineering
            ↓
        Chronological validation
            ↓
        Model selection
            ↓
        Final model training
            ↓
        Recursive future forecasting
            ↓
        Confidence intervals
            ↓
        ForecastResult
    """

    # =====================================================
    # CONFIGURATION
    # =====================================================

    MODEL_SELECTION_MIN_OBSERVATIONS = 10

    # Prevent extremely large datasets from making the
    # forecasting engine unnecessarily slow.
    MAX_TRAINING_ROWS = 20000

    # Validation must contain enough observations to
    # produce meaningful metrics.
    MIN_VALIDATION_OBSERVATIONS = 3

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.loader = DatasetLoader()

        self.feature_engineer = ForecastFeatureEngineer()

        self.model_selector = ForecastModelSelector()

        self.confidence_calculator = (
            ForecastConfidenceCalculator()
        )

    # =====================================================
    # COLUMN NORMALIZATION
    # =====================================================

    @staticmethod
    def _normalize_column_name(
        column_name: str,
    ) -> str:
        """
        Normalize a column name for matching.

        Examples:

            Latest Launch  -> latest_launch
            latest launch  -> latest_launch
            LATEST LAUNCH  -> latest_launch
            latest-launch  -> latest_launch
            Latest_Launch  -> latest_launch

        Only used for matching.
        The original dataframe column is preserved.
        """

        normalized = str(
            column_name
        ).strip().lower()

        normalized = re.sub(
            r"[\s\-]+",
            "_",
            normalized,
        )

        normalized = re.sub(
            r"[^a-z0-9_]",
            "",
            normalized,
        )

        normalized = re.sub(
            r"_+",
            "_",
            normalized,
        )

        return normalized.strip("_")

    # =====================================================
    # COLUMN RESOLUTION
    # =====================================================

    @classmethod
    def _resolve_column_name(
        cls,
        dataframe: pd.DataFrame,
        requested_column: str,
        column_type: str,
    ) -> str:
        """
        Resolve a requested column against the actual
        dataframe columns.

        This handles differences such as:

            latest_launch
            Latest_Launch
            Latest Launch
            latest-launch
            LATEST LAUNCH
        """

        if not requested_column:
            raise ValueError(
                f"{column_type.capitalize()} column "
                "must be provided."
            )

        # -------------------------------------------------
        # Exact match
        # -------------------------------------------------

        if requested_column in dataframe.columns:
            return requested_column

        requested_normalized = (
            cls._normalize_column_name(
                requested_column
            )
        )

        # -------------------------------------------------
        # Normalized match
        # -------------------------------------------------

        matches = []

        for column in dataframe.columns:

            normalized_column = (
                cls._normalize_column_name(
                    column
                )
            )

            if normalized_column == requested_normalized:
                matches.append(column)

        if len(matches) == 1:
            return matches[0]

        if len(matches) > 1:
            raise ValueError(
                f"Multiple {column_type} columns match "
                f"'{requested_column}': {matches}. "
                "Please select the exact column."
            )

        # -------------------------------------------------
        # Helpful error
        # -------------------------------------------------

        available_columns = [
            str(column)
            for column in dataframe.columns
        ]

        raise ValueError(
            f"{column_type.capitalize()} column "
            f"'{requested_column}' not found. "
            f"Available columns: {available_columns}"
        )

    # =====================================================
    # MINIMUM DATA REQUIREMENT
    # =====================================================

    def _minimum_required_observations(
        self,
    ) -> int:
        """
        Calculate minimum raw observations required
        by the current feature-engineering setup.
        """

        max_lag = max(
            self.feature_engineer.lags,
            default=0,
        )

        return max(
            self.MODEL_SELECTION_MIN_OBSERVATIONS
            + max_lag,
            10,
        )

    # =====================================================
    # DATE FREQUENCY
    # =====================================================

    def _get_date_offset(
        self,
        frequency: str,
    ):
        """
        Return the appropriate date offset.
        """

        frequency = frequency.lower()

        if frequency == "daily":
            return pd.Timedelta(days=1)

        if frequency == "weekly":
            return pd.Timedelta(weeks=1)

        if frequency == "monthly":
            return None

        raise ValueError(
            "Unsupported frequency. "
            "Use daily, weekly, or monthly."
        )

    # =====================================================
    # MODEL FACTORY
    # =====================================================

    def _create_model(
        self,
        model_name: str,
    ):
        """
        Create a fresh instance of a selected model.
        """

        models = self.model_selector.models

        if model_name not in models:
            raise ValueError(
                f"Unsupported forecasting model: "
                f"{model_name}"
            )

        model_template = models[model_name]

        model_class = (
            model_template.__class__
        )

        model_params = (
            model_template.get_params()
        )

        return model_class(
            **model_params
        )

    # =====================================================
    # LARGE DATASET TRAINING LIMIT
    # =====================================================

    def _limit_training_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Limit expensive final ML training for very large
        datasets.

        Most recent observations are retained because they
        represent the latest business behavior.
        """

        if len(X) <= self.MAX_TRAINING_ROWS:
            return X, y

        print(
            "[ForecastEngine] "
            f"Large training dataset detected: "
            f"{len(X):,} rows. "
            f"Using latest "
            f"{self.MAX_TRAINING_ROWS:,} rows."
        )

        X_training = (
            X.tail(
                self.MAX_TRAINING_ROWS
            )
            .reset_index(drop=True)
        )

        y_training = (
            y.tail(
                self.MAX_TRAINING_ROWS
            )
            .reset_index(drop=True)
        )

        return X_training, y_training

    # =====================================================
    # FUTURE FEATURES
    # =====================================================

    def _build_future_features(
        self,
        history: pd.DataFrame,
        date_column: str,
        target_column: str,
        future_date: pd.Timestamp,
    ) -> pd.DataFrame:
        """
        Build forecasting features for one future period.
        """

        target_history = (
            history[target_column]
            .astype(float)
        )

        time_index = float(
            len(history)
        )

        future = pd.DataFrame(
            {
                "date": [future_date],
            }
        )

        # -------------------------------------------------
        # TIME
        # -------------------------------------------------

        future["time_index"] = time_index

        # -------------------------------------------------
        # CALENDAR
        # -------------------------------------------------

        future["day_of_week"] = (
            future["date"].dt.dayofweek
        )

        future["day_of_month"] = (
            future["date"].dt.day
        )

        future["month"] = (
            future["date"].dt.month
        )

        future["quarter"] = (
            future["date"].dt.quarter
        )

        future["week_of_year"] = (
            future["date"]
            .dt.isocalendar()
            .week
            .astype(int)
        )

        future["day_of_year"] = (
            future["date"].dt.dayofyear
        )

        # -------------------------------------------------
        # CYCLICAL FEATURES
        # -------------------------------------------------

        future["day_of_week_sin"] = (
            np.sin(
                2
                * np.pi
                * future["day_of_week"]
                / 7
            )
        )

        future["day_of_week_cos"] = (
            np.cos(
                2
                * np.pi
                * future["day_of_week"]
                / 7
            )
        )

        future["month_sin"] = (
            np.sin(
                2
                * np.pi
                * future["month"]
                / 12
            )
        )

        future["month_cos"] = (
            np.cos(
                2
                * np.pi
                * future["month"]
                / 12
            )
        )

        future["day_of_year_sin"] = (
            np.sin(
                2
                * np.pi
                * future["day_of_year"]
                / 365.25
            )
        )

        future["day_of_year_cos"] = (
            np.cos(
                2
                * np.pi
                * future["day_of_year"]
                / 365.25
            )
        )

        # -------------------------------------------------
        # LAGS
        # -------------------------------------------------

        for lag in self.feature_engineer.lags:

            if len(target_history) >= lag:
                value = (
                    target_history.iloc[-lag]
                )
            else:
                value = (
                    target_history.iloc[-1]
                )

            future[
                f"lag_{lag}"
            ] = float(value)

        # -------------------------------------------------
        # ROLLING FEATURES
        # -------------------------------------------------

        for window in (
            self.feature_engineer.rolling_windows
        ):

            values = (
                target_history.tail(window)
            )

            future[
                f"rolling_mean_{window}"
            ] = float(
                values.mean()
            )

            if len(values) >= 2:
                std = float(
                    values.std()
                )
            else:
                std = 0.0

            future[
                f"rolling_std_{window}"
            ] = std

        # -------------------------------------------------
        # TREND
        # -------------------------------------------------

        future[
            "time_index_squared"
        ] = (
            future["time_index"] ** 2
        )

        return future

    # =====================================================
    # SAFE METRICS
    # =====================================================

    @staticmethod
    def _calculate_metrics(
        actual: np.ndarray,
        predicted: np.ndarray,
    ) -> dict:
        """
        Calculate validation metrics safely.

        Metrics are calculated only on the chronological
        validation period — never on the training data.
        """

        actual = np.asarray(
            actual,
            dtype=float,
        )

        predicted = np.asarray(
            predicted,
            dtype=float,
        )

        if len(actual) == 0:
            raise ValueError(
                "No validation observations available."
            )

        errors = (
            actual - predicted
        )

        mae = float(
            np.mean(
                np.abs(errors)
            )
        )

        mse = float(
            np.mean(
                errors ** 2
            )
        )

        rmse = float(
            np.sqrt(mse)
        )

        # -------------------------------------------------
        # MAPE
        # -------------------------------------------------
        #
        # Ignore zero actual values because division by
        # zero makes traditional MAPE undefined.
        # -------------------------------------------------

        non_zero = (
            np.abs(actual) > 1e-12
        )

        if np.any(non_zero):

            percentage_errors = (
                np.abs(
                    errors[non_zero]
                    / actual[non_zero]
                )
            )

            mape = float(
                np.mean(
                    percentage_errors
                )
                * 100
            )

        else:
            mape = None

        # -------------------------------------------------
        # R-SQUARED
        # -------------------------------------------------

        if len(actual) >= 2:

            denominator = np.sum(
                (
                    actual
                    - np.mean(actual)
                ) ** 2
            )

            if denominator > 1e-12:

                r_squared = float(
                    1.0
                    - (
                        np.sum(
                            errors ** 2
                        )
                        / denominator
                    )
                )

            else:
                r_squared = 0.0

        else:
            r_squared = 0.0

        # R² can legitimately be negative during
        # validation. For the dashboard score we clamp it
        # to the useful 0–1 range.
        r_squared_score = max(
            0.0,
            min(
                1.0,
                r_squared,
            ),
        )

        # -------------------------------------------------
        # ACCURACY
        # -------------------------------------------------

        if mape is not None:

            accuracy_score = max(
                0.0,
                min(
                    100.0,
                    100.0 - mape,
                ),
            )

        else:
            accuracy_score = None

        return {
            "mae": mae,
            "mse": mse,
            "rmse": rmse,
            "mape": mape,
            "r_squared": r_squared_score,
            "accuracy_score": accuracy_score,
        }

    # =====================================================
    # FORECAST
    # =====================================================

    def forecast(
        self,
        file_path: str,
        target_column: str,
        date_column: str,
        forecast_periods: int = 30,
        frequency: str = "daily",
        model: str = "auto",
    ) -> ForecastResult:
        """
        Generate a forecast from a dataset.
        """

        # =================================================
        # BASIC INPUT VALIDATION
        # =================================================

        if forecast_periods < 1:
            raise ValueError(
                "forecast_periods must be at least 1."
            )

        frequency = frequency.lower()

        if frequency not in {
            "daily",
            "weekly",
            "monthly",
        }:
            raise ValueError(
                "Unsupported frequency. "
                "Use daily, weekly, or monthly."
            )

        # =================================================
        # LOAD DATA
        # =================================================

        dataframe = self.loader.load(
            file_path
        )

        if dataframe is None:
            raise ValueError(
                "Dataset loader returned no data."
            )

        if dataframe.empty:
            raise ValueError(
                "The uploaded dataset is empty."
            )

        # =================================================
        # RESOLVE COLUMN NAMES
        # =================================================

        resolved_date_column = (
            self._resolve_column_name(
                dataframe=dataframe,
                requested_column=date_column,
                column_type="date",
            )
        )

        resolved_target_column = (
            self._resolve_column_name(
                dataframe=dataframe,
                requested_column=target_column,
                column_type="target",
            )
        )

        date_column = (
            resolved_date_column
        )

        target_column = (
            resolved_target_column
        )

        # =================================================
        # CLEAN ORIGINAL DATA
        # =================================================

        dataframe = dataframe.copy()

        dataframe[date_column] = (
            pd.to_datetime(
                dataframe[date_column],
                errors="coerce",
            )
        )

        dataframe[target_column] = (
            pd.to_numeric(
                dataframe[target_column],
                errors="coerce",
            )
        )

        dataframe = (
            dataframe
            .dropna(
                subset=[
                    date_column,
                    target_column,
                ]
            )
            .sort_values(
                date_column
            )
            .reset_index(drop=True)
        )

        if dataframe.empty:
            raise ValueError(
                "No valid rows remain after cleaning "
                "the date and target columns."
            )

        # =================================================
        # MINIMUM RAW OBSERVATIONS
        # =================================================

        minimum_required = (
            self._minimum_required_observations()
        )

        if len(dataframe) < minimum_required:

            raise ValueError(
                f"At least {minimum_required} "
                "valid historical observations "
                "are required for forecasting "
                "with the current feature "
                "configuration. "
                f"Only {len(dataframe)} valid "
                "observations were found."
            )

        # =================================================
        # FEATURE ENGINEERING
        # =================================================

        feature_dataframe = (
            self.feature_engineer
            .create_features(
                dataframe=dataframe,
                date_column=date_column,
                target_column=target_column,
            )
        )

        if feature_dataframe.empty:
            raise ValueError(
                "Feature engineering produced no usable data."
            )

        if len(feature_dataframe) < (
            self.MODEL_SELECTION_MIN_OBSERVATIONS
        ):
            raise ValueError(
                "Not enough usable observations remain "
                "after feature engineering."
            )

        # =================================================
        # FEATURE COLUMNS
        # =================================================

        feature_columns = (
            self.feature_engineer
            .get_feature_columns(
                feature_dataframe,
                date_column,
                target_column,
            )
        )

        if not feature_columns:
            raise ValueError(
                "No numeric forecasting features available."
            )

        X = (
            feature_dataframe[
                feature_columns
            ]
            .copy()
        )

        y = (
            feature_dataframe[
                target_column
            ]
            .astype(float)
        )

        # =================================================
        # FEATURE CLEANUP
        # =================================================

        X = X.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        valid_mask = (
            X.notna().all(axis=1)
            & y.notna()
        )

        X = (
            X.loc[valid_mask]
            .reset_index(drop=True)
        )

        y = (
            y.loc[valid_mask]
            .reset_index(drop=True)
        )

        if len(X) < (
            self.MODEL_SELECTION_MIN_OBSERVATIONS
        ):
            raise ValueError(
                "Not enough valid observations remain "
                "after feature cleanup."
            )

        # =================================================
        # MODEL SELECTION
        # =================================================

        if model == "auto":

            selected_evaluation = (
                self.model_selector
                .select_best(
                    dataframe=feature_dataframe,
                    target_column=target_column,
                )
            )

            selected_model = (
                selected_evaluation.model_name
            )

        else:

            selected_model = model

            if selected_model not in (
                self.model_selector.models
            ):
                raise ValueError(
                    "Unsupported forecasting model: "
                    f"{selected_model}"
                )

        # =================================================
        # CHRONOLOGICAL VALIDATION
        # =================================================

        validation_size = max(
            self.MIN_VALIDATION_OBSERVATIONS,
            int(
                len(X) * 0.20
            ),
        )

        # Never allow validation to consume the entire
        # dataset.
        max_validation_size = (
            len(X) - 2
        )

        validation_size = min(
            validation_size,
            max_validation_size,
        )

        if validation_size < 1:
            raise ValueError(
                "Not enough observations for "
                "chronological validation."
            )

        train_end = (
            len(X)
            - validation_size
        )

        if train_end < 2:
            raise ValueError(
                "Not enough observations for "
                "chronological training."
            )

        X_train = X.iloc[
            :train_end
        ]

        y_train = y.iloc[
            :train_end
        ]

        X_validation = X.iloc[
            train_end:
        ]

        y_validation = y.iloc[
            train_end:
        ]

        # =================================================
        # VALIDATION MODEL
        # =================================================

        validation_model = (
            self._create_model(
                selected_model
            )
        )

        validation_model.fit(
            X_train,
            y_train,
        )

        validation_predictions = (
            validation_model.predict(
                X_validation
            )
        )

        # =================================================
        # VALIDATION METRICS
        # =================================================

        metrics = self._calculate_metrics(
            actual=np.asarray(
                y_validation,
                dtype=float,
            ),
            predicted=np.asarray(
                validation_predictions,
                dtype=float,
            ),
        )

        mae = metrics["mae"]
        mse = metrics["mse"]
        rmse = metrics["rmse"]
        mape = metrics["mape"]
        r_squared = metrics["r_squared"]
        accuracy_score = metrics["accuracy_score"]

        # =================================================
        # ERROR STATISTICS
        # =================================================

        actual_array = np.asarray(
            y_validation,
            dtype=float,
        )

        predicted_array = np.asarray(
            validation_predictions,
            dtype=float,
        )

        error_statistics = (
            self.confidence_calculator
            .calculate_error_statistics(
                actual=actual_array,
                predicted=predicted_array,
            )
        )

        error_std = float(
            error_statistics.get(
                "error_std",
                0.0,
            )
        )

        # =================================================
        # CONFIDENCE SCORE
        # =================================================

        confidence_score = (
            self.confidence_calculator
            .calculate_confidence_score(
                mape=mape,
                r_squared=r_squared,
                sample_size=len(X_train),
            )
        )

        # =================================================
        # FINAL TRAINING DATA
        # =================================================

        X_final, y_final = (
            self._limit_training_data(
                X,
                y,
            )
        )

        # =================================================
        # TRAIN FINAL MODEL
        # =================================================

        final_model = (
            self._create_model(
                selected_model
            )
        )

        final_model.fit(
            X_final,
            y_final,
        )

        # =================================================
        # HISTORY FOR RECURSIVE FORECAST
        # =================================================

        history = dataframe[
            [
                date_column,
                target_column,
            ]
        ].copy()

        predictions: list[dict] = []

        date_offset = (
            self._get_date_offset(
                frequency
            )
        )

        last_date = (
            history[
                date_column
            ].iloc[-1]
        )

        # =================================================
        # FUTURE FORECAST
        # =================================================

        for step in range(
            1,
            forecast_periods + 1,
        ):

            # -------------------------------------------------
            # FUTURE DATE
            # -------------------------------------------------

            if frequency == "monthly":

                future_date = (
                    last_date
                    + pd.DateOffset(
                        months=step
                    )
                )

            else:

                future_date = (
                    last_date
                    + date_offset * step
                )

            # -------------------------------------------------
            # BUILD FUTURE FEATURES
            # -------------------------------------------------

            future_features = (
                self._build_future_features(
                    history=history,
                    date_column=date_column,
                    target_column=target_column,
                    future_date=future_date,
                )
            )

            # -------------------------------------------------
            # ALIGN FEATURES
            # -------------------------------------------------

            missing_features = [
                column
                for column in feature_columns
                if column
                not in future_features.columns
            ]

            if missing_features:

                for column in missing_features:

                    if column in X_final.columns:

                        future_features[
                            column
                        ] = X_final.iloc[
                            -1
                        ][column]

                    else:

                        future_features[
                            column
                        ] = 0.0

            X_future = (
                future_features[
                    feature_columns
                ]
                .copy()
            )

            # -------------------------------------------------
            # CLEAN FUTURE FEATURES
            # -------------------------------------------------

            X_future = X_future.replace(
                [np.inf, -np.inf],
                np.nan,
            )

            # Use the final training data statistics,
            # not the entire raw dataset.
            fill_values = (
                X_final.median(
                    numeric_only=True
                )
            )

            X_future = (
                X_future.fillna(
                    fill_values
                )
            )

            X_future = (
                X_future.fillna(0.0)
            )

            # -------------------------------------------------
            # PREDICTION
            # -------------------------------------------------

            prediction = float(
                final_model.predict(
                    X_future
                )[0]
            )

            # Forecast quantities cannot be negative.
            prediction = max(
                0.0,
                prediction,
            )

            predictions.append(
                {
                    "date": (
                        future_date.strftime(
                            "%Y-%m-%d"
                        )
                    ),
                    "value": prediction,
                }
            )

            # -------------------------------------------------
            # RECURSIVE HISTORY UPDATE
            # -------------------------------------------------

            history.loc[
                len(history)
            ] = {
                date_column: future_date,
                target_column: prediction,
            }

        # =================================================
        # CONFIDENCE INTERVALS
        # =================================================

        confidence_intervals = (
            self.confidence_calculator
            .build_intervals(
                predictions=predictions,
                error_std=error_std,
            )
        )

        # =================================================
        # FEATURE IMPORTANCE
        # =================================================

        feature_importance = None

        if hasattr(
            final_model,
            "feature_importances_",
        ):

            feature_importance = {
                column: float(
                    importance
                )
                for column, importance
                in zip(
                    feature_columns,
                    final_model.feature_importances_,
                )
            }

        elif hasattr(
            final_model,
            "coef_",
        ):

            coefficients = np.asarray(
                final_model.coef_
            )

            # Handle multi-output models safely.
            if coefficients.ndim > 1:
                coefficients = (
                    coefficients[0]
                )

            feature_importance = {
                column: float(
                    abs(coefficient)
                )
                for column, coefficient
                in zip(
                    feature_columns,
                    coefficients,
                )
            }

        # =================================================
        # EXPLANATION
        # =================================================

        if accuracy_score is not None:

            accuracy_text = (
                f"{accuracy_score:.2f}%"
            )

        else:

            accuracy_text = (
                "not available"
            )

        if confidence_score is not None:

            confidence_text = (
                f"{float(confidence_score):.2f}"
            )

        else:

            confidence_text = (
                "not available"
            )

        ai_explanation = (
            "Forecast generated using the "
            f"MUGONEXT {selected_model} "
            "forecasting engine. "
            f"Chronological validation accuracy: "
            f"{accuracy_text}. "
            f"Confidence score: "
            f"{confidence_text}."
        )

        # =================================================
        # RESULT
        # =================================================

        return ForecastResult(
            predictions=predictions,
            model=selected_model,
            forecast_periods=forecast_periods,
            target_column=target_column,
            date_column=date_column,

            mae=mae,
            mse=mse,
            rmse=rmse,
            mape=mape,
            r_squared=r_squared,

            accuracy_score=accuracy_score,
            confidence_score=confidence_score,

            confidence_intervals=(
                confidence_intervals
            ),

            feature_importance=(
                feature_importance
            ),

            ai_explanation=(
                ai_explanation
            ),
        )
