"""
=========================================================
MUGONEXT
User Model
=========================================================

Represents a user within a MUGONEXT organization.

Features
--------
✓ Authentication
✓ Authorization
✓ User Profile
✓ Security
✓ Preferences
✓ Multi-Tenant Support
✓ Account Lifecycle
✓ User Relationships

Author:
MUGONEXT
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.constants import (
    AccountStatus,
    UserRole,
)

from app.models.base import BaseModel
from app.models.mixins.ownership import OwnershipMixin


class User(
    BaseModel,
    OwnershipMixin,
):
    """
    Represents a user belonging to a company.
    """

    __tablename__ = "users"

    # =====================================================
    # Identity
    # =====================================================

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    # =====================================================
    # Profile
    # =====================================================

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    profile_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # =====================================================
    # Contact Information
    # =====================================================

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # =====================================================
    # Authentication
    # =====================================================

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    password_reset_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    password_reset_token: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    password_reset_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    login_provider: Mapped[str] = mapped_column(
        String(50),
        default="local",
        nullable=False,
    )

    refresh_token_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # =====================================================
    # Authorization
    # =====================================================

    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role_enum",
        ),
        default=UserRole.VIEWER,
        nullable=False,
        index=True,
    )

    account_status: Mapped[AccountStatus] = mapped_column(
        Enum(
            AccountStatus,
            name="account_status_enum",
        ),
        default=AccountStatus.PENDING,
        nullable=False,
        index=True,
    )

    # =====================================================
    # Security
    # =====================================================

    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    email_verification_token: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    email_verification_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_activity_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_failed_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    login_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    mfa_secret: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =====================================================
    # Lifecycle
    # =====================================================

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # =====================================================
    # User Preferences
    # =====================================================

    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        default="UTC",
        nullable=False,
    )

    receive_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    theme: Mapped[str] = mapped_column(
        String(20),
        default="system",
        nullable=False,
    )

    # =====================================================
    # Account Creation Tracking
    # =====================================================

    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # =====================================================
    # Relationships
    # =====================================================

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="users",
        lazy="selectin",
    )

    created_by: Mapped["User | None"] = relationship(
        "User",
        remote_side="User.id",
        foreign_keys=[created_by_user_id],
        back_populates="created_users",
        lazy="selectin",
    )

    created_users: Mapped[list["User"]] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="created_by",
        lazy="selectin",
    )

    uploads: Mapped[list["Upload"]] = relationship(
        "Upload",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    forecasts: Mapped[list["Forecast"]] = relationship(
        "Forecast",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        lazy="selectin",
    )

    api_keys: Mapped[list["ApiKey"]] = relationship(
        "ApiKey",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # =====================================================
    # Helper Properties
    # =====================================================

    @property
    def full_name(self) -> str:
        """
        Returns the preferred display name.
        """

        if self.display_name and self.display_name.strip():
            return self.display_name

        return f"{self.first_name} {self.last_name}".strip()

    @property
    def initials(self) -> str:
        """
        Returns the user's initials.
        """

        return (
            self.first_name[:1]
            + self.last_name[:1]
        ).upper()

    @property
    def is_locked(self) -> bool:
        """
        Returns True if the account is currently locked.
        """

        if self.locked_until is None:
            return False

        return self.locked_until > datetime.now(
            self.locked_until.tzinfo
        )

    @property
    def is_verified(self) -> bool:
        """
        Returns True if the user's email is verified.
        """

        return self.email_verified_at is not None

    @property
    def is_active(self) -> bool:
        """
        Returns True if the account is active.
        """

        return self.account_status == AccountStatus.ACTIVE

    @property
    def has_mfa(self) -> bool:
        """
        Returns True if MFA is enabled.
        """

        return self.mfa_enabled

    @property
    def can_login(self) -> bool:
        """
        Returns True when the minimum authentication
        requirements are satisfied.
        """

        return (
            self.is_active
            and not self.is_locked
            and self.is_verified
            and not self.is_deleted
        )

    @property
    def is_admin(self) -> bool:
        """
        Returns True if the user is an administrator.
        """

        return self.role == UserRole.ADMIN

    @property
    def is_owner(self) -> bool:
        """
        Returns True if the user is the company owner.
        """

        return self.role == UserRole.OWNER

    @property
    def is_manager(self) -> bool:
        """
        Returns True if the user is a manager.
        """

        return self.role == UserRole.MANAGER

    @property
    def can_manage_users(self) -> bool:
        """
        Returns True if the user can manage other users.
        """

        return self.role in (
            UserRole.OWNER,
            UserRole.ADMIN,
        )

    @property
    def is_deleted(self) -> bool:
        """
        Returns True if the account has been soft-deleted.
        """

        return self.deleted_at is not None

    @property
    def password_age_days(self) -> int | None:
        """
        Returns the age of the current password in days.
        """

        if self.password_changed_at is None:
            return None

        return (
            datetime.now(self.password_changed_at.tzinfo)
            - self.password_changed_at
        ).days

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<User("
            f"id={self.id}, "
            f"company_id={self.company_id}, "
            f"email='{self.email}', "
            f"role='{self.role.value}', "
            f"status='{self.account_status.value}'"
            f")>"
        )