"""
=========================================================
MUGONEXT
Upload API Routes
=========================================================

Handles:

    - Real CSV / XLSX / XLS dataset uploads
    - Automatic Excel worksheet selection
    - Automatic date/target column detection
    - Dataset loading
    - Dataset preprocessing
    - Dataset validation
    - Data quality scoring
    - Upload metadata management
    - Company/tenant isolation

=========================================================
"""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_user,
    get_db,
    require_analyst,
    require_manager,
)

from app.constants import (
    FileType,
    StorageProvider,
    UploadSource,
    UploadStatus,
)

from app.core.config import BASE_DIR, settings
from app.models.upload import Upload
from app.models.user import User

from app.schemas.upload import (
    UploadCreate,
    UploadResponse,
    UploadUpdate,
)

from app.services.forecasting.loader import DatasetLoader
from app.services.forecasting.preprocessor import DatasetPreprocessor
from app.services.forecasting.validator import DatasetValidator


router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


# =========================================================
# CONSTANTS
# =========================================================

SUPPORTED_UPLOAD_EXTENSIONS = {
    ".csv": FileType.CSV,
    ".xlsx": FileType.XLSX,
    ".xls": FileType.XLS,
}


DATE_COLUMN_ALIASES = {
    "date",
    "datetime",
    "timestamp",
    "time",
    "orderdate",
    "transactiondate",
    "salesdate",
    "invoicedate",
    "purchasedate",
    "deliverydate",
    "createdat",
    "transactiontime",
    "ordertime",
    "businessdate",
    "recorddate",
    "reportdate",

    # Business datasets
    "saledate",
    "purchase_date",
    "launcheddate",
    "launchdate",
    "latestlaunch",
    "latestlaunched",
}


TARGET_COLUMN_ALIASES = {
    "sales",
    "sale",
    "revenue",
    "salesamount",
    "salesvalue",
    "salesinthousands",
    "totalsales",
    "totalsalesamount",
    "revenueamount",
    "amount",
    "total",
    "totalamount",
    "unitsold",
    "unitssold",
    "quantity",
    "qty",
    "volume",
    "turnover",
}


# =========================================================
# FILE / STORAGE HELPERS
# =========================================================

def _get_upload_directory() -> Path:
    upload_directory = BASE_DIR / settings.UPLOAD_FOLDER

    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return upload_directory


def _get_file_extension(
    filename: str | None,
) -> tuple[str, FileType]:
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required.",
        )

    extension = Path(filename).suffix.lower()

    file_type = SUPPORTED_UPLOAD_EXTENSIONS.get(
        extension
    )

    if file_type is None:
        supported_formats = ", ".join(
            sorted(
                SUPPORTED_UPLOAD_EXTENSIONS.keys()
            )
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported dataset format. "
                f"Supported formats: {supported_formats}."
            ),
        )

    return extension, file_type


def _generate_stored_filename(
    extension: str,
) -> str:
    return (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )


def _calculate_quality_score(
    dataframe: pd.DataFrame,
) -> float:
    return DatasetPreprocessor.calculate_quality_score(
        dataframe
    )


# =========================================================
# COLUMN NAME NORMALIZATION
# =========================================================

def _normalize_column_name(
    column: Any,
) -> str:
    return re.sub(
        r"[^a-z0-9]",
        "",
        str(column).strip().lower(),
    )


# =========================================================
# AUTOMATIC DATE COLUMN DETECTION
# =========================================================

