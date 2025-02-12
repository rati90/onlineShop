from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.database import get_session
from app.db.models import User
from app.routers.schemas import UserCreate, UserResponse
from passlib.context import CryptContext
from app.dependencies.auth import get_current_user, verify_password, create_access_token

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.user_id, "username": current_user.username, "email": current_user.email}


@router.post("/login")
def login_user(identifier: str, password: str, db: Session = Depends(get_session)):
    statement = select(User).where((User.username == identifier) | (User.email == identifier))
    user = db.exec(statement).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_session)):
    existing_user = db.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
