"""
=========================================================
MUGONEXT
API Key Model
=========================================================

Represents an API key belonging to a MUGONEXT user/company.

Author:
MUGONEXT
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins.ownership import OwnershipMixin


class ApiKey(
    BaseModel,
    OwnershipMixin,
):
    """
    Represents an API key belonging to a user and company.
    """

    __tablename__ = "api_keys"

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

    # company_id comes from OwnershipMixin

    # =====================================================
    # API Key Information
    # =====================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    key_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    key_prefix: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
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

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =====================================================
    # Relationships
    # =====================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="api_keys",
        lazy="selectin",
    )

    company: Mapped["Company"] = relationship(
        "Company",
        lazy="selectin",
    )

    # =====================================================
    # Helper Properties
    # =====================================================

    @property
    def is_expired(self) -> bool:
        """
        Returns True if the API key has expired.
        """

        if self.expires_at is None:
            return False

        return self.expires_at <= datetime.now(
            self.expires_at.tzinfo
        )

    @property
    def is_revoked(self) -> bool:
        """
        Returns True if the API key has been revoked.
        """

        return self.revoked_at is not None

    @property
    def can_be_used(self) -> bool:
        """
        Returns True if the API key can currently be used.
        """

        return (
            self.is_active
            and not self.is_expired
            and not self.is_revoked
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<ApiKey("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"user_id={self.user_id}, "
            f"company_id={self.company_id}, "
            f"active={self.is_active}"
            f")>"
        )