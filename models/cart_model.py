from utils.db import Base
from sqlalchemy import Column,Integer,String,DateTime,func,Enum as SqlEnum,ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship
from enum import Enum
import uuid


# id user_id items



class Cart(Base):
    __tablename__ = "carts"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.user_id"),nullable=False)
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    
    
    
class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True),ForeignKey("products.product_id"),nullable=False)
    quantity: Mapped[int] =  mapped_column(default=1)
    cart_id = Column(UUID(as_uuid=True),ForeignKey("carts.id"),nullable=False)
    cart = relationship("Cart",back_populates="items")
    