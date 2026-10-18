"""
=========================================================
MUGONEXT
Recommendation Analyzer
=========================================================

Analyzes forecast outputs and converts them into
structured business signals.

Author:
MUGONEXT
"""

from __future__ import annotations

from statistics import mean, pstdev
from typing import Any


class RecommendationAnalyzer:
    """
    Analyzes a forecast and extracts business-oriented signals.
    """

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def analyze(
        self,
        *,
        predictions: list[dict[str, Any]],
        mape: float | None = None,
        accuracy_score: float | None = None,
        confidence_score: float | None = None,
        r_squared: float | None = None,
    ) -> dict[str, Any]:
        if not predictions:
            raise ValueError(
                "At least one forecast prediction is required."
            )

        values: list[float] = []

        for item in predictions:
            value = self._safe_float(
                item.get("value")
            )

            if value is not None:
                values.append(value)

        if not values:
            raise ValueError(
                "Forecast predictions contain no numeric values."
            )

        first_value = values[0]
        last_value = values[-1]

        absolute_change = last_value - first_value

        if first_value != 0:
            percentage_change = (
                absolute_change / abs(first_value)
            ) * 100
        else:
            percentage_change = 0.0

        average_value = mean(values)

        if average_value != 0:
            coefficient_of_variation = (
                pstdev(values) / abs(average_value)
            ) * 100
        else:
            coefficient_of_variation = 0.0

        if len(values) >= 2:
            sequential_changes = [
                values[index] - values[index - 1]
                for index in range(1, len(values))
            ]

            average_step_change = mean(
                sequential_changes
            )

            direction_changes = sum(
                1
                for index in range(1, len(sequential_changes))
                if (
                    sequential_changes[index]
                    * sequential_changes[index - 1]
                ) < 0
            )
        else:
            average_step_change = 0.0
            direction_changes = 0

        if percentage_change > 10:
            trend = "strong_growth"
        elif percentage_change > 3:
            trend = "growth"
        elif percentage_change < -10:
            trend = "strong_decline"
        elif percentage_change < -3:
            trend = "decline"
        else:
            trend = "stable"

        if coefficient_of_variation >= 15:
            volatility = "high"
        elif coefficient_of_variation >= 7:
            volatility = "moderate"
        else:
            volatility = "low"

        if accuracy_score is not None:
            if accuracy_score >= 90:
                forecast_quality = "high"
            elif accuracy_score >= 75:
                forecast_quality = "moderate"
            else:
                forecast_quality = "low"
        elif mape is not None:
            if mape <= 10:
                forecast_quality = "high"
            elif mape <= 25:
                forecast_quality = "moderate"
            else:
                forecast_quality = "low"
        else:
            forecast_quality = "unknown"

        if confidence_score is not None:
            if confidence_score >= 75:
                confidence_level = "high"
            elif confidence_score >= 50:
                confidence_level = "moderate"
            else:
                confidence_level = "low"
        else:
            confidence_level = "unknown"

        if trend in {"strong_decline", "decline"}:
            business_signal = "downside_risk"
        elif trend in {"strong_growth", "growth"}:
            business_signal = "growth_opportunity"
        elif volatility == "high":
            business_signal = "volatility_risk"
        else:
            business_signal = "stable_outlook"

        return {
            "trend": trend,
            "business_signal": business_signal,
            "volatility": volatility,
            "average_forecast": round(
                average_value,
                2,
            ),
            "first_forecast": round(
                first_value,
                2,
            ),
            "last_forecast": round(
                last_value,
                2,
            ),
            "absolute_change": round(
                absolute_change,
                2,
            ),
            "percentage_change": round(
                percentage_change,
                2,
            ),
            "coefficient_of_variation": round(
                coefficient_of_variation,
                2,
            ),
            "average_step_change": round(
                average_step_change,
                2,
            ),
            "direction_changes": direction_changes,
            "forecast_quality": forecast_quality,
            "confidence_level": confidence_level,
            "mape": mape,
            "accuracy_score": accuracy_score,
            "r_squared": r_squared,
            "confidence_score": confidence_score,
            "forecast_periods": len(values),
        }