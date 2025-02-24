from sqlmodel import SQLModel
from pydantic import EmailStr
from typing import Optional, List
from datetime import datetime

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


class CategoryBase(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    name: str  # Ensure name is required for creation


class CategoryRead(SQLModel):
    category_id: int
    name: str
    description: Optional[str] = None


class ProductBase(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    name: str
    price: float
    stock: int
    category_id: int


class ProductRead(SQLModel):
    product_id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: CategoryRead


class OrderItemCreate(SQLModel):
    product_id: int
    quantity: int
    price_at_purchase: float


class OrderCreate(SQLModel):
    order_items: List[OrderItemCreate]
    total_amount: float
    status: str = "pending"
    sale_source: str = "online"


class OrderRead(SQLModel):
    order_id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime


class PaymentCreate(SQLModel):
    order_id: int
    payment_method: str
    amount: float


class PaymentRead(SQLModel):
    payment_id: int
    order_id: int
    payment_method: str
    amount: float
    status: str
    created_at: datetime