def _detect_date_column(
    dataframe: pd.DataFrame,
) -> str:
    """
    Automatically detect the most likely date column.

    Detection order:

        1. Exact semantic aliases
        2. Date/time keyword columns
        3. Strong datetime parsing on non-numeric columns

    Numeric columns are ignored during generic date
    detection so sales, quantities, prices, IDs, etc.
    are not accidentally interpreted as dates.
    """

    columns = list(dataframe.columns)

    # =====================================================
    # 1. EXACT SEMANTIC MATCH
    # =====================================================

    for column in columns:
        normalized = _normalize_column_name(column)

        if normalized in DATE_COLUMN_ALIASES:
            return str(column)

    # =====================================================
    # 2. DATE/TIME KEYWORD MATCH
    # =====================================================

    keyword_candidates = []

    date_keywords = (
        "date",
        "datetime",
        "timestamp",
        "time",
        "launch",
    )

    for column in columns:
        normalized = _normalize_column_name(column)

        if any(
            keyword in normalized
            for keyword in date_keywords
        ):
            keyword_candidates.append(column)

    for column in keyword_candidates:
        series = dataframe[column]

        if pd.api.types.is_numeric_dtype(series):
            continue

        try:
            parsed = pd.to_datetime(
                series,
                errors="coerce",
                format="mixed",
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

        parse_ratio = float(
            parsed.notna().mean()
        )

        if parse_ratio >= 0.70:
            return str(column)

    # =====================================================
    # 3. GENERIC DATE DETECTION
    # =====================================================

    date_candidates: list[tuple[str, float]] = []

    for column in columns:
        series = dataframe[column]

        if pd.api.types.is_numeric_dtype(series):
            continue

        non_null = series.dropna()

        if non_null.empty:
            continue

        try:
            parsed = pd.to_datetime(
                series,
                errors="coerce",
                format="mixed",
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

        parse_ratio = float(
            parsed.notna().mean()
        )

        if parse_ratio >= 0.80:
            date_candidates.append(
                (
                    str(column),
                    parse_ratio,
                )
            )

    if date_candidates:
        date_candidates.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return date_candidates[0][0]

    raise ValueError(
        "MUGONEXT could not automatically detect a "
        "date column. Please provide a column containing "
        "dates, such as Date, Order Date, Transaction Date, "
        "Invoice Date, Sales Date, Latest Launch, or Timestamp."
    )


# =========================================================
# AUTOMATIC TARGET COLUMN DETECTION
# =========================================================

def _detect_target_column(
    dataframe: pd.DataFrame,
    date_column: str,
) -> str:

    columns = list(dataframe.columns)

    # =====================================================
    # 1. EXACT SEMANTIC MATCHES
    # =====================================================

    alias_candidates = []

    for column in columns:

        if str(column) == str(date_column):
            continue

        normalized = _normalize_column_name(
            column
        )

        if normalized in TARGET_COLUMN_ALIASES:
            alias_candidates.append(column)

    if len(alias_candidates) == 1:
        return str(alias_candidates[0])

    # =====================================================
    # 2. SEVERAL SEMANTIC CANDIDATES
    # =====================================================

    if alias_candidates:

        priority_keywords = (
            "sales",
            "revenue",
            "amount",
            "total",
            "turnover",
            "unitsold",
            "quantity",
            "volume",
        )

        for keyword in priority_keywords:

            for column in alias_candidates:

                normalized = _normalize_column_name(
                    column
                )

                if keyword in normalized:

                    numeric_values = pd.to_numeric(
                        dataframe[column],
                        errors="coerce",
                    )

                    numeric_ratio = float(
                        numeric_values.notna().mean()
                    )

                    if numeric_ratio >= 0.70:
                        return str(column)

        return str(alias_candidates[0])

    # =====================================================
    # 3. KEYWORD + NUMERIC VALIDATION
    # =====================================================

    keyword_candidates = []

    target_keywords = (
        "sales",
        "revenue",
        "amount",
        "quantity",
        "qty",
        "unitsold",
        "volume",
        "turnover",
        "total",
    )

    for column in columns:

        if str(column) == str(date_column):
            continue

        normalized = _normalize_column_name(
            column
        )

        if any(
            keyword in normalized
            for keyword in target_keywords
        ):

            numeric_values = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

            numeric_ratio = float(
                numeric_values.notna().mean()
            )

            if numeric_ratio >= 0.70:

                keyword_candidates.append(
                    (
                        str(column),
                        numeric_ratio,
                    )
                )

    if keyword_candidates:

        keyword_candidates.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return keyword_candidates[0][0]

    # =====================================================
    # 4. NUMERIC COLUMN FALLBACK
    # =====================================================

    numeric_candidates = []

    for column in columns:

        if str(column) == str(date_column):
            continue

        numeric_values = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

        numeric_ratio = float(
            numeric_values.notna().mean()
        )

        if numeric_ratio >= 0.80:

            numeric_candidates.append(
                (
                    str(column),
                    numeric_ratio,
                )
            )

    if len(numeric_candidates) == 1:
        return numeric_candidates[0][0]

    if numeric_candidates:

        # Prefer columns that look like actual business
        # measurements instead of IDs or dimensions.
        preferred_keywords = (
            "sales",
            "revenue",
            "amount",
            "profit",
            "quantity",
            "units",
            "volume",
            "price",
            "value",
        )

        for keyword in preferred_keywords:

            for column, ratio in numeric_candidates:

                normalized = _normalize_column_name(
                    column
                )

                if keyword in normalized:
                    return column

        numeric_candidates.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return numeric_candidates[0][0]

    raise ValueError(
        "MUGONEXT could not automatically detect a "
        "sales or business-value column. Please provide "
        "a numeric column such as Sales, Revenue, Amount, "
        "Quantity, or Units Sold."
    )


# =========================================================
# RESOLVE DATASET COLUMNS
# =========================================================

def _detect_dataset_columns(
    dataframe: pd.DataFrame,
    target_column: str | None,
    date_column: str | None,
) -> tuple[str, str]:

    if dataframe.empty:
        raise ValueError(
            "The uploaded dataset contains no rows."
        )

    if len(dataframe.columns) < 2:
        raise ValueError(
            "The uploaded dataset must contain at least "
            "two columns: a date column and a business "
            "value column."
        )

    # =====================================================
    # DATE COLUMN
    # =====================================================

    if date_column:

        if date_column not in dataframe.columns:
            raise ValueError(
                f"The specified date column "
                f"'{date_column}' was not found in the "
                "uploaded dataset."
            )

        resolved_date_column = date_column

    else:

        resolved_date_column = _detect_date_column(
            dataframe
        )

    # =====================================================
    # TARGET COLUMN
    # =====================================================

    if target_column:

        if target_column not in dataframe.columns:
            raise ValueError(
                f"The specified target column "
                f"'{target_column}' was not found in the "
                "uploaded dataset."
            )

        resolved_target_column = target_column

    else:

        resolved_target_column = _detect_target_column(
            dataframe,
            resolved_date_column,
        )

    # =====================================================
    # SAME COLUMN CHECK
    # =====================================================

    if (
        resolved_target_column
        == resolved_date_column
    ):
        raise ValueError(
            "The detected date and target columns are "
            "the same. MUGONEXT requires separate columns."
        )

    return (
        resolved_target_column,
        resolved_date_column,
    )


# =========================================================
# EXCEL WORKSHEET INTELLIGENCE
# =========================================================

def _inspect_excel_sheets(
    file_path: Path,
) -> list[dict[str, Any]]:
    """
    Inspect every worksheet in an Excel workbook.

    Each sheet is evaluated for:

        - number of rows
        - number of columns
        - detectable date column
        - detectable target column
        - overall business-data score

    This allows MUGONEXT to ignore report/dashboard sheets
    and select the actual underlying business dataset.
    """

    try:
        excel_file = pd.ExcelFile(file_path)
    except Exception as exc:
        raise ValueError(
            f"Unable to open Excel workbook: {exc}"
        ) from exc

    inspections: list[dict[str, Any]] = []

    for sheet in excel_file.sheet_names:

        try:
            dataframe = pd.read_excel(
                file_path,
                sheet_name=sheet,
            )
        except Exception:
            continue

        dataframe = dataframe.dropna(
            how="all"
        )

        if dataframe.empty:
            continue

        score = 0
        detected_date: str | None = None
        detected_target: str | None = None
        detection_error: str | None = None

        # -------------------------------------------------
        # Basic table structure
        # -------------------------------------------------

        if len(dataframe.columns) >= 2:
            score += 10

        if len(dataframe) >= 5:
            score += 10

        # -------------------------------------------------
        # Date detection
        # -------------------------------------------------

        try:
            detected_date = _detect_date_column(
                dataframe
            )
            score += 40
        except ValueError as exc:
            detection_error = str(exc)

        # -------------------------------------------------
        # Target detection
        # -------------------------------------------------

        if detected_date:

            try:
                detected_target = _detect_target_column(
                    dataframe,
                    detected_date,
                )
                score += 40
            except ValueError as exc:
                detection_error = str(exc)

        inspections.append(
            {
                "sheet_name": str(sheet),
                "dataframe": dataframe,
                "rows": int(len(dataframe)),
                "columns": int(len(dataframe.columns)),
                "detected_date": detected_date,
                "detected_target": detected_target,
                "score": score,
                "error": detection_error,
            }
        )

    return inspections


def _load_excel_dataset(
    file_path: Path,
    requested_sheet_name: str | None,
) -> tuple[pd.DataFrame, str]:
    """
    Load an Excel dataset.

    If the user specifies a worksheet, that worksheet is used.

    Otherwise MUGONEXT inspects all worksheets and selects the
    highest-scoring worksheet that contains both a date and a
    business-value column.
    """

    try:
        excel_file = pd.ExcelFile(file_path)
    except Exception as exc:
        raise ValueError(
            f"Unable to open Excel workbook: {exc}"
        ) from exc

    # =====================================================
    # USER-SPECIFIED SHEET
    # =====================================================

    if requested_sheet_name:

        if requested_sheet_name not in excel_file.sheet_names:
            raise ValueError(
                f"The specified worksheet "
                f"'{requested_sheet_name}' was not found. "
                f"Available worksheets: "
                f"{', '.join(excel_file.sheet_names)}."
            )

        try:
            dataframe = pd.read_excel(
                file_path,
                sheet_name=requested_sheet_name,
            )
        except Exception as exc:
            raise ValueError(
                f"Failed to read worksheet "
                f"'{requested_sheet_name}': {exc}"
            ) from exc

        dataframe = dataframe.dropna(
            how="all"
        )

        return (
            dataframe,
            requested_sheet_name,
        )

    # =====================================================
    # AUTOMATIC SHEET SELECTION
    # =====================================================

    inspections = _inspect_excel_sheets(
        file_path
    )

    if not inspections:
        raise ValueError(
            "The Excel workbook does not contain "
            "any readable worksheets with data."
        )

    valid_candidates = [
        inspection
        for inspection in inspections
        if (
            inspection["detected_date"]
            and inspection["detected_target"]
        )
    ]

    if not valid_candidates:

        available_sheets = ", ".join(
            inspection["sheet_name"]
            for inspection in inspections
        )

        raise ValueError(
            "MUGONEXT inspected all worksheets but could "
            "not find a sheet containing both a recognizable "
            "date column and a business-value column. "
            f"Worksheets inspected: {available_sheets}. "
            "Please upload a raw business-data sheet or "
            "specify the correct worksheet."
        )

    # Highest score first.
    valid_candidates.sort(
        key=lambda item: (
            item["score"],
            item["rows"],
            item["columns"],
        ),
        reverse=True,
    )

    selected = valid_candidates[0]

    return (
        selected["dataframe"],
        selected["sheet_name"],
    )


# =========================================================
# LOAD DATASET
# =========================================================

def _load_dataset(
    file_path: Path,
    file_type: FileType,
    sheet_name: str | None,
) -> tuple[pd.DataFrame, str | None]:
    """
    Central dataset loader.

    CSV:
        Uses the existing DatasetLoader.

    XLSX/XLS:
        Uses MUGONEXT's multi-sheet intelligence.
    """

    # =====================================================
    # EXCEL
    # =====================================================

    if file_type in {
        FileType.XLSX,
        FileType.XLS,
    }:

        dataframe, selected_sheet = _load_excel_dataset(
            file_path,
            sheet_name,
        )

        return (
            dataframe,
            selected_sheet,
        )

    # =====================================================
    # CSV
    # =====================================================

    loader = DatasetLoader()

    try:
        dataframe = loader.load(
            file_path
        )
    except FileNotFoundError as exc:
        raise ValueError(
            str(exc)
        ) from exc
    except Exception as exc:
        raise ValueError(
            f"Failed to read the uploaded dataset: {exc}"
        ) from exc

    return (
        dataframe,
        None,
    )


# =========================================================
# REAL FILE UPLOAD
# =========================================================

@router.post(
    "/file",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_dataset_file(
    file: UploadFile = File(...),
    dataset_name: str = Form(...),
    target_column: str | None = Form(
        default=None
    ),
    date_column: str | None = Form(
        default=None
    ),
    description: str | None = Form(
        default=None
    ),
    sheet_name: str | None = Form(
        default=None
    ),
    delimiter: str | None = Form(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_analyst
    ),
):

    # =====================================================
    # FILE EXTENSION
    # =====================================================

    extension, file_type = _get_file_extension(
        file.filename
    )

    # =====================================================
    # STORAGE DIRECTORY
    # =====================================================

    upload_directory = _get_upload_directory()

    stored_filename = _generate_stored_filename(
        extension
    )

    stored_path = (
        upload_directory
        / stored_filename
    ).resolve()

    # =====================================================
    # PATH SAFETY
    # =====================================================

    upload_directory_resolved = (
        upload_directory.resolve()
    )

    if (
        upload_directory_resolved
        not in stored_path.parents
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid upload path.",
        )

    # =====================================================
    # DUPLICATE ORIGINAL FILENAME
    # =====================================================

    existing_upload = (
        db.query(Upload)
        .filter(
            Upload.company_id
            == current_user.company_id,
            Upload.original_filename
            == file.filename,
            Upload.deleted_at.is_(None),
        )
        .first()
    )

    if existing_upload:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An active upload with the same "
                "original filename already exists."
            ),
        )

    # =====================================================
    # SAVE FILE
    # =====================================================

    hasher = hashlib.sha256()
    total_bytes = 0
    max_upload_size = settings.MAX_UPLOAD_SIZE

    try:

        with stored_path.open("wb") as destination:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total_bytes += len(chunk)

                if (
                    total_bytes
                    > max_upload_size
                ):

                    raise HTTPException(
                        status_code=(
                            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                        ),
                        detail=(
                            "Uploaded file exceeds "
                            f"the maximum allowed size "
                            f"of {max_upload_size} bytes."
                        ),
                    )

                hasher.update(chunk)
                destination.write(chunk)

    except HTTPException:

        stored_path.unlink(
            missing_ok=True
        )

        raise

    except Exception as exc:

        stored_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Failed to save uploaded file: {exc}"
            ),
        ) from exc

    finally:

        await file.close()

    # =====================================================
    # EMPTY FILE CHECK
    # =====================================================

    if total_bytes <= 0:

        stored_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    file_hash = hasher.hexdigest()

    # =====================================================
    # DUPLICATE HASH CHECK
    # =====================================================

    duplicate_hash = (
        db.query(Upload)
        .filter(
            Upload.file_hash == file_hash,
            Upload.deleted_at.is_(None),
        )
        .first()
    )

    if duplicate_hash:

        stored_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This exact dataset has already "
                "been uploaded."
            ),
        )

    # =====================================================
    # LOAD DATASET
    # =====================================================

    try:

        dataframe, selected_sheet_name = (
            _load_dataset(
                file_path=stored_path,
                file_type=file_type,
                sheet_name=sheet_name,
            )
        )

    except ValueError as exc:

        stored_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        stored_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Failed to read the uploaded dataset: {exc}"
            ),
        ) from exc

    # =====================================================
    # NORMALIZE EXCEL EMPTY ROWS
    # =====================================================

    dataframe = dataframe.dropna(
        how="all"
    )

    # =====================================================
    # AUTOMATIC COLUMN DETECTION
    # =====================================================

    try:

        target_column, date_column = (
            _detect_dataset_columns(
                dataframe=dataframe,
                target_column=target_column,
                date_column=date_column,
            )
        )

    except ValueError as exc:

        stored_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # =====================================================
    # PREPROCESS DATASET
    # =====================================================

    preprocessor = DatasetPreprocessor()

    try:

        (
            processed_dataframe,
            processing_metadata,
        ) = preprocessor.process(
            dataframe,
            target_column=target_column,
            date_column=date_column,
        )

    except ValueError as exc:

        stored_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        stored_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Dataset preprocessing failed: {exc}"
            ),
        ) from exc

    # =====================================================
    # VALIDATE DATASET
    # =====================================================

    validator = DatasetValidator()

    validation_result = validator.validate(
        dataframe=processed_dataframe,
        target_column=(
            processing_metadata[
                "target_column"
            ]
        ),
        date_column=(
            processing_metadata[
                "date_column"
            ]
        ),
    )

    # =====================================================
    # QUALITY SCORE
    # =====================================================

    quality_score = _calculate_quality_score(
        processed_dataframe
    )

    validation_passed = bool(
        validation_result[
            "validation_passed"
        ]
    )

    # =====================================================
    # STATUS
    # =====================================================

    upload_status = (
        UploadStatus.COMPLETED
        if validation_passed
        else UploadStatus.FAILED
    )

    # =====================================================
    # VALIDATION ERROR MESSAGE
    # =====================================================

    error_message: str | None = None

    if validation_result["errors"]:

        error_message = "; ".join(
            validation_result["errors"]
        )

    # =====================================================
    # COLUMN METADATA
    # =====================================================

    column_metadata: dict[str, Any] = {

        "columns": (
            processed_dataframe
            .columns
            .tolist()
        ),

        "dtypes": {
            str(column): str(dtype)
            for column, dtype
            in processed_dataframe.dtypes.items()
        },

        "detected_columns": {

            "target_column": (
                processing_metadata[
                    "target_column"
                ]
            ),

            "date_column": (
                processing_metadata[
                    "date_column"
                ]
            ),
        },

        "validation_warnings": (
            validation_result[
                "warnings"
            ]
        ),

        "processing": processing_metadata,

        "workbook": {
            "selected_sheet": (
                selected_sheet_name
            ),
            "automatic_sheet_detection": (
                file_type
                in {
                    FileType.XLSX,
                    FileType.XLS,
                }
                and sheet_name is None
            ),
        },
    }

    # =====================================================
    # CREATE DATABASE RECORD
    # =====================================================

    upload = Upload(

        # -------------------------------------------------
        # OWNERSHIP
        # -------------------------------------------------

        company_id=current_user.company_id,
        user_id=current_user.id,

        # -------------------------------------------------
        # FILE INFORMATION
        # -------------------------------------------------

        original_filename=file.filename,
        stored_filename=stored_filename,

        file_extension=file_type,

        mime_type=(
            file.content_type
            or "application/octet-stream"
        ),

        file_size=total_bytes,

        # -------------------------------------------------
        # STORAGE
        # -------------------------------------------------

        storage_path=str(
            stored_path
        ),

        storage_provider=(
            StorageProvider.LOCAL
        ),

        file_hash=file_hash,

        checksum_algorithm="sha256",

        # -------------------------------------------------
        # DATASET
        # -------------------------------------------------

        dataset_name=dataset_name,

        dataset_version=1,

        description=description,

        rows=int(
            len(processed_dataframe)
        ),

        columns=int(
            len(processed_dataframe.columns)
        ),

        column_metadata=column_metadata,

        target_column=(
            processing_metadata[
                "target_column"
            ]
        ),

        date_column=(
            processing_metadata[
                "date_column"
            ]
        ),

        sheet_name=(
            selected_sheet_name
            or sheet_name
        ),

        encoding="utf-8",

        delimiter=delimiter,

        # -------------------------------------------------
        # PROCESSING
        # -------------------------------------------------

        status=upload_status,

        upload_source=(
            UploadSource.WEB
        ),

        progress=100,

        validation_passed=(
            validation_passed
        ),

        missing_values_count=int(
            validation_result[
                "missing_values_count"
            ]
        ),

        duplicate_rows_count=int(
            validation_result[
                "duplicate_rows_count"
            ]
        ),

        data_quality_score=(
            quality_score
        ),

        data_drift_detected=False,

        preview_generated=False,

        is_processed=(
            validation_passed
        ),

        is_archived=False,

        error_message=error_message,
    )

    # =====================================================
    # SAVE DATABASE RECORD
    # =====================================================

    db.add(upload)

    db.commit()

    db.refresh(upload)

    return upload


