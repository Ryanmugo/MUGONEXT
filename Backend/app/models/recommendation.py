"""
=========================================================
MUGONEXT
Recommendation Model
=========================================================

Represents an AI-generated business recommendation.

Used for
--------
✓ Business Recommendations
✓ Decision Support
✓ Inventory Optimization
✓ Sales Optimization
✓ Demand Planning
✓ Cost Optimization
✓ Risk Detection
✓ Operational Improvement
✓ AI Insights

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

from app.constants import (
    RecommendationPriority,
    RecommendationStatus,
)

from app.models.base import BaseModel
from app.models.mixins.ownership import OwnershipMixin


class Recommendation(
    BaseModel,
    OwnershipMixin,
):
    """
    Represents an AI-generated recommendation belonging
    to a company.
    """

    __tablename__ = "recommendations"

    # =====================================================
    # Table Constraints & Indexes
    # =====================================================

    __table_args__ = (
        CheckConstraint(
            "priority_score IS NULL "
            "OR (priority_score >= 0 AND priority_score <= 100)",
            name="ck_recommendation_priority_score",
        ),

        CheckConstraint(
            "confidence_score IS NULL "
            "OR (confidence_score >= 0 AND confidence_score <= 100)",
            name="ck_recommendation_confidence_score",
        ),

        CheckConstraint(
            "impact_score IS NULL "
            "OR (impact_score >= 0 AND impact_score <= 100)",
            name="ck_recommendation_impact_score",
        ),

        CheckConstraint(
            "progress >= 0 AND progress <= 100",
            name="ck_recommendation_progress",
        ),

        CheckConstraint(
            "estimated_cost IS NULL OR estimated_cost >= 0",
            name="ck_recommendation_estimated_cost",
        ),

        CheckConstraint(
            "estimated_savings IS NULL OR estimated_savings >= 0",
            name="ck_recommendation_estimated_savings",
        ),

        Index(
            "ix_recommendation_company_upload",
            "company_id",
            "upload_id",
        ),

        Index(
            "ix_recommendation_company_forecast",
            "company_id",
            "forecast_id",
        ),

        Index(
            "ix_recommendation_company_status",
            "company_id",
            "status",
        ),

        Index(
            "ix_recommendation_company_priority",
            "company_id",
            "priority",
        ),

        Index(
            "ix_recommendation_company_created",
            "company_id",
            "created_at",
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

    upload_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "uploads.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    forecast_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "forecasts.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # company_id comes from OwnershipMixin

    # =====================================================
    # Recommendation Identity
    # =====================================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    # =====================================================
    # Recommendation Content
    # =====================================================

    recommendation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    expected_outcome: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    suggested_action: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Priority & Impact
    # =====================================================

    priority: Mapped[RecommendationPriority] = mapped_column(
        Enum(
            RecommendationPriority,
            name="recommendation_priority_enum",
        ),
        default=RecommendationPriority.MEDIUM,
        nullable=False,
        index=True,
    )

    priority_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    impact_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # =====================================================
    # Business Impact
    # =====================================================

    estimated_cost: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    estimated_savings: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    estimated_revenue_impact: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    roi_percentage: Mapped[float | None] = mapped_column(
        Float,
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

    source_data: Mapped[dict | list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    ai_explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Processing
    # =====================================================

    status: Mapped[RecommendationStatus] = mapped_column(
        Enum(
            RecommendationStatus,
            name="recommendation_status_enum",
        ),
        default=RecommendationStatus.PENDING,
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
    # Execution / Tracking
    # =====================================================

    action_taken: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    action_taken_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    action_notes: Mapped[str | None] = mapped_column(
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

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # =====================================================
    # Relationships
    # =====================================================

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="recommendations",
        lazy="selectin",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="recommendations",
        lazy="selectin",
    )

    upload: Mapped["Upload | None"] = relationship(
        "Upload",
        back_populates="recommendations",
        lazy="selectin",
    )

    forecast: Mapped["Forecast | None"] = relationship(
        "Forecast",
        lazy="selectin",
    )

    # =====================================================
    # Helper Properties
    # =====================================================

    @property
    def is_completed(self) -> bool:
        """
        Returns True if recommendation generation completed.
        """

        return self.status == RecommendationStatus.COMPLETED

    @property
    def is_processing(self) -> bool:
        """
        Returns True if recommendation generation is running.
        """

        return self.status == RecommendationStatus.PROCESSING

    @property
    def is_failed(self) -> bool:
        """
        Returns True if recommendation generation failed.
        """

        return self.status == RecommendationStatus.FAILED

    @property
    def is_pending(self) -> bool:
        """
        Returns True if recommendation is pending.
        """

        return self.status == RecommendationStatus.PENDING

    @property
    def is_deleted(self) -> bool:
        """
        Returns True if recommendation was soft-deleted.
        """

        return self.deleted_at is not None

    @property
    def is_archived_status(self) -> bool:
        """
        Returns True if recommendation is archived.
        """

        return self.is_archived

    @property
    def has_confidence_score(self) -> bool:
        """
        Returns True if a confidence score exists.
        """

        return self.confidence_score is not None

    @property
    def has_impact_score(self) -> bool:
        """
        Returns True if an impact score exists.
        """

        return self.impact_score is not None

    @property
    def has_priority_score(self) -> bool:
        """
        Returns True if a priority score exists.
        """

        return self.priority_score is not None

    @property
    def has_reasoning(self) -> bool:
        """
        Returns True if AI reasoning exists.
        """

        return bool(
            self.reasoning
            and self.reasoning.strip()
        )

    @property
    def has_explanation(self) -> bool:
        """
        Returns True if an AI explanation exists.
        """

        return bool(
            self.ai_explanation
            and self.ai_explanation.strip()
        )

    @property
    def has_error(self) -> bool:
        """
        Returns True if an error was recorded.
        """

        return bool(
            self.error_message
            and self.error_message.strip()
        )

    @property
    def completion_percentage(self) -> int:
        """
        Returns recommendation processing progress.
        """

        return self.progress

    @property
    def processing_duration(self) -> int | None:
        """
        Returns recommendation processing duration.
        """

        return self.processing_time_seconds

    @property
    def has_business_impact(self) -> bool:
        """
        Returns True if business impact data exists.
        """

        return any(
            value is not None
            for value in (
                self.estimated_cost,
                self.estimated_savings,
                self.estimated_revenue_impact,
                self.roi_percentage,
            )
        )

    @property
    def can_be_used(self) -> bool:
        """
        Returns True if the recommendation is available
        for business decision support.
        """

        return (
            self.is_completed
            and self.is_active
            and not self.is_archived
            and not self.is_deleted
        )

    @property
    def is_actioned(self) -> bool:
        """
        Returns True if the recommended action was taken.
        """

        return self.action_taken

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<Recommendation("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"company_id={self.company_id}, "
            f"upload_id={self.upload_id}, "
            f"forecast_id={self.forecast_id}, "
            f"priority='{self.priority.value}', "
            f"status='{self.status.value}'"
            f")>"
        )