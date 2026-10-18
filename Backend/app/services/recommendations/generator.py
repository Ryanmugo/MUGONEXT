"""
=========================================================
MUGONEXT
Recommendation Generator
=========================================================

Converts analyzed forecast signals into structured
business recommendations.

Author:
MUGONEXT
"""

from __future__ import annotations

from typing import Any

from app.constants import RecommendationPriority


class RecommendationGenerator:
    """
    Generates actionable business recommendations from
    forecast analysis.
    """

    def generate(
        self,
        *,
        analysis: dict[str, Any],
        forecast_id: int | None = None,
        upload_id: int | None = None,
    ) -> dict[str, Any]:

        trend = analysis["trend"]
        business_signal = analysis["business_signal"]
        volatility = analysis["volatility"]

        percentage_change = analysis["percentage_change"]
        average_forecast = analysis["average_forecast"]

        forecast_quality = analysis["forecast_quality"]
        confidence_level = analysis["confidence_level"]

        confidence_score = analysis.get(
            "confidence_score"
        )
        accuracy_score = analysis.get(
            "accuracy_score"
        )

        # =====================================================
        # GROWTH
        # =====================================================

        if trend == "strong_growth":
            title = "Prepare for strong forecasted growth"
            category = "sales_growth"

            recommendation = (
                "Prepare inventory, staffing, and operational "
                "capacity for the forecasted increase in demand."
            )

            reasoning = (
                f"The forecast indicates a {percentage_change:.2f}% "
                "increase between the first and final forecast "
                "period."
            )

            suggested_action = (
                "Review inventory availability, staffing capacity, "
                "supplier lead times, and sales capacity before the "
                "forecasted increase materializes."
            )

            expected_outcome = (
                "Improved readiness for increased demand and reduced "
                "risk of stockouts or operational bottlenecks."
            )

            priority = (
                RecommendationPriority.HIGH
            )

            impact_score = min(
                100.0,
                60.0 + abs(percentage_change),
            )

        elif trend == "growth":
            title = "Prepare for forecasted growth"
            category = "sales_growth"

            recommendation = (
                "Increase operational readiness gradually to support "
                "the forecasted growth in demand."
            )

            reasoning = (
                f"The forecast shows an expected increase of "
                f"{percentage_change:.2f}% across the forecast period."
            )

            suggested_action = (
                "Monitor demand closely and adjust inventory, staffing, "
                "and promotional activity in line with the forecast."
            )

            expected_outcome = (
                "Better capacity planning while avoiding unnecessary "
                "overcommitment of resources."
            )

            priority = (
                RecommendationPriority.MEDIUM
            )

            impact_score = min(
                100.0,
                50.0 + abs(percentage_change),
            )

        # =====================================================
        # DECLINE
        # =====================================================

        elif trend == "strong_decline":
            title = "Address strong forecasted decline"
            category = "risk"

            recommendation = (
                "Review demand, pricing, inventory, and customer "
                "engagement strategies because the forecast indicates "
                "a significant decline."
            )

            reasoning = (
                f"The forecast indicates a {abs(percentage_change):.2f}% "
                "decline between the first and final forecast period."
            )

            suggested_action = (
                "Investigate declining demand drivers and review "
                "pricing, marketing, inventory commitments, and "
                "sales activity."
            )

            expected_outcome = (
                "Earlier intervention and reduced exposure to declining "
                "revenue or excess inventory."
            )

            priority = (
                RecommendationPriority.CRITICAL
            )

            impact_score = min(
                100.0,
                70.0 + abs(percentage_change),
            )

        elif trend == "decline":
            title = "Monitor forecasted demand decline"
            category = "risk"

            recommendation = (
                "Monitor the expected decline closely and prepare "
                "corrective actions before the trend becomes severe."
            )

            reasoning = (
                f"The forecast shows an expected decline of "
                f"{abs(percentage_change):.2f}% across the forecast period."
            )

            suggested_action = (
                "Review sales performance, customer demand, pricing, "
                "and inventory levels over the next planning period."
            )

            expected_outcome = (
                "Reduced risk of overstocking and earlier detection "
                "of weakening demand."
            )

            priority = (
                RecommendationPriority.HIGH
            )

            impact_score = min(
                100.0,
                55.0 + abs(percentage_change),
            )

        # =====================================================
        # VOLATILITY
        # =====================================================

        elif volatility == "high":
            title = "Monitor high forecast volatility"
            category = "risk"

            recommendation = (
                "Use shorter planning cycles and closely monitor "
                "forecast changes because the projected values are "
                "highly variable."
            )

            reasoning = (
                "The forecast shows elevated variability across the "
                "projection period."
            )

            suggested_action = (
                "Increase monitoring frequency and avoid committing "
                "large resources based on a single forecast snapshot."
            )

            expected_outcome = (
                "Reduced exposure to sudden demand changes and "
                "better operational flexibility."
            )

            priority = (
                RecommendationPriority.HIGH
            )

            impact_score = 70.0

        # =====================================================
        # STABLE
        # =====================================================

        else:
            title = "Maintain stable operational planning"
            category = "operations"

            recommendation = (
                "Maintain current operating plans while continuing "
                "to monitor forecast performance."
            )

            reasoning = (
                "The forecast indicates a relatively stable outlook "
                "with no major directional change."
            )

            suggested_action = (
                "Maintain current inventory and operational plans, "
                "with regular forecast reviews."
            )

            expected_outcome = (
                "Stable resource allocation with controlled operational "
                "risk."
            )

            priority = (
                RecommendationPriority.MEDIUM
            )

            impact_score = 40.0

        # =====================================================
        # PRIORITY SCORE
        # =====================================================

        priority_score = impact_score

        if confidence_level == "low":
            priority_score *= 0.90
        elif confidence_level == "high":
            priority_score *= 1.05

        priority_score = max(
            0.0,
            min(
                100.0,
                priority_score,
            ),
        )

        # =====================================================
        # CONFIDENCE
        # =====================================================

        if confidence_score is None:
            recommendation_confidence = 50.0
        else:
            recommendation_confidence = max(
                0.0,
                min(
                    100.0,
                    float(confidence_score),
                ),
            )

        # =====================================================
        # EXPLANATION
        # =====================================================

        explanation_parts = [
            (
                f"MUGONEXT detected a {trend.replace('_', ' ')} "
                f"forecast."
            ),
            (
                f"The projected change is {percentage_change:.2f}% "
                "across the forecast horizon."
            ),
            (
                f"Forecast quality is {forecast_quality} and "
                f"confidence is {confidence_level}."
            ),
        ]

        if accuracy_score is not None:
            explanation_parts.append(
                f"Reported forecast accuracy is "
                f"{accuracy_score:.2f}%."
            )

        if confidence_score is not None:
            explanation_parts.append(
                f"Confidence score is "
                f"{confidence_score:.2f}/100."
            )

        ai_explanation = " ".join(
            explanation_parts
        )

        return {
            "upload_id": upload_id,
            "forecast_id": forecast_id,
            "title": title,
            "category": category,
            "description": (
                "Automatically generated by the "
                "MUGONEXT recommendation engine."
            ),
            "recommendation": recommendation,
            "reasoning": reasoning,
            "expected_outcome": expected_outcome,
            "suggested_action": suggested_action,
            "priority": priority,
            "priority_score": round(
                priority_score,
                2,
            ),
            "impact_score": round(
                impact_score,
                2,
            ),
            "confidence_score": round(
                recommendation_confidence,
                2,
            ),
            "ai_provider": "local",
            "model_version": "1.0",
            "parameters": {
                "trend": trend,
                "business_signal": business_signal,
                "volatility": volatility,
                "forecast_quality": forecast_quality,
                "confidence_level": confidence_level,
                "average_forecast": average_forecast,
            },
            "source_data": analysis,
            "ai_explanation": ai_explanation,
        }