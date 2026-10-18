"""
=========================================================
MUGONEXT
Recommendation Schemas
=========================================================

Pydantic schemas for the Recommendation API.

Author:
MUGONEXT
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.constants import (
    RecommendationPriority,
    RecommendationStatus,
)


# =========================================================
# CREATE
# =========================================================


class RecommendationCreate(BaseModel):
    """
    Create a new AI-generated recommendation.
    """

    upload_id: int | None = Field(
        default=None,
        gt=0,
    )

    forecast_id: int | None = Field(
        default=None,
        gt=0,
    )

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    category: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    recommendation: str = Field(
        min_length=1,
    )

    reasoning: str | None = None

    expected_outcome: str | None = None

    suggested_action: str | None = None

    priority: RecommendationPriority = (
        RecommendationPriority.MEDIUM
    )

    priority_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    impact_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    confidence_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    estimated_cost: float | None = Field(
        default=None,
        ge=0,
    )

    estimated_savings: float | None = Field(
        default=None,
        ge=0,
    )

    estimated_revenue_impact: float | None = None

    roi_percentage: float | None = None

    ai_provider: str | None = Field(
        default=None,
        max_length=100,
    )

    model_version: str | None = Field(
        default=None,
        max_length=100,
    )

    parameters: dict[str, Any] | None = None

    source_data: dict[str, Any] | list[Any] | None = None

    ai_explanation: str | None = None


# =========================================================
# GENERATE FROM FORECAST
# =========================================================


class RecommendationGenerateRequest(BaseModel):
    """
    Request used to generate a recommendation directly
    from an existing forecast.
    """

    forecast_id: int = Field(
        ...,
        gt=0,
    )


# =========================================================
# UPDATE
# =========================================================


class RecommendationUpdate(BaseModel):
    """
    Update an existing recommendation.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    recommendation: str | None = None

    reasoning: str | None = None

    expected_outcome: str | None = None

    suggested_action: str | None = None

    priority: RecommendationPriority | None = None

    priority_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    impact_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    confidence_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    estimated_cost: float | None = Field(
        default=None,
        ge=0,
    )

    estimated_savings: float | None = Field(
        default=None,
        ge=0,
    )

    estimated_revenue_impact: float | None = None

    roi_percentage: float | None = None

    ai_explanation: str | None = None


# =========================================================
# ACTION
# =========================================================


class RecommendationAction(BaseModel):
    """
    Record that a recommendation was acted upon.
    """

    action_taken: bool = True

    action_notes: str | None = Field(
        default=None,
        max_length=5000,
    )


# =========================================================
# RESPONSE
# =========================================================


class RecommendationResponse(BaseModel):
    """
    Complete recommendation response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    company_id: int

    user_id: int

    upload_id: int | None

    forecast_id: int | None

    title: str

    category: str

    description: str | None

    recommendation: str

    reasoning: str | None

    expected_outcome: str | None

    suggested_action: str | None

    priority: RecommendationPriority

    priority_score: float | None

    impact_score: float | None

    confidence_score: float | None

    estimated_cost: float | None

    estimated_savings: float | None

    estimated_revenue_impact: float | None

    roi_percentage: float | None

    ai_provider: str | None

    model_version: str | None

    parameters: dict[str, Any] | None

    source_data: dict[str, Any] | list[Any] | None

    ai_explanation: str | None

    status: RecommendationStatus

    progress: int

    started_at: datetime | None

    completed_at: datetime | None

    processing_time_seconds: int | None

    error_message: str | None

    action_taken: bool

    action_taken_at: datetime | None

    action_notes: str | None

    is_active: bool

    is_archived: bool

    deleted_at: datetime | None

    created_at: datetime

    updated_at: datetime


# =========================================================
# LIST RESPONSE
# =========================================================


class RecommendationListResponse(BaseModel):
    """
    Paginated recommendation response.
    """

    items: list[RecommendationResponse]

    total: int

    page: int

    page_size: int

    pages: int