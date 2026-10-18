import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.can_login:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account cannot log in.",
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "company_id": user.company_id,
            "role": user.role.value,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# =========================================================
# FORGOT PASSWORD
# =========================================================

@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    # Do not reveal whether an email exists.
    if not user:
        return {
            "message": (
                "If an account exists for this email, "
                "a password reset request has been created."
            ),
            "reset_token": None,
        }

    # Generate a cryptographically secure token.
    reset_token = secrets.token_urlsafe(48)

    user.password_reset_token = reset_token
    user.password_reset_expires_at = (
        datetime.now(timezone.utc) + timedelta(minutes=30)
    )
    user.password_reset_required = True

    db.commit()

    # V1 development behavior:
    # Return token so the frontend can be tested locally.
    #
    # IMPORTANT:
    # In production this token should be sent through
    # an email provider instead of being returned here.
    return {
        "message": (
            "If an account exists for this email, "
            "a password reset request has been created."
        ),
        "reset_token": reset_token,
    }


# =========================================================
# RESET PASSWORD
# =========================================================

@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(
            User.password_reset_token == request.token
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    now = datetime.now(timezone.utc)

    if (
        user.password_reset_expires_at is None
        or user.password_reset_expires_at < now
    ):
        user.password_reset_token = None
        user.password_reset_expires_at = None
        user.password_reset_required = False

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    # Prevent accidentally reusing the current password.
    if verify_password(
        request.new_password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from your current password.",
        )

    # Hash the new password using the existing security system.
    user.password_hash = hash_password(
        request.new_password
    )

    user.password_changed_at = now

    # Invalidate the reset token immediately.
    user.password_reset_token = None
    user.password_reset_expires_at = None
    user.password_reset_required = False

    # Invalidate existing refresh-token sessions if your
    # refresh-token system uses this field.
    user.refresh_token_version += 1

    db.commit()

    return {
        "message": "Password reset successfully. You can now log in."
    }