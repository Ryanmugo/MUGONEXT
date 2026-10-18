from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.constants import AccountStatus, UserRole


# =========================================================
# Base
# =========================================================

class UserBase(BaseModel):
    first_name: str
    last_name: str
    display_name: str | None = None

    email: EmailStr
    phone: str | None = None

    avatar_url: str | None = None
    bio: str | None = None

    language: str = "en"
    timezone: str = "UTC"

    receive_notifications: bool = True
    theme: str = "system"


# =========================================================
# Create
# =========================================================

class UserCreate(UserBase):
    password: str
    company_id: int
    role: UserRole = UserRole.VIEWER


# =========================================================
# Update
# =========================================================

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None

    email: EmailStr | None = None
    phone: str | None = None

    avatar_url: str | None = None
    bio: str | None = None

    language: str | None = None
    timezone: str | None = None

    receive_notifications: bool | None = None
    theme: str | None = None

    role: UserRole | None = None
    account_status: AccountStatus | None = None


# =========================================================
# Response
# =========================================================

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int

    role: UserRole
    account_status: AccountStatus

    profile_completed: bool

    email_verified_at: datetime | None = None
    last_login: datetime | None = None
    last_activity_at: datetime | None = None

    mfa_enabled: bool

    created_at: datetime
    updated_at: datetime