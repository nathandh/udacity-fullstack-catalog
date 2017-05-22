import sys, datetime

from sqlalchemy import (Column, ForeignKey, Integer, String,
                        Text, DateTime, Enum, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.schema import Table

Base = declarative_base()

class LoginType(Base):
    # Initial allowable login value is only "Google"
    # Can expand this enum type later (e.g. Facebook, LinkedIn, etc...)
    __tablename__ = 'logintype'
    id = Column(Integer, primary_key=True)
    source = Column(String(40), nullable=False)

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(Text, nullable=False)
    
    created_by = Column(String, ForeignKey('user.email')) 
    created = Column(DateTime(timezone=True), server_default=func.now())
    last_update_by = Column(String, ForeignKey('user.email'))
    updated = Column(DateTime(timezone=True), server_default=func.now())

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


user_role_association = Table('user_role_association', Base.metadata,
                              Column('user_id', Integer(), 
                              ForeignKey('user.id'),
                              primary_key=True),
                              Column('role_id', Integer(),
                              ForeignKey('role.id'),
                              primary_key=True))
                              
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(256), nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    
    roles = relationship("Role", secondary='user_role_association', 
                         order_by="Role.id")

    logintype_id = Column(Integer, ForeignKey('logintype.id'))
    logintype = relationship("LoginType")

class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    permission = Column(String(40), nullable=False)

    users = relationship("User", secondary='user_role_association',
                         order_by="User.id")

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
