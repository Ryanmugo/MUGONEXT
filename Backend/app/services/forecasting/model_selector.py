from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


@dataclass
class ModelEvaluation:
    model_name: str
    mae: float
    mse: float
    rmse: float
    mape: float | None
    r_squared: float
    accuracy_score: float | None


class ForecastModelSelector:
    """
    Fast forecasting model selector for MUGONEXT.

    Uses chronological validation and automatically limits the
    amount of data used for expensive model comparison.

    The original uploaded dataset is never modified.
    """

    # Maximum rows used during AUTO model selection.
    MAX_SELECTION_ROWS = 10_000

    def __init__(self):
        self.models = {
            "linear_regression": LinearRegression(),

            "random_forest": RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1,
            ),

            "gradient_boosting": GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=3,
                random_state=42,
            ),
        }

    # =========================================================
    # LARGE DATASET SAMPLING
    # =========================================================

    def _limit_selection_data(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Limit rows used for model selection.

        Keeps the most recent observations because recent
        business behavior is generally more relevant for
        forecasting than very old observations.

        The original dataframe is never modified.
        """

        if len(dataframe) <= self.MAX_SELECTION_ROWS:
            return dataframe.copy()

        print(
            "[ForecastModelSelector] "
            f"Large dataset detected: {len(dataframe):,} rows. "
            f"Using latest {self.MAX_SELECTION_ROWS:,} rows "
            "for model selection."
        )

        return dataframe.tail(
            self.MAX_SELECTION_ROWS
        ).reset_index(drop=True)

    # =========================================================
    # FEATURE PREPARATION
    # =========================================================

    def _prepare_features(
        self,
        dataframe: pd.DataFrame,
        target_column: str,
    ):
        excluded = {
            target_column,
            "date",
        }

        preferred_features = [
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

        for column in dataframe.columns:
            if (
                column.startswith("lag_")
                or column.startswith("rolling_mean_")
                or column.startswith("rolling_std_")
            ):
                preferred_features.append(column)

        feature_columns = [
            column
            for column in preferred_features
            if (
                column in dataframe.columns
                and column not in excluded
                and pd.api.types.is_numeric_dtype(
                    dataframe[column]
                )
            )
        ]

        if not feature_columns:
            raise ValueError(
                "No forecasting-safe numeric features available."
            )

        X = dataframe[feature_columns].copy()

        y = pd.to_numeric(
            dataframe[target_column],
            errors="coerce",
        )

        valid_rows = (
            X.notna().all(axis=1)
            & y.notna()
        )

        X = (
            X.loc[valid_rows]
            .reset_index(drop=True)
        )

        y = (
            y.loc[valid_rows]
            .reset_index(drop=True)
        )

        if len(X) < 10:
            raise ValueError(
                "At least 10 valid observations are required "
                "for model selection."
            )

        return X, y, feature_columns

    # =========================================================
    # EVALUATION
    # =========================================================

    def evaluate(
        self,
        dataframe: pd.DataFrame,
        target_column: str,
    ) -> list[ModelEvaluation]:

        if len(dataframe) < 10:
            raise ValueError(
                "At least 10 observations are required "
                "for model selection."
            )

        # IMPORTANT:
        # Limit expensive model comparison for large datasets.
        dataframe = self._limit_selection_data(
            dataframe
        )

        X, y, feature_columns = self._prepare_features(
            dataframe,
            target_column,
        )

        validation_size = max(
            3,
            int(len(X) * 0.20),
        )

        if len(X) - validation_size < 5:
            raise ValueError(
                "Not enough observations for "
                "model evaluation."
            )

        train_end = len(X) - validation_size

        X_train = X.iloc[:train_end]
        y_train = y.iloc[:train_end]

        X_validation = X.iloc[train_end:]
        y_validation = y.iloc[train_end:]

        results = []

        for model_name, base_model in self.models.items():

            model = clone(base_model)

            try:
                model.fit(
                    X_train,
                    y_train,
                )

                predictions = model.predict(
                    X_validation
                )

                actual = np.asarray(
                    y_validation,
                    dtype=float,
                )

                predicted = np.asarray(
                    predictions,
                    dtype=float,
                )

                if len(actual) != len(predicted):
                    raise ValueError(
                        "Prediction length does not match "
                        "validation data."
                    )

                if not np.all(
                    np.isfinite(predicted)
                ):
                    raise ValueError(
                        "Model produced non-finite predictions."
                    )

                mae = float(
                    mean_absolute_error(
                        actual,
                        predicted,
                    )
                )

                mse = float(
                    mean_squared_error(
                        actual,
                        predicted,
                    )
                )

                rmse = float(
                    np.sqrt(mse)
                )

                non_zero = actual != 0

                if np.any(non_zero):
                    mape = float(
                        np.mean(
                            np.abs(
                                (
                                    actual[non_zero]
                                    - predicted[non_zero]
                                )
                                / actual[non_zero]
                            )
                        )
                        * 100
                    )
                else:
                    mape = None

                if len(actual) >= 2:
                    try:
                        r_squared = float(
                            r2_score(
                                actual,
                                predicted,
                            )
                        )
                    except Exception:
                        r_squared = 0.0

                    if not np.isfinite(
                        r_squared
                    ):
                        r_squared = 0.0

                    r_squared = max(
                        0.0,
                        min(
                            1.0,
                            r_squared,
                        ),
                    )
                else:
                    r_squared = 0.0

                if (
                    mape is not None
                    and np.isfinite(mape)
                ):
                    accuracy_score = max(
                        0.0,
                        min(
                            100.0,
                            100.0 - mape,
                        ),
                    )
                else:
                    accuracy_score = None

                results.append(
                    ModelEvaluation(
                        model_name=model_name,
                        mae=mae,
                        mse=mse,
                        rmse=rmse,
                        mape=mape,
                        r_squared=r_squared,
                        accuracy_score=accuracy_score,
                    )
                )

            except Exception as exc:

                print(
                    "[ForecastModelSelector] "
                    f"Skipping {model_name}: "
                    f"{type(exc).__name__}: {exc}"
                )

                continue

        if not results:
            raise ValueError(
                "None of the available forecasting models "
                "could be trained successfully on this dataset."
            )

        return results

    # =========================================================
    # BEST MODEL
    # =========================================================

    def select_best(
        self,
        dataframe: pd.DataFrame,
        target_column: str,
    ) -> ModelEvaluation:

        evaluations = self.evaluate(
            dataframe=dataframe,
            target_column=target_column,
        )

        return min(
            evaluations,
            key=lambda result: (
                result.rmse,
                -result.r_squared,
                result.mae,
            ),
        )