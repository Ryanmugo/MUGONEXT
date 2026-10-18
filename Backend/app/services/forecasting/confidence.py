
from dataclasses import dataclass

import numpy as np


@dataclass
class ConfidenceInterval:
    """
    Represents the uncertainty range around a forecast.
    """

    prediction: float
    lower_bound: float
    upper_bound: float
    confidence_level: float


class ForecastConfidenceCalculator:
    """
    Calculates forecast confidence intervals using historical
    validation errors.

    MUGONEXT does not assume a fixed +/- percentage.

    Instead:

        Historical errors
              ↓
        Error standard deviation
              ↓
        Confidence margin
              ↓
        Forecast interval

    This allows the interval to adapt to the actual behaviour
    of the dataset.
    """

    Z_SCORES = {
        0.80: 1.282,
        0.90: 1.645,
        0.95: 1.960,
        0.99: 2.576,
    }

    def __init__(
        self,
        confidence_level: float = 0.95,
    ):
        if confidence_level not in self.Z_SCORES:
            raise ValueError(
                "Unsupported confidence level. "
                "Use one of: 0.80, 0.90, 0.95, 0.99."
            )

        self.confidence_level = confidence_level

    # =========================================================
    # ERROR STATISTICS
    # =========================================================

    def calculate_error_statistics(
        self,
        actual: np.ndarray,
        predicted: np.ndarray,
    ) -> dict:
        """
        Calculate historical forecasting errors.
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
                "At least one historical forecast error "
                "is required."
            )

        if len(actual) != len(predicted):
            raise ValueError(
                "Actual and predicted values must have "
                "the same length."
            )

        errors = actual - predicted

        absolute_errors = np.abs(errors)

        mae = float(
            np.mean(absolute_errors)
        )

        error_std = float(
            np.std(
                errors,
                ddof=1,
            )
        ) if len(errors) > 1 else mae

        rmse = float(
            np.sqrt(
                np.mean(
                    errors ** 2
                )
            )
        )

        return {
            "mae": mae,
            "rmse": rmse,
            "error_std": error_std,
            "sample_size": len(errors),
        }

    # =========================================================
    # CALCULATE INTERVAL
    # =========================================================

    def calculate_interval(
        self,
        prediction: float,
        error_std: float,
        horizon: int = 1,
    ) -> ConfidenceInterval:
        """
        Calculate a confidence interval for a forecast.

        The uncertainty expands with the forecast horizon.

        horizon=1:
            smallest uncertainty

        horizon=10:
            wider uncertainty

        horizon=30:
            wider still
        """

        prediction = float(prediction)
        error_std = max(
            0.0,
            float(error_std),
        )

        horizon = max(
            1,
            int(horizon),
        )

        z_score = self.Z_SCORES[
            self.confidence_level
        ]

        # Forecast uncertainty increases as the horizon
        # moves further into the future.
        horizon_factor = np.sqrt(
            horizon
        )

        margin = (
            z_score
            * error_std
            * horizon_factor
        )

        lower_bound = max(
            0.0,
            prediction - margin,
        )

        upper_bound = max(
            lower_bound,
            prediction + margin,
        )

        return ConfidenceInterval(
            prediction=prediction,
            lower_bound=float(
                lower_bound
            ),
            upper_bound=float(
                upper_bound
            ),
            confidence_level=self.confidence_level,
        )

    # =========================================================
    # CALCULATE CONFIDENCE SCORE
    # =========================================================

    def calculate_confidence_score(
        self,
        mape: float | None,
        r_squared: float | None,
        sample_size: int,
    ) -> float:
        """
        Produce a 0-100 confidence score.

        The score combines:

            1. Forecast error
            2. Model explanatory power
            3. Amount of historical data

        This is a PRODUCT confidence score, not a
        statistical probability that the forecast will
        definitely occur.
        """

        # -----------------------------------------------------
        # Accuracy component
        # -----------------------------------------------------

        if mape is None:
            accuracy_component = 50.0
        else:
            accuracy_component = max(
                0.0,
                min(
                    100.0,
                    100.0 - float(mape),
                ),
            )

        # -----------------------------------------------------
        # R² component
        # -----------------------------------------------------

        if r_squared is None:
            r2_component = 50.0
        else:
            r2_component = max(
                0.0,
                min(
                    100.0,
                    float(r_squared) * 100.0,
                ),
            )

        # -----------------------------------------------------
        # Data sufficiency component
        # -----------------------------------------------------

        # Full data-confidence score after 60 observations.
        data_component = min(
            100.0,
            (max(sample_size, 1) / 60.0) * 100.0,
        )

        # -----------------------------------------------------
        # Weighted confidence
        # -----------------------------------------------------

        confidence_score = (
            accuracy_component * 0.50
            + r2_component * 0.30
            + data_component * 0.20
        )

        return round(
            max(
                0.0,
                min(
                    100.0,
                    confidence_score,
                ),
            ),
            2,
        )

    # =========================================================
    # BUILD FORECAST INTERVALS
    # =========================================================

    def build_intervals(
        self,
        predictions: list[dict],
        error_std: float,
    ) -> list[dict]:
        """
        Add confidence intervals to a list of forecasts.

        Expected input:

            [
                {
                    "date": "...",
                    "value": 100000
                }
            ]

        Returns:

            [
                {
                    "date": "...",
                    "value": 100000,
                    "lower_bound": ...,
                    "upper_bound": ...,
                    "confidence_level": 0.95
                }
            ]
        """

        intervals = []

        for index, forecast in enumerate(
            predictions,
            start=1,
        ):
            prediction = float(
                forecast["value"]
            )

            interval = self.calculate_interval(
                prediction=prediction,
                error_std=error_std,
                horizon=index,
            )

            intervals.append(
                {
                    "date": forecast["date"],
                    "value": prediction,
                    "lower_bound": interval.lower_bound,
                    "upper_bound": interval.upper_bound,
                    "confidence_level": interval.confidence_level,
                }
            )

        return intervals

