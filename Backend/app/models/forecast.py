"""
=========================================================
MUGONEXT
Forecast Model
=========================================================

Represents an AI-generated forecast based on an uploaded
dataset.

Used for
--------
✓ Demand Forecasting
✓ Sales Forecasting
✓ Inventory Forecasting
✓ Trend Prediction
✓ Forecast Analytics
✓ Model Evaluation
✓ AI Decision Support
✓ Business Intelligence

Author:
MUGONEXT
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.constants import ForecastModel
from app.models.base import BaseModel
from app.models.mixins.ownership import OwnershipMixin


class Forecast(
    BaseModel,
    OwnershipMixin,
):
    """
    Represents an AI-generated forecast belonging to a company.
    """

    __tablename__ = "forecasts"

    # =====================================================
    # Table Constraints & Indexes
    # =====================================================

    __table_args__ = (
        CheckConstraint(
            "forecast_periods > 0",
            name="ck_forecast_periods_positive",
        ),

        CheckConstraint(
            "progress >= 0 AND progress <= 100",
            name="ck_forecast_progress",
        ),

        CheckConstraint(
            "mae IS NULL OR mae >= 0",
            name="ck_forecast_mae",
        ),

        CheckConstraint(
            "mse IS NULL OR mse >= 0",
            name="ck_forecast_mse",
        ),

        CheckConstraint(
            "rmse IS NULL OR rmse >= 0",
            name="ck_forecast_rmse",
        ),

        CheckConstraint(
            "mape IS NULL OR mape >= 0",
            name="ck_forecast_mape",
        ),

        CheckConstraint(
            "r_squared IS NULL "
            "OR (r_squared >= 0 AND r_squared <= 1)",
            name="ck_forecast_r_squared",
        ),

        CheckConstraint(
            "confidence_score IS NULL "
            "OR (confidence_score >= 0 AND confidence_score <= 100)",
            name="ck_forecast_confidence_score",
        ),

        CheckConstraint(
            "quality_score IS NULL "
            "OR (quality_score >= 0 AND quality_score <= 100)",
            name="ck_forecast_quality_score",
        ),

        CheckConstraint(
            "accuracy_score IS NULL "
            "OR (accuracy_score >= 0 AND accuracy_score <= 100)",
            name="ck_forecast_accuracy_score",
        ),

        Index(
            "ix_forecast_company_upload",
            "company_id",
            "upload_id",
        ),

        Index(
            "ix_forecast_company_status",
            "company_id",
            "status",
        ),

        Index(
            "ix_forecast_company_created",
            "company_id",
            "created_at",
        ),

        Index(
            "ix_forecast_company_model",
            "company_id",
            "forecast_model",
        ),
    )

    # =====================================================
    # Ownership
    # =====================================================

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    upload_id: Mapped[int] = mapped_column(
        ForeignKey(
            "uploads.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # company_id comes from OwnershipMixin

    # =====================================================
    # Forecast Identity
    # =====================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    forecast_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # =====================================================
    # Forecast Configuration
    # =====================================================

    forecast_model: Mapped[ForecastModel] = mapped_column(
        Enum(
            ForecastModel,
            name="forecast_model_enum",
        ),
        nullable=False,
        index=True,
    )

    target_column: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    date_column: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    forecast_periods: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    frequency: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # =====================================================
    # Forecast Results
    # =====================================================

    predictions: Mapped[list | dict] = mapped_column(
        JSON,
        nullable=False,
    )

    confidence_intervals: Mapped[
        dict | list | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    forecast_start_date: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    forecast_end_date: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =====================================================
    # Model Performance
    # =====================================================

    mae: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    mse: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    rmse: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    mape: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    r_squared: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    accuracy_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # =====================================================
    # Forecast Quality
    # =====================================================

    confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    quality_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # =====================================================
    # Processing
    # =====================================================

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        index=True,
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    processing_time_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    # =====================================================
    # AI Metadata
    # =====================================================

    ai_provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    model_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    parameters: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    feature_importance: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    ai_explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Lifecycle
    # =====================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    deleted_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # =====================================================
    # Relationships
    # =====================================================

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="forecasts",
        lazy="selectin",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="forecasts",
        lazy="selectin",
    )

    upload: Mapped["Upload"] = relationship(
        "Upload",
        back_populates="forecasts",
        lazy="selectin",
    )

    # =====================================================
    # Helper Properties
    # =====================================================

    @property
    def is_completed(self) -> bool:
        """Returns True if forecast generation completed."""

        return self.status == "completed"

    @property
    def is_processing(self) -> bool:
        """Returns True if forecast generation is running."""

        return self.status == "processing"

    @property
    def is_failed(self) -> bool:
        """Returns True if forecast generation failed."""

        return self.status == "failed"

    @property
    def is_pending(self) -> bool:
        """Returns True if forecast generation is pending."""

        return self.status == "pending"

    @property
    def is_deleted(self) -> bool:
        """Returns True if the forecast was soft-deleted."""

        return self.deleted_at is not None

    @property
    def is_archived_status(self) -> bool:
        """Returns True if the forecast is archived."""

        return self.is_archived

    @property
    def has_predictions(self) -> bool:
        """Returns True if predictions exist."""

        return bool(self.predictions)

    @property
    def has_accuracy_metrics(self) -> bool:
        """Returns True if accuracy metrics exist."""

        return any(
            metric is not None
            for metric in (
                self.mae,
                self.mse,
                self.rmse,
                self.mape,
                self.r_squared,
                self.accuracy_score,
            )
        )

    @property
    def has_confidence_score(self) -> bool:
        """Returns True if a confidence score exists."""

        return self.confidence_score is not None

    @property
    def has_quality_score(self) -> bool:
        """Returns True if a quality score exists."""

        return self.quality_score is not None

    @property
    def has_explanation(self) -> bool:
        """Returns True if an AI explanation exists."""

        return bool(
            self.ai_explanation
            and self.ai_explanation.strip()
        )

    @property
    def has_error(self) -> bool:
        """Returns True if an error was recorded."""

        return bool(
            self.error_message
            and self.error_message.strip()
        )

    @property
    def completion_percentage(self) -> int:
        """Returns forecast generation progress."""

        return self.progress

    @property
    def processing_duration(self) -> int | None:
        """Returns forecast processing duration."""

        return self.processing_time_seconds

    @property
    def is_versioned(self) -> bool:
        """Returns True if this forecast has multiple versions."""

        return self.forecast_version > 1

    @property
    def can_be_used(self) -> bool:
        """
        Returns True if the forecast is available for
        downstream MUGONEXT decision-support features.
        """

        return (
            self.is_completed
            and self.is_active
            and not self.is_archived
            and not self.is_deleted
            and self.has_predictions
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<Forecast("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"upload_id={self.upload_id}, "
            f"company_id={self.company_id}, "
            f"model='{self.forecast_model.value}', "
            f"version={self.forecast_version}, "
            f"status='{self.status}'"
            f")>"
        )