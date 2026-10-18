from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.company import Company
from app.schemas.company import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
)
from app.api.dependencies.auth import (
    get_current_user,
    require_owner,
)

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new company.

    This endpoint remains unauthenticated because company
    creation may be part of the registration/onboarding flow.
    """

    existing_company = (
        db.query(Company)
        .filter(
            Company.slug == company_data.slug
        )
        .first()
    )

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company slug already exists.",
        )

    company = Company(
        **company_data.model_dump()
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


@router.get(
    "/",
    response_model=list[CompanyResponse],
)
def get_companies(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return only the company belonging to the
    authenticated user.

    Prevents users from discovering other tenants.
    """

    company = (
        db.query(Company)
        .filter(
            Company.id == current_user.company_id
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    return [company]


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
def get_company(
    company_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a company only if it belongs to
    the authenticated user's tenant.
    """

    company = (
        db.query(Company)
        .filter(
            Company.id == company_id,
            Company.id == current_user.company_id,
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    return company


@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
)
def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user=Depends(require_owner),
    db: Session = Depends(get_db),
):
    """
    Update the authenticated user's own company.

    Owner access is required.
    Cross-company updates are blocked.
    """

    company = (
        db.query(Company)
        .filter(
            Company.id == company_id,
            Company.id == current_user.company_id,
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    update_data = company_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return company


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_company(
    company_id: int,
    current_user=Depends(require_owner),
    db: Session = Depends(get_db),
):
    """
    Delete the authenticated user's own company.

    Owner access is required.

    Cross-company deletion is blocked.
    """

    company = (
        db.query(Company)
        .filter(
            Company.id == company_id,
            Company.id == current_user.company_id,
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    db.delete(company)
    db.commit()

    return None