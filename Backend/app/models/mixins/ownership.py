"""
=========================================================
MUGONEXT
Ownership Mixin
=========================================================

Provides common ownership fields for models that belong
to a company and optionally to a specific user.

Used for
--------
✓ Multi-Tenant Architecture
✓ Company-Level Data Isolation
✓ Shared Ownership Logic
✓ Security
✓ Authorization
✓ Query Filtering

Author:
MUGONEXT
"""

from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class OwnershipMixin:
    """
    Provides multi-tenant ownership information.

    Every model using this mixin belongs to exactly one
    company.

    company_id identifies the organization that owns the
    record.

    Individual models may additionally define user_id
    when a record is associated with a specific user.
    """

    # =====================================================
    # Company Ownership
    # =====================================================

    company_id: Mapped[int] = mapped_column(
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )