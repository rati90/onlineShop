from sqlmodel import SQLModel
from pydantic import EmailStr

class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(SQLModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
