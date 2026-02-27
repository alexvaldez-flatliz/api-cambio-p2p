from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)

    wallet_pen = Column(Float, default=0)
    wallet_usd = Column(Float, default=0)

    offers = relationship("Offer", back_populates="owner")
    orders = relationship("Order", back_populates="buyer")


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True)
    type = Column(String)  # buy or sell
    amount = Column(Float)
    price = Column(Float)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="offers")

    orders = relationship("Order", back_populates="offer")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    status = Column(String, default="pending")

    offer_id = Column(Integer, ForeignKey("offers.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"))

    offer = relationship("Offer", back_populates="orders")
    buyer = relationship("User", back_populates="orders")