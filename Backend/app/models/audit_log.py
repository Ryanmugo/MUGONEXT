"""
=========================================================
MUGONEXT
Audit Log Model
=========================================================

Represents an immutable record of an important action
performed within the MUGONEXT platform.

Used for
✓ Security Auditing
✓ User Activity Tracking
✓ Administrative Actions
✓ Authentication Events
✓ Dataset Activity
✓ Forecast Activity
✓ Recommendation Activity
✓ Compliance
✓ Troubleshooting

Author:
MUGONEXT
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
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

from app.models.base import BaseModel
from app.models.mixins.ownership import OwnershipMixin


class AuditLog(
    BaseModel,
    OwnershipMixin,
):
    """
    Represents an audit event generated within MUGONEXT.

    Audit logs should generally be treated as immutable records.
    """

    __tablename__ = "audit_logs"

    __table_args__ = (
        Index(
            "ix_audit_company_created",
            "company_id",
            "created_at",
        ),
        Index(
            "ix_audit_company_action",
            "company_id",
            "action",
        ),
        Index(
            "ix_audit_company_user",
            "company_id",
            "user_id",
        ),
        Index(
            "ix_audit_resource",
            "resource_type",
            "resource_id",
        ),
    )

    # =====================================================
    # Ownership
    # =====================================================

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # company_id comes from OwnershipMixin

    # =====================================================
    # Event Identity
    # =====================================================

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Resource Information
    # =====================================================

    resource_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    resource_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    resource_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =====================================================
    # Request Information
    # =====================================================

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    endpoint: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    http_method: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # =====================================================
    # Event Details
    # =====================================================

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    old_values: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    new_values: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # =====================================================
    # Security
    # =====================================================

    success: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # =====================================================
    # Timestamp
    # =====================================================

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # =====================================================
    # Relationships
    # =====================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="audit_logs",
        lazy="selectin",
    )

    # =====================================================
    # Helper Properties
    # =====================================================

    @property
    def is_successful(self) -> bool:
        """
        Returns True when the audited action succeeded.
        """

        return self.success

    @property
    def is_failed(self) -> bool:
        """
        Returns True when the audited action failed.
        """

        return not self.success

    @property
    def has_resource(self) -> bool:
        """
        Returns True when this event is associated with
        a specific resource.
        """

        return (
            self.resource_type is not None
            and self.resource_id is not None
        )

    @property
    def has_metadata(self) -> bool:
        """
        Returns True when additional event metadata exists.
        """

        return bool(self.metadata_json)

    @property
    def has_changes(self) -> bool:
        """
        Returns True when old or new values were recorded.
        """

        return bool(
            self.old_values
            or self.new_values
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<AuditLog("
            f"id={self.id}, "
            f"company_id={self.company_id}, "
            f"user_id={self.user_id}, "
            f"action='{self.action}', "
            f"event_type='{self.event_type}', "
            f"success={self.success}"
            f")>"
        )