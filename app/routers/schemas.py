from sqlmodel import SQLModel
from pydantic import EmailStr
from typing import Optional


class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(SQLModel):
    user_id: int
    username: str
    email: EmailStr
    is_active: bool


class AddressCreate(SQLModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    country: Optional[str] = "GE"  # Default to Georgia (ISO country code)


class AddressUpdate(SQLModel):
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None  # Allows changing the country if needed


class AddressResponse(SQLModel):
    address_id: int
    user_id: int
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    country: str

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
