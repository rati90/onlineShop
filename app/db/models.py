from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func
from typing import Optional


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