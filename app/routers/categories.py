from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.db.models import Category, Admin
from app.db.database import get_session
from app.routers.schemas import CategoryCreate, CategoryRead, CategoryBase
from app.dependencies.auth import get_current_admin

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# Route to create a new category (admin only)
@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,  # Use CategoryCreate to ensure 'name' is required
    db: Session = Depends(get_session),
    current_admin: Admin = Depends(get_current_admin)
):
    # Ensure the category name is unique
    existing_category = db.exec(select(Category).where(Category.name == category.name)).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


# Route to get all categories (public)
@router.get("/", response_model=List[CategoryRead])
def read_categories(db: Session = Depends(get_session)):
    categories = db.exec(select(Category)).all()
    return categories


# Route to get a single category by ID (public)
@router.get("/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, db: Session = Depends(get_session)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# Route to update a category (admin only)
@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category_update: CategoryBase,  # Use CategoryBase for updates
    db: Session = Depends(get_session),
    current_admin: Admin = Depends(get_current_admin)
):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Update only the provided fields
    category_data = category_update.dict(exclude_unset=True)
    for key, value in category_data.items():
        setattr(category, key, value)

    # Ensure the new name is unique if it's being updated
    if "name" in category_data:
        existing_category = db.exec(select(Category).where(Category.name == category.name, Category.category_id != category_id)).first()
        if existing_category:
            raise HTTPException(status_code=400, detail="Category name already exists")

    db.add(category)
    db.commit()
    db.refresh(category)
    return category