"""
=========================================================
MUGONEXT
Recommendation API Routes
=========================================================

Endpoints for AI-generated business recommendations.

Author:
MUGONEXT
"""

from __future__ import annotations

from math import ceil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_user,
    get_db,
)
from app.constants import (
    RecommendationPriority,
    RecommendationStatus,
)
from app.models.forecast import Forecast
from app.schemas.recommendation import (
    RecommendationAction,
    RecommendationCreate,
    RecommendationGenerateRequest,
    RecommendationListResponse,
    RecommendationResponse,
    RecommendationUpdate,
)
from app.services.recommendations import (
    RecommendationService,
)


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


# =========================================================
# CREATE
# =========================================================

@router.post(
    "",
    response_model=RecommendationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recommendation(
    data: RecommendationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new recommendation.
    """

    recommendation = RecommendationService.create(
        db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        data=data.model_dump(
            exclude_none=True
        ),
    )

    return recommendation


# =========================================================
# GENERATE FROM FORECAST
# =========================================================

@router.post(
    "/generate",
    response_model=RecommendationResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_recommendation(
    data: RecommendationGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate a business recommendation directly
    from an existing forecast.
    """

    forecast = (
        db.query(Forecast)
        .filter(
            Forecast.id == data.forecast_id,
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
            detail="Forecast not found for your company.",
        )

    try:
        recommendation = (
            RecommendationService.generate_from_forecast(
                db=db,
                forecast=forecast,
                company_id=current_user.company_id,
                user_id=current_user.id,
            )
        )

        return recommendation

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# =========================================================
# LIST
# =========================================================

@router.get(
    "",
    response_model=RecommendationListResponse,
)
def list_recommendations(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    priority: RecommendationPriority | None = None,
    status_filter: RecommendationStatus | None = Query(
        default=None,
        alias="status",
    ),
    category: str | None = None,
    include_archived: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return recommendations belonging only to
    the authenticated user's company.
    """

    items, total = RecommendationService.list(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        priority=priority,
        status=status_filter,
        category=category,
        include_archived=include_archived,
    )

    pages = (
        ceil(total / page_size)
        if total
        else 0
    )

    return RecommendationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


# =========================================================
# GET ONE
# =========================================================

@router.get(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def get_recommendation(
    recommendation_id: int,
    include_archived: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get a single recommendation belonging to
    the authenticated user's company.
    """

    recommendation = (
        RecommendationService.get_by_id(
            db,
            recommendation_id=recommendation_id,
            company_id=current_user.company_id,
            include_archived=include_archived,
        )
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found.",
        )

    return recommendation


# =========================================================
# UPDATE
# =========================================================

@router.patch(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def update_recommendation(
    recommendation_id: int,
    data: RecommendationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update an existing recommendation.
    """

    recommendation = (
        RecommendationService.get_by_id(
            db,
            recommendation_id=recommendation_id,
            company_id=current_user.company_id,
            include_archived=True,
        )
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found.",
        )

    updated = RecommendationService.update(
        db,
        recommendation=recommendation,
        data=data.model_dump(
            exclude_none=True
        ),
    )

    return updated


# =========================================================
# ARCHIVE
# =========================================================

@router.post(
    "/{recommendation_id}/archive",
    response_model=RecommendationResponse,
)
def archive_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Archive a recommendation.
    """

    recommendation = (
        RecommendationService.get_by_id(
            db,
            recommendation_id=recommendation_id,
            company_id=current_user.company_id,
            include_archived=True,
        )
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found.",
        )

    return RecommendationService.archive(
        db,
        recommendation=recommendation,
    )


# =========================================================
# RESTORE
# =========================================================

@router.post(
    "/{recommendation_id}/restore",
    response_model=RecommendationResponse,
)
def restore_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Restore an archived recommendation.
    """

    recommendation = (
        RecommendationService.get_by_id(
            db,
            recommendation_id=recommendation_id,
            company_id=current_user.company_id,
            include_archived=True,
        )
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found.",
        )

    return RecommendationService.restore(
        db,
        recommendation=recommendation,
    )


# =========================================================
# DELETE
# =========================================================

@router.delete(
    "/{recommendation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Soft-delete a recommendation.
    """

    recommendation = (
        RecommendationService.get_by_id(
            db,
            recommendation_id=recommendation_id,
            company_id=current_user.company_id,
            include_archived=True,
        )
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found.",
        )

    RecommendationService.delete(
        db,
        recommendation=recommendation,
    )

    return None


# =========================================================
# MARK ACTIONED
# =========================================================

@router.post(
    "/{recommendation_id}/action",
    response_model=RecommendationResponse,
)
def mark_recommendation_actioned(
    recommendation_id: int,
    data: RecommendationAction,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Record whether a business acted on a recommendation.
    """

    recommendation = (
        RecommendationService.get_by_id(
            db,
            recommendation_id=recommendation_id,
            company_id=current_user.company_id,
            include_archived=True,
        )
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found.",
        )

    return RecommendationService.mark_actioned(
        db,
        recommendation=recommendation,
        action_taken=data.action_taken,
        action_notes=data.action_notes,
    )