"""
=========================================================
MUGONEXT
Chat Message Model
=========================================================

Represents an individual message inside an AI chat session.

Used for
--------
✓ User Questions
✓ AI Responses
✓ RAG Context
✓ Source Citations
✓ Conversation History
✓ Token Tracking
✓ AI Usage Analytics

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
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import ChatRole

from app.models.base import BaseModel
from app.models.mixins.ownership import OwnershipMixin


class ChatMessage(
    BaseModel,
    OwnershipMixin,
):
    """
    Represents a single message belonging to a chat session.
    """

    __tablename__ = "chat_messages"

    # =====================================================
    # Table Constraints & Indexes
    # =====================================================

    __table_args__ = (
        CheckConstraint(
            "input_tokens IS NULL OR input_tokens >= 0",
            name="ck_chat_message_input_tokens",
        ),

        CheckConstraint(
            "output_tokens IS NULL OR output_tokens >= 0",
            name="ck_chat_message_output_tokens",
        ),

        CheckConstraint(
            "total_tokens IS NULL OR total_tokens >= 0",
            name="ck_chat_message_total_tokens",
        ),

        CheckConstraint(
            "retrieval_count >= 0",
            name="ck_chat_message_retrieval_count",
        ),

        CheckConstraint(
            "processing_time_ms IS NULL "
            "OR processing_time_ms >= 0",
            name="ck_chat_message_processing_time",
        ),

        CheckConstraint(
            "sequence_number >= 0",
            name="ck_chat_message_sequence_number",
        ),

        Index(
            "ix_chat_message_company_session",
            "company_id",
            "chat_session_id",
        ),

        Index(
            "ix_chat_message_company_user",
            "company_id",
            "user_id",
        ),

        Index(
            "ix_chat_message_session_created",
            "chat_session_id",
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

    chat_session_id: Mapped[int] = mapped_column(
        ForeignKey(
            "chat_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # company_id comes from OwnershipMixin

    # =====================================================
    # Message Identity
    # =====================================================

    role: Mapped[ChatRole] = mapped_column(
        Enum(
            ChatRole,
            name="chat_message_role_enum",
        ),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # =====================================================
    # AI Metadata
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

    # =====================================================
    # Token Usage
    # =====================================================

    input_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    output_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    total_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # =====================================================
    # RAG Information
    # =====================================================

    rag_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    retrieval_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    retrieved_context: Mapped[list | dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    sources: Mapped[list | dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    citations: Mapped[list | dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # =====================================================
    # Message Metadata
    # =====================================================

    message_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # =====================================================
    # Processing
    # =====================================================

    processing_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
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

    is_deleted: Mapped[bool] = mapped_column(
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

    chat_session: Mapped["ChatSession"] = relationship(
        "ChatSession",
        back_populates="messages",
        lazy="selectin",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="chat_messages",
        lazy="selectin",
    )

    # =====================================================
    # Helper Properties
    # =====================================================

    @property
    def is_user_message(self) -> bool:
        """Returns True if this message was created by the user."""

        return self.role == ChatRole.USER

    @property
    def is_assistant_message(self) -> bool:
        """Returns True if this message was generated by the AI."""

        return self.role == ChatRole.ASSISTANT

    @property
    def is_system_message(self) -> bool:
        """Returns True if this is a system message."""

        return self.role == ChatRole.SYSTEM

    @property
    def has_rag_context(self) -> bool:
        """Returns True if RAG context was retrieved."""

        return bool(self.retrieved_context)

    @property
    def has_sources(self) -> bool:
        """Returns True if sources were attached."""

        return bool(self.sources)

    @property
    def has_citations(self) -> bool:
        """Returns True if citations were attached."""

        return bool(self.citations)

    @property
    def has_token_usage(self) -> bool:
        """Returns True if token usage was recorded."""

        return self.total_tokens is not None

    @property
    def has_error(self) -> bool:
        """Returns True if an error was recorded."""

        return bool(
            self.error_message
            and self.error_message.strip()
        )

    @property
    def is_deleted_message(self) -> bool:
        """Returns True if the message was soft-deleted."""

        return (
            self.is_deleted
            or self.deleted_at is not None
        )

    @property
    def word_count(self) -> int:
        """Returns the approximate number of words."""

        if not self.content:
            return 0

        return len(self.content.split())

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<ChatMessage("
            f"id={self.id}, "
            f"chat_session_id={self.chat_session_id}, "
            f"company_id={self.company_id}, "
            f"role='{self.role.value}', "
            f"sequence={self.sequence_number}"
            f")>"
        )