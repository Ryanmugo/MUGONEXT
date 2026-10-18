"""
=========================================================
MUGONEXT
Chat Session Model
=========================================================

Represents an AI/RAG conversation session.

Used for
--------
✓ AI Conversations
✓ RAG
✓ Dataset Questions
✓ Forecast Questions
✓ Recommendation Questions
✓ Business Intelligence
✓ Conversation History

Author:
MUGONEXT
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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


class ChatSession(
    BaseModel,
    OwnershipMixin,
):
    """
    Represents an AI conversation session belonging
    to a company and user.
    """

    __tablename__ = "chat_sessions"

    # =====================================================
    # Table Constraints & Indexes
    # =====================================================

    __table_args__ = (
        CheckConstraint(
            "message_count >= 0",
            name="ck_chat_session_message_count",
        ),
        CheckConstraint(
            "token_count >= 0",
            name="ck_chat_session_token_count",
        ),
        CheckConstraint(
            "top_k_results > 0",
            name="ck_chat_session_top_k_results",
        ),
        CheckConstraint(
            "temperature IS NULL OR "
            "(temperature >= 0 AND temperature <= 2)",
            name="ck_chat_session_temperature",
        ),
        CheckConstraint(
            "max_tokens IS NULL OR max_tokens > 0",
            name="ck_chat_session_max_tokens",
        ),
        Index(
            "ix_chat_session_company_user",
            "company_id",
            "user_id",
        ),
        Index(
            "ix_chat_session_company_upload",
            "company_id",
            "upload_id",
        ),
        Index(
            "ix_chat_session_company_active",
            "company_id",
            "is_active",
        ),
        Index(
            "ix_chat_session_company_created",
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
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # company_id comes from OwnershipMixin

    # =====================================================
    # Session Identity
    # =====================================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    session_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # =====================================================
    # Conversation Information
    # =====================================================

    message_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    token_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # =====================================================
    # AI Configuration
    # =====================================================

    ai_provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    model_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    model_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    system_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    temperature: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    max_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # =====================================================
    # RAG Configuration
    # =====================================================

    rag_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    retrieval_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    top_k_results: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )

    retrieved_documents: Mapped[list | dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # =====================================================
    # Conversation Context
    # =====================================================

    context: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # =====================================================
    # Processing
    # =====================================================

    is_processing: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    last_error: Mapped[str | None] = mapped_column(
        String(2000),
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
        back_populates="chat_sessions",
        lazy="selectin",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="chat_sessions",
        lazy="selectin",
    )

    upload: Mapped["Upload | None"] = relationship(
        "Upload",
        back_populates="chat_sessions",
        lazy="selectin",
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="chat_session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # =====================================================
    # Helper Properties
    # =====================================================

    @property
    def is_deleted(self) -> bool:
        """
        Returns True if the session has been soft-deleted.
        """

        return self.deleted_at is not None

    @property
    def has_messages(self) -> bool:
        """
        Returns True if the session contains messages.
        """

        return self.message_count > 0

    @property
    def has_context(self) -> bool:
        """
        Returns True if conversation context exists.
        """

        return bool(self.context)

    @property
    def has_retrieved_documents(self) -> bool:
        """
        Returns True if RAG retrieval returned documents.
        """

        return bool(self.retrieved_documents)

    @property
    def has_error(self) -> bool:
        """
        Returns True if the session has an error.
        """

        return bool(
            self.last_error
            and self.last_error.strip()
        )

    @property
    def is_rag_ready(self) -> bool:
        """
        Returns True if RAG functionality can be used.
        """

        return (
            self.is_active
            and not self.is_archived
            and not self.is_deleted
            and self.rag_enabled
            and self.retrieval_enabled
        )

    @property
    def can_chat(self) -> bool:
        """
        Returns True if the session can accept messages.
        """

        return (
            self.is_active
            and not self.is_archived
            and not self.is_deleted
            and not self.is_processing
        )

    @property
    def has_ai_configuration(self) -> bool:
        """
        Returns True if an AI model has been configured.
        """

        return bool(
            self.ai_provider
            and self.model_name
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<ChatSession("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"company_id={self.company_id}, "
            f"user_id={self.user_id}, "
            f"messages={self.message_count}, "
            f"active={self.is_active}"
            f")>"
        )