# =========================================================
# CREATE UPLOAD RECORD
# =========================================================

@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_upload(
    upload_data: UploadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_analyst
    ),
):

    existing_upload = (
        db.query(Upload)
        .filter(
            Upload.stored_filename
            == upload_data.stored_filename,

            Upload.company_id
            == current_user.company_id,

            Upload.deleted_at.is_(None),
        )
        .first()
    )

    if existing_upload:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "An upload with this stored "
                "filename already exists."
            ),
        )

    upload = Upload(
        **upload_data.model_dump(),
        company_id=current_user.company_id,
        user_id=current_user.id,
    )

    db.add(upload)

    db.commit()

    db.refresh(upload)

    return upload


# =========================================================
# LIST COMPANY UPLOADS
# =========================================================

@router.get(
    "/",
    response_model=list[UploadResponse],
)
def get_uploads(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    uploads = (
        db.query(Upload)
        .filter(
            Upload.company_id
            == current_user.company_id,

            Upload.deleted_at.is_(None),
        )
        .order_by(
            Upload.created_at.desc()
        )
        .all()
    )

    return uploads


# =========================================================
# GET SINGLE UPLOAD
# =========================================================

@router.get(
    "/{upload_id}",
    response_model=UploadResponse,
)
def get_upload(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    upload = (
        db.query(Upload)
        .filter(
            Upload.id == upload_id,

            Upload.company_id
            == current_user.company_id,

            Upload.deleted_at.is_(None),
        )
        .first()
    )

    if not upload:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found.",
        )

    return upload


# =========================================================
# UPDATE UPLOAD
# =========================================================

@router.put(
    "/{upload_id}",
    response_model=UploadResponse,
)
def update_upload(
    upload_id: int,
    upload_data: UploadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_analyst
    ),
):

    upload = (
        db.query(Upload)
        .filter(
            Upload.id == upload_id,

            Upload.company_id
            == current_user.company_id,

            Upload.deleted_at.is_(None),
        )
        .first()
    )

    if not upload:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found.",
        )

    update_data = upload_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            upload,
            field,
            value,
        )

    db.commit()

    db.refresh(upload)

    return upload


# =========================================================
# ARCHIVE / DELETE UPLOAD
# =========================================================

@router.delete(
    "/{upload_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_upload(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):

    upload = (
        db.query(Upload)
        .filter(
            Upload.id == upload_id,

            Upload.company_id
            == current_user.company_id,

            Upload.deleted_at.is_(None),
        )
        .first()
    )

    if not upload:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found.",
        )

    upload.deleted_at = (
        datetime.now(timezone.utc)
    )

    upload.is_archived = True

    db.commit()

    return None