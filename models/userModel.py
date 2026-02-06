from utils.db import Base
from sqlalchemy import Column,Integer,String,DateTime,func,Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship
from enum import Enum

import uuid

class roles(str,Enum):
    admin  = "admin"
    customer  = "customer"
    vendor  = "vendor"
    


class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True),default=uuid.uuid4,primary_key=True,index=True)
    username = Column(String,nullable=False,unique=True)
    email = Column(String,nullable=False,unique=True)
    password = Column(String, nullable=False)
    role: Mapped[roles] = mapped_column(
        SqlEnum(roles, name="role_enum"),default=roles.customer,nullable=False
    )
    products = relationship("Product",back_populates="vendor",cascade="all, delete-orphan")
    token_version: Mapped[int] =  mapped_column(default=0)
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True),onupdate=func.now(),server_default=func.now())
    


