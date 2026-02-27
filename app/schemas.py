from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str


class OfferCreate(BaseModel):
    type: str
    amount: float
    price: float


class OrderCreate(BaseModel):
    offer_id: int