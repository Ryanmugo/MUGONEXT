
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.api.dependencies.auth import (
    get_current_user,
    require_analyst,
    require_manager,
)

from app.models.forecast import Forecast
from app.models.upload import Upload
from app.models.user import User

from app.schemas.forecast import (
    ForecastCreate,
    ForecastResponse,
    ForecastUpdate,
)

from app.services.forecasting.service import ForecastService


router = APIRouter(
    prefix="/forecasts",
    tags=["Forecasts"],
)

forecast_service = ForecastService()


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# CREATE FORECAST
# =========================================================

@router.post(
    "/",
    response_model=ForecastResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_forecast(
    forecast_data: ForecastCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """
    Create a new forecast from a validated upload.

    The actual forecasting work is handled by ForecastService.
    """

    upload = (
        db.query(Upload)
        .filter(
            Upload.id == forecast_data.upload_id,
            Upload.company_id == current_user.company_id,
            Upload.deleted_at.is_(None),
        )
        .first()
    )

    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found for your company.",
        )

    try:
        forecast = forecast_service.generate_forecast(
            db=db,
            upload=upload,
            current_user=current_user,
            name=forecast_data.name,
            target_column=forecast_data.target_column,
            date_column=forecast_data.date_column,
            forecast_periods=forecast_data.forecast_periods,
            frequency=forecast_data.frequency,
            description=forecast_data.description,
            model=forecast_data.forecast_model.value,
        )

        return forecast

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# =========================================================
# LIST COMPANY FORECASTS
# =========================================================

@router.get(
    "/",
    response_model=list[ForecastResponse],
)
def get_forecasts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return active, non-archived forecasts belonging
    to the current user's company.
    """

    forecasts = (
        db.query(Forecast)
        .filter(
            Forecast.company_id == current_user.company_id,
            Forecast.deleted_at.is_(None),
            Forecast.is_archived.is_(False),
            Forecast.is_active.is_(True),
        )
        .order_by(
            Forecast.created_at.desc()
        )
        .all()
    )

    return forecasts


# =========================================================
# GET SINGLE FORECAST
# =========================================================

@router.get(
    "/{forecast_id}",
    response_model=ForecastResponse,
)
def get_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get one active forecast belonging to the current user's company.

    Archived forecasts are intentionally hidden from the normal
    GET endpoint and therefore return HTTP 404.

    The record remains in the database for historical purposes.
    """

    forecast = (
        db.query(Forecast)
        .filter(
            Forecast.id == forecast_id,
            Forecast.company_id == current_user.company_id,
            Forecast.deleted_at.is_(None),
            Forecast.is_archived.is_(False),
            Forecast.is_active.is_(True),
        )
        .first()
    )

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found.",
        )

    return forecast


# =========================================================
# UPDATE FORECAST
# =========================================================

@router.put(
    "/{forecast_id}",
    response_model=ForecastResponse,
)
def update_forecast(
    forecast_id: int,
    forecast_data: ForecastUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """
    Update an active forecast belonging to the current company.

    Archived or deleted forecasts cannot be updated.
    """

    forecast = (
        db.query(Forecast)
        .filter(
            Forecast.id == forecast_id,
            Forecast.company_id == current_user.company_id,
            Forecast.deleted_at.is_(None),
            Forecast.is_archived.is_(False),
            Forecast.is_active.is_(True),
        )
        .first()
    )

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found.",
        )

    update_data = forecast_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            forecast,
            field,
            value,
        )

    forecast.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(forecast)

    return forecast


# =========================================================
# ARCHIVE FORECAST
# =========================================================

@router.post(
    "/{forecast_id}/archive",
    response_model=ForecastResponse,
)
def archive_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """
    Archive an active forecast.

    The forecast is not deleted. Instead:
        is_archived = True
        is_active = False

    Archived forecasts are excluded from normal list/get
    operations.
    """

    forecast = (
        db.query(Forecast)
        .filter(
            Forecast.id == forecast_id,
            Forecast.company_id == current_user.company_id,
            Forecast.deleted_at.is_(None),
            Forecast.is_archived.is_(False),
            Forecast.is_active.is_(True),
        )
        .first()
    )

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found.",
        )

    forecast.is_archived = True
    forecast.is_active = False
    forecast.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(forecast)

    return forecast


# =========================================================
# UNARCHIVE FORECAST
# =========================================================

@router.post(
    "/{forecast_id}/unarchive",
    response_model=ForecastResponse,
)
def unarchive_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """
    Restore an archived forecast.

    This makes the forecast visible again through the normal
    list/get endpoints.
    """

    forecast = (
        db.query(Forecast)
        .filter(
            Forecast.id == forecast_id,
            Forecast.company_id == current_user.company_id,
            Forecast.deleted_at.is_(None),
            Forecast.is_archived.is_(True),
        )
        .first()
    )

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archived forecast not found.",
        )

    forecast.is_archived = False
    forecast.is_active = True
    forecast.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(forecast)

    return forecast


# =========================================================
# DELETE FORECAST
# =========================================================

@router.delete(
    "/{forecast_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """
    Soft-delete a forecast.

    The database record is retained.
    """

    forecast = (
        db.query(Forecast)
        .filter(
            Forecast.id == forecast_id,
            Forecast.company_id == current_user.company_id,
            Forecast.deleted_at.is_(None),
        )
        .first()
    )

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found.",
        )

    forecast.deleted_at = datetime.now(
        timezone.utc
    )

    forecast.is_active = False
    forecast.is_archived = True

    forecast.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()

    return None
