from utils.db import Base
from sqlalchemy import Column,Integer,String,DateTime,func,Enum as SqlEnum,ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship
from enum import Enum
import uuid




class Product(Base):
    __tablename__ = "products"
    product_id = Column(UUID(as_uuid=True), default=uuid.uuid4,nullable=False,primary_key=True,index=True)
    name = Column(String,nullable=False,index=True)
    price = Column(DECIMAL,nullable=False)
    description = Column(String,nullable=True)
    available_units:Mapped[int] =  mapped_column(default=1,nullable=False)
    vendor_id = Column(UUID(as_uuid=True),
                       ForeignKey("users.user_id"),
                       nullable=False)
    vendor = relationship("User",back_populates="products")