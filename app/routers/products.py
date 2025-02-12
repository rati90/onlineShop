from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from app.db.models import Product, Category, Admin
from app.db.database import get_session
from app.routers.schemas import ProductCreate, ProductRead, ProductBase
from app.dependencies.auth import get_current_admin

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# Route to create a new product (admin only)
@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_session),
    current_admin: Admin = Depends(get_current_admin)
):
    # Check if the category exists
    category = db.exec(select(Category).where(Category.category_id == product.category_id)).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# Route to get all products (public)
@router.get("/", response_model=List[ProductRead])
def read_products(category_id: Optional[str] = None, db: Session = Depends(get_session)):
    query = select(Product)
    if category_id:
        query = query.join(Category).where(Category.category_id == category_id)

    products = db.exec(query).all()
    return products


# Route to get a single product by ID (public)
@router.get("/{product_id}", response_model=ProductRead)
def read_product(product_id: int, db: Session = Depends(get_session)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product_update: ProductBase,  # Use ProductBase for updates
    db: Session = Depends(get_session),
    current_admin: Admin = Depends(get_current_admin)
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update only the provided fields
    product_data = product_update.dict(exclude_unset=True)
    for key, value in product_data.items():
        setattr(product, key, value)

    # Check if the category exists if it's being updated
    if "category_id" in product_data:
        category = db.exec(select(Category).where(Category.category_id == product.category_id)).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")

    db.add(product)
    db.commit()
    db.refresh(product)
    return product
