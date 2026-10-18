from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# ENUMS
# =========================================================

class ForecastModel(str, Enum):
    AUTO = "auto"
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"


# =========================================================
# CREATE FORECAST
# =========================================================

class ForecastCreate(BaseModel):
    """
    Request used to generate a forecast.

    Predictions and statistical metrics are NOT supplied
    by the client.

    MUGONEXT generates them from the uploaded dataset.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    upload_id: int

    description: str | None = None

    forecast_model: ForecastModel = ForecastModel.AUTO

    target_column: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    date_column: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    forecast_periods: int = Field(
        ...,
        ge=1,
        le=3650,
    )

    frequency: str = Field(
        default="daily",
        pattern="^(daily|weekly|monthly)$",
    )


# =========================================================
# UPDATE FORECAST
# =========================================================

class ForecastUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    is_active: bool | None = None


# =========================================================
# FORECAST RESPONSE
# =========================================================

class ForecastResponse(BaseModel):
    """
    Complete forecast returned by MUGONEXT.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    company_id: int

    user_id: int

    upload_id: int

    name: str

    description: str | None

    forecast_version: int

    forecast_model: str

    target_column: str

    date_column: str

    forecast_periods: int

    frequency: str

    predictions: list[dict[str, Any]]

    confidence_intervals: list[dict[str, Any]] | None

    forecast_start_date: datetime | None

    forecast_end_date: datetime | None

    mae: float | None

    mse: float | None

    rmse: float | None

    mape: float | None

    r_squared: float | None

    accuracy_score: float | None

    confidence_score: float | None

    quality_score: float | None

    status: str

    progress: int

    started_at: datetime | None

    completed_at: datetime | None

    processing_time_seconds: int | None

    error_message: str | None

    ai_provider: str | None

    model_version: str | None

    parameters: dict[str, Any] | None

    feature_importance: dict[str, float] | None

    ai_explanation: str | None

    is_active: bool

    is_archived: bool

    deleted_at: datetime | None

    created_at: datetime

    updated_at: datetime