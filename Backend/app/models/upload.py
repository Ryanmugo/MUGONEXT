"""
=========================================================
MUGONEXT
Upload Model
=========================================================

Represents a dataset uploaded by a company.

Used for
--------
✓ Forecasting
✓ Recommendations
✓ Data Analysis
✓ Visualizations
✓ AI Processing
✓ RAG
✓ Dataset Versioning

Author:
MUGONEXT
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.constants import (
    FileType,
    ForecastModel,
    StorageProvider,
    UploadSource,
    UploadStatus,
)

from app.models.base import BaseModel
from app.models.mixins.ownership import OwnershipMixin


class Upload(
    BaseModel,
    OwnershipMixin,
):
    """
    Represents a dataset uploaded by a company.
    """

    __tablename__ = "uploads"

    # =====================================================
    # Table Constraints & Indexes
    # =====================================================

    __table_args__ = (
        CheckConstraint(
            "progress >= 0 AND progress <= 100",
            name="ck_upload_progress",
        ),
        CheckConstraint(
            "rows IS NULL OR rows >= 0",
            name="ck_upload_rows",
        ),
        CheckConstraint(
            "columns IS NULL OR columns >= 0",
            name="ck_upload_columns",
        ),
        CheckConstraint(
            "file_size > 0",
            name="ck_upload_file_size",
        ),
        Index(
            "ix_upload_company_dataset",
            "company_id",
            "dataset_name",
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

    # company_id comes from OwnershipMixin

    # =====================================================
    # File Information
    # =====================================================

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    file_extension: Mapped[FileType] = mapped_column(
        Enum(
            FileType,
            name="file_type_enum",
        ),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # =====================================================
    # Storage Information
    # =====================================================

    storage_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    storage_provider: Mapped[StorageProvider] = mapped_column(
        Enum(
            StorageProvider,
            name="storage_provider_enum",
        ),
        default=StorageProvider.LOCAL,
        nullable=False,
    )

    file_hash: Mapped[str | None] = mapped_column(
        String(128),
        unique=True,
        nullable=True,
        index=True,
    )

    checksum_algorithm: Mapped[str] = mapped_column(
        String(20),
        default="sha256",
        nullable=False,
    )

    # =====================================================
    # Dataset Information
    # =====================================================

    dataset_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    dataset_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    rows: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    columns: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    column_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    target_column: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    date_column: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    sheet_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    encoding: Mapped[str] = mapped_column(
        String(50),
        default="utf-8",
        nullable=False,
    )

    delimiter: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    # =====================================================
    # Processing Information
    # =====================================================

    status: Mapped[UploadStatus] = mapped_column(
        Enum(
            UploadStatus,
            name="upload_status_enum",
        ),
        default=UploadStatus.PENDING,
        nullable=False,
        index=True,
    )

    upload_source: Mapped[UploadSource] = mapped_column(
        Enum(
            UploadSource,
            name="upload_source_enum",
        ),
        default=UploadSource.WEB,
        nullable=False,
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    processing_completed_at: Mapped[datetime | None] = mapped_column(
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

    validation_passed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    missing_values_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    duplicate_rows_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    data_quality_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    data_drift_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    preview_generated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_processed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
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
    # AI Information
    # =====================================================

    forecast_model_used: Mapped[ForecastModel | None] = mapped_column(
        Enum(
            ForecastModel,
            name="forecast_model_enum",
        ),
        nullable=True,
    )

    ai_summary: Mapped[str | None] = mapped_column(
        String(5000),
        nullable=True,
    )

    embedding_generated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    vector_indexed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    rag_ready: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    recommendation_generated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    forecast_generated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    ai_processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    ai_processing_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    llm_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # =====================================================
    # Relationships
    # =====================================================

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="uploads",
        lazy="selectin",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="uploads",
        lazy="selectin",
    )

    forecasts: Mapped[list["Forecast"]] = relationship(
        "Forecast",
        back_populates="upload",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="upload",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="upload",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # =====================================================
    # Helper Properties
    # =====================================================

    @property
    def size_mb(self) -> float:
        """
        Returns the file size in MB.
        """

        return round(
            self.file_size / (1024 * 1024),
            2,
        )

    @property
    def filename(self) -> str:
        """
        Returns the original filename.
        """

        return self.original_filename

    @property
    def is_completed(self) -> bool:
        """
        Returns True if processing completed successfully.
        """

        return self.status == UploadStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """
        Returns True if processing failed.
        """

        return self.status == UploadStatus.FAILED

    @property
    def is_processing(self) -> bool:
        """
        Returns True if processing is currently running.
        """

        return self.status == UploadStatus.PROCESSING

    @property
    def is_deleted(self) -> bool:
        """
        Returns True if the upload has been soft-deleted.
        """

        return self.deleted_at is not None

    @property
    def can_generate_forecast(self) -> bool:
        """
        Returns True if the dataset is ready for forecasting.
        """

        return (
            self.is_processed
            and self.validation_passed
            and not self.forecast_generated
            and not self.is_deleted
        )

    @property
    def can_generate_recommendations(self) -> bool:
        """
        Returns True if the dataset is ready for recommendations.
        """

        return (
            self.is_processed
            and self.validation_passed
            and not self.recommendation_generated
            and not self.is_deleted
        )

    @property
    def can_run_ai(self) -> bool:
        """
        Returns True if the dataset can enter the AI pipeline.
        """

        return (
            self.is_processed
            and self.validation_passed
            and self.status == UploadStatus.COMPLETED
            and not self.is_deleted
        )

    @property
    def is_ready_for_rag(self) -> bool:
        """
        Returns True if the dataset is ready for RAG.
        """

        return (
            self.embedding_generated
            and self.vector_indexed
            and self.rag_ready
            and not self.is_deleted
        )

    @property
    def has_embeddings(self) -> bool:
        """
        Returns True if embeddings have been generated.
        """

        return self.embedding_generated

    @property
    def has_forecast(self) -> bool:
        """
        Returns True if a forecast has been generated.
        """

        return self.forecast_generated

    @property
    def has_recommendations(self) -> bool:
        """
        Returns True if recommendations have been generated.
        """

        return self.recommendation_generated

    @property
    def has_preview(self) -> bool:
        """
        Returns True if a dataset preview exists.
        """

        return self.preview_generated

    @property
    def has_data_quality_score(self) -> bool:
        """
        Returns True if a data quality score exists.
        """

        return self.data_quality_score is not None

    @property
    def has_errors(self) -> bool:
        """
        Returns True if an error was recorded.
        """

        return self.error_message is not None

    @property
    def processing_duration(self) -> int | None:
        """
        Returns the recorded processing duration.
        """

        return self.processing_time_seconds

    @property
    def completion_percentage(self) -> int:
        """
        Returns processing progress.
        """

        return self.progress

    @property
    def is_versioned(self) -> bool:
        """
        Returns True if this dataset has multiple versions.
        """

        return self.dataset_version > 1

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<Upload("
            f"id={self.id}, "
            f"dataset='{self.dataset_name}', "
            f"user_id={self.user_id}, "
            f"company_id={self.company_id}, "
            f"status='{self.status.value}'"
            f")>"
        )