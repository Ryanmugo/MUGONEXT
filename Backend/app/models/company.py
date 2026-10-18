"""
=========================================================
MUGONEXT
Company Model
=========================================================

Represents an organization/company using MUGONEXT.

A company is the primary tenant in the MUGONEXT platform.

Used for
✓ Multi-Tenant Architecture
✓ User Management
✓ Dataset Management
✓ Forecasting
✓ Recommendations
✓ AI Chat
✓ Subscriptions
✓ Usage Tracking
✓ Company Preferences

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
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from constants import (
    CompanyStatus,
    SubscriptionPlan,
)

from app.models.base import BaseModel


class Company(BaseModel):
    """
    Represents a company using MUGONEXT.

    The company is the primary tenant. Users, uploads,
    forecasts, recommendations, and chat sessions belong
    to a company.
    """

    __tablename__ = "companies"

    __table_args__ = (
        CheckConstraint(
            "forecasts_used_this_month >= 0",
            name="ck_company_forecasts_used",
        ),
        Index(
            "ix_company_status_active",
            "status",
            "is_active",
        ),
        Index(
            "ix_company_country",
            "country",
        ),
    )

    # =====================================================
    # Identity
    # =====================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    legal_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    logo_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # =====================================================
    # Contact Information
    # =====================================================

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # =====================================================
    # Platform Preferences
    # =====================================================

    timezone: Mapped[str] = mapped_column(
        String(100),
        default="UTC",
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="USD",
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )

    # =====================================================
    # Subscription
    # =====================================================

    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(
            SubscriptionPlan,
            name="subscription_plan_enum",
        ),
        default=SubscriptionPlan.FREE,
        nullable=False,
        index=True,
    )

    subscription_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    subscription_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =====================================================
    # Account Status
    # =====================================================

    status: Mapped[CompanyStatus] = mapped_column(
        Enum(
            CompanyStatus,
            name="company_status_enum",
        ),
        default=CompanyStatus.TRIAL,
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # =====================================================
    # AI / Usage
    # =====================================================

    forecasts_used_this_month: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # =====================================================
    # Relationships
    # =====================================================

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    uploads: Mapped[list["Upload"]] = relationship(
        "Upload",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    forecasts: Mapped[list["Forecast"]] = relationship(
        "Forecast",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # =====================================================
    # Helper Properties
    # =====================================================

    @property
    def is_trial(self) -> bool:
        """
        Returns True if the company is currently on trial.
        """

        return self.status == CompanyStatus.TRIAL

    @property
    def is_subscription_active(self) -> bool:
        """
        Returns True if the company's subscription is active.
        """

        if self.status != CompanyStatus.ACTIVE:
            return False

        if self.subscription_expires_at is None:
            return True

        return (
            self.subscription_expires_at
            > datetime.now(
                self.subscription_expires_at.tzinfo
            )
        )

    @property
    def is_trial_expired(self) -> bool:
        """
        Returns True if the company's trial has expired.
        """

        if self.trial_ends_at is None:
            return False

        return (
            datetime.now(
                self.trial_ends_at.tzinfo
            )
            > self.trial_ends_at
        )

    @property
    def can_use_platform(self) -> bool:
        """
        Returns True when the company is allowed to use
        the MUGONEXT platform.
        """

        if not self.is_active:
            return False

        if self.status == CompanyStatus.TRIAL:
            return not self.is_trial_expired

        if self.status == CompanyStatus.ACTIVE:
            return self.is_subscription_active

        return False

    @property
    def forecast_usage(self) -> int:
        """
        Returns the number of forecasts used this month.
        """

        return self.forecasts_used_this_month

    @property
    def has_users(self) -> bool:
        """
        Returns True when the company has users.
        """

        return bool(self.users)

    @property
    def has_uploads(self) -> bool:
        """
        Returns True when the company has uploaded datasets.
        """

        return bool(self.uploads)

    @property
    def has_forecasts(self) -> bool:
        """
        Returns True when the company has forecasts.
        """

        return bool(self.forecasts)

    @property
    def has_recommendations(self) -> bool:
        """
        Returns True when the company has recommendations.
        """

        return bool(self.recommendations)

    @property
    def has_chat_sessions(self) -> bool:
        """
        Returns True when the company has AI conversations.
        """

        return bool(self.chat_sessions)

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<Company("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"slug='{self.slug}', "
            f"plan='{self.subscription_plan.value}', "
            f"status='{self.status.value}'"
            f")>"
        )