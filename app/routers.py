from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .dependencies import get_db, get_current_user
from .security import hash_password, verify_password, create_token

router = APIRouter()

# -------- AUTH --------

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(user.password)
    db_user = models.User(email=user.email, password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    return db_user


@router.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"sub": db_user.email})
    return {"token": token}


# -------- WALLET --------

@router.post("/wallet/deposit")
def deposit(amount: float, currency: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if currency == "PEN":
        user.wallet_pen += amount
    else:
        user.wallet_usd += amount
    db.commit()
    return user


# -------- OFFERS --------

@router.post("/offers")
def create_offer(offer: schemas.OfferCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_offer = models.Offer(**offer.dict(), owner_id=user.id)
    db.add(db_offer)
    db.commit()
    return db_offer


@router.get("/offers")
def list_offers(db: Session = Depends(get_db)):
    return db.query(models.Offer).all()


# -------- ORDERS --------

@router.post("/orders")
def create_order(order: schemas.OrderCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    offer = db.query(models.Offer).get(order.offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found")

    db_order = models.Order(offer_id=offer.id, buyer_id=user.id)
    db.add(db_order)
    db.commit()
    return db_order


@router.patch("/orders/{order_id}/accept")
def accept(order_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    if order.offer.owner_id != user.id:
        raise HTTPException(403, "Not owner")
    order.status = "accepted"
    db.commit()
    return order


@router.patch("/orders/{order_id}/paid")
def paid(order_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    if order.buyer_id != user.id:
        raise HTTPException(403)
    order.status = "paid"
    db.commit()
    return order


@router.patch("/orders/{order_id}/release")
def release(order_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)

    if order.offer.owner_id != user.id:
        raise HTTPException(403)

    order.status = "released"

    # ledger simple
    order.offer.owner.wallet_usd -= order.offer.amount
    order.buyer.wallet_usd += order.offer.amount

    db.commit()
    return order
