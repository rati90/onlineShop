from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from typing import Optional, List


class Admin(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str


class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))

    orders: List["Order"] = Relationship(back_populates="user")


class Address(SQLModel, table=True):
    address_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    address_line1: str = Field(max_length=255)
    address_line2: Optional[str] = Field(default=None, max_length=255)
    city: str = Field(max_length=50)
    state: str = Field(max_length=50)
    zip_code: str = Field(max_length=20)
    country: str = Field(default="GE", max_length=50)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))


class Category(SQLModel, table=True):
    category_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))

    products: List["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    product_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: int = Field(foreign_key="category.category_id")
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))

    category: Category = Relationship(back_populates="products")


class Order(SQLModel, table=True):
    order_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    total_amount: float = Field(gt=0)
    status: str = Field(default="pending", max_length=50)
    sale_source: str = Field(default="online", max_length=10)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))

    user: Optional["User"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")
    payments: List["Payment"] = Relationship(back_populates="order")  # ⬅️ Add this


class OrderItem(SQLModel, table=True):
    order_item_id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.order_id")
    product_id: int = Field(foreign_key="product.product_id")
    quantity: int = Field(ge=1)
    price_at_purchase: float = Field(gt=0)

    order: Order = Relationship(back_populates="order_items")  # ⬅️ Add this
    product: Product = Relationship()


class Payment(SQLModel, table=True):
    payment_id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.order_id")
    payment_method: str = Field(max_length=50)
    amount: float = Field(gt=0)
    status: str = Field(default="pending", max_length=20)  # ⬅️ Change default to 'pending' for better flow
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))

    order: Order = Relationship(back_populates="payments")

