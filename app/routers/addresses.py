from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.database import get_session
from app.db.models import Address, User
from app.dependencies.auth import get_current_user
from typing import List
from app.routers.schemas import AddressCreate, AddressResponse, AddressUpdate

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)


@router.post("/", response_model=AddressResponse)
def create_address(
        address: AddressCreate,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    new_address = Address(**address.dict(), user_id=current_user.user_id)

    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    return new_address


@router.get("/", response_model=List[AddressResponse])
def get_my_addresses(
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    addresses = db.exec(select(Address).where(Address.user_id == current_user.user_id)).all()
    return addresses


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
        address_id: int,
        address_update: AddressUpdate,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    address = db.get(Address, address_id)

    if not address or address.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Address not found")

    # Update only the provided fields
    address_data = address_update.dict(exclude_unset=True)
    for key, value in address_data.items():
        setattr(address, key, value)

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


@router.delete("/{address_id}")
def delete_address(
        address_id: int,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    address = db.get(Address, address_id)

    if not address or address.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(address)
    db.commit()
    return {"message": "Address deleted successfully"}
