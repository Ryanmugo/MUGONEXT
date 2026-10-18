from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class CompanyCreate(BaseModel):
    name: str
    slug: str
    email: EmailStr
    country: str
    legal_name: str | None = None
    description: str | None = None
    logo_url: str | None = None
    phone: str | None = None
    website: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    email: EmailStr | None = None
    country: str | None = None
    legal_name: str | None = None
    description: str | None = None
    logo_url: str | None = None
    phone: str | None = None
    website: str | None = None


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    email: str
    country: str
    legal_name: str | None = None
    description: str | None = None
    logo_url: str | None = None
    phone: str | None = None
    website: str | None = None
    timezone: str
    currency: str
    language: str
    created_at: datetime
    updated_at: datetime