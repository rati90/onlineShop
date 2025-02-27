from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.db.models import User, Admin
from app.db.database import get_session
import os

# Secret key for JWT token generation (change this in production)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# OAuth2 scheme definition for token authentication
oauth2_scheme_user = OAuth2PasswordBearer(
    tokenUrl="auth/user/login",
    scheme_name="UserAuth",        # <-- important
)

oauth2_scheme_admin = OAuth2PasswordBearer(
    tokenUrl="auth/admin/login",
    scheme_name="AdminAuth",       # <-- important
)

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if a provided password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticates a user by verifying their username and password.

    Returns the user object if authentication is successful, otherwise None.
    """
    user = db.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def authenticate_admin(db: Session, username: str, password: str):
    """
    Authenticates a user by verifying their username and password.

    Returns the admin object if authentication is successful, otherwise None.
    """
    admin = db.exec(select(Admin).where(Admin.username == username)).first()
    if not admin or not verify_password(password, admin.hashed_password):
        return None
    return admin


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Creates a JWT access token with expiration.

    Args:
        data: A dictionary containing user information (e.g., {"sub": username}).
        expires_delta: Optional expiration time for the token.

    Returns:
        A JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme_user), db: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(token: str = Depends(oauth2_scheme_admin), db: Session = Depends(get_session)) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    admin = db.exec(select(Admin).where(Admin.username == username)).first()
    if admin is None:
        raise credentials_exception
    return admin
