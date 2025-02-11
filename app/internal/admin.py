from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.database import get_session
from app.db.models import Admin, User
from app.dependencies.auth import hash_password, verify_password, create_access_token, get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


# Admin Login
@router.post("/login")
def login_admin(username: str, password: str, db: Session = Depends(get_session)):
    admin = db.exec(select(Admin).where(Admin.username == username)).first()
    if not admin or not verify_password(password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Create Admin (only existing admin can create new ones)
@router.post("/create")
def create_admin(username: str, password: str, db: Session = Depends(get_session), current_admin: Admin = Depends(get_current_admin, use_cache=False)):
    # Check if any admin exists
    existing_admins = db.exec(select(Admin)).all()

    # If an admin exists but the request is unauthorized, deny access
    if existing_admins and not current_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only an existing admin can create new admins")

    # Ensure the username is unique
    if db.exec(select(Admin).where(Admin.username == username)).first():
        raise HTTPException(status_code=400, detail="Admin already exists")

    # Hash password and create the new admin
    new_admin = Admin(username=username, hashed_password=hash_password(password))
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {"message": "Admin created successfully"}


# Get Current Admin Info
@router.get("/me")
def get_admin_me(current_admin: Admin = Depends(get_current_admin)):
    return current_admin


# Get all users (only admin can view)
@router.get("/users")
def get_all_users(db: Session = Depends(get_session), current_admin: Admin = Depends(get_current_admin)):
    users = db.exec(select(User)).all()
    return users
