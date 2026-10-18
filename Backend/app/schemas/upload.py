from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.constants import (
    FileType,
    StorageProvider,
    UploadSource,
    UploadStatus,
)


class UploadCreate(BaseModel):
    original_filename: str
    stored_filename: str
    file_extension: FileType
    mime_type: str
    file_size: int
    storage_path: str
    dataset_name: str
    description: str | None = None
    rows: int | None = None
    columns: int | None = None
    column_metadata: dict | None = None
    target_column: str | None = None
    date_column: str | None = None
    sheet_name: str | None = None
    encoding: str = "utf-8"
    delimiter: str | None = None
    storage_provider: StorageProvider = StorageProvider.LOCAL
    upload_source: UploadSource = UploadSource.WEB


class UploadUpdate(BaseModel):
    dataset_name: str | None = None
    description: str | None = None
    target_column: str | None = None
    date_column: str | None = None
    sheet_name: str | None = None


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    user_id: int

    original_filename: str
    stored_filename: str
    file_extension: FileType
    mime_type: str
    file_size: int

    storage_path: str
    storage_provider: StorageProvider

    dataset_name: str
    dataset_version: int
    description: str | None

    rows: int | None
    columns: int | None
    column_metadata: dict | None

    target_column: str | None
    date_column: str | None
    sheet_name: str | None

    encoding: str
    delimiter: str | None

    status: UploadStatus
    upload_source: UploadSource
    progress: int

    validation_passed: bool
    missing_values_count: int
    duplicate_rows_count: int
    data_quality_score: float | None

    data_drift_detected: bool
    preview_generated: bool
    is_processed: bool
    is_archived: bool

    deleted_at: datetime | None

    ai_summary: str | None
    embedding_generated: bool
    vector_indexed: bool
    rag_ready: bool
    recommendation_generated: bool
    forecast_generated: bool

    created_at: datetime
    updated_at: datetime