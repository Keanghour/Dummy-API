# app/api/v1/models.py
from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# class Product(Base):
#     __tablename__ = 'products'
    
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     price = Column(Float)
#     description = Column(String)
#     category = Column(String)
#     image = Column(String)
#     rating = Column(JSON)  # Assuming you store rating as a JSON object




class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    color = Column(String, nullable=True)
    category = Column(String, nullable=True)
    image = Column(String, nullable=True)
    discount = Column(Float, nullable=True)
    rating = Column(JSON, nullable=True)