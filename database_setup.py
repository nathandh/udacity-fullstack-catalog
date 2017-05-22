import sys, datetime, enum

from sqlalchemy import (Column, ForeignKey, Integer, String,
                        Text, DateTime, Enum, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class LoginType(enum.Enum):
    # Initial allowable login value is only "Google"
    # Can expand this enum type later (e.g. Facebook, LinkedIn, etc...)
    google = "google"

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(Text, nullable=False)
    
    created_by = Column(String, ForeignKey('user.email')) 
    created = Column(DateTime(timezone=True), server_default=func.now())
    last_update_by = Column(String, ForeignKey('user.email'))
    updated = Column(DateTime(timezone=True), server_default=func.now())

    categories = relationship("category", order_by="Category.id")
    items = relationship("Item", order_by="Item.id")

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(Text, nullable=False)
    
    created_by = Column(String, ForeignKey('user.email'))
    created = Column(DateTime(timezone=True), server_default=func.now())
    last_update_by = Column(String, ForeignKey('user.email'))
    updated = Column(DateTime(timezone=True), server_default=func.now())

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category")

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login_type = Column(Enum(LoginType))
    email = Column(String(256), nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
