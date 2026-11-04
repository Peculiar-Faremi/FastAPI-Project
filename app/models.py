from .database import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, text, ForeignKey
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    inventory = Column(Integer, nullable=True, default=0)
    review= Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    is_ordered = Column(Boolean, nullable=True,index=True, default=False)
    ordered_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user_id= Column (Integer, ForeignKey("users.id", ondelete= "CASCADE"), nullable=False)
    owner= relationship("User")
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    