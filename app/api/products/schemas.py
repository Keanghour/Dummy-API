# app/api/products/schemas.py

from pydantic import BaseModel
from typing import Dict

class Rating(BaseModel):
    rate: float
    count: int

class ProductCreate(BaseModel):
    title: str
    price: float
    description: str
    category: str
    image: str
    rating: Dict[str, float]  # Use Dict for JSON compatibility

class ProductResponse(BaseModel):
    id: int
    title: str
    price: float
    description: str
    category: str
    image: str
    rating: Rating

    class Config:
        orm_mode = True
        from_attributes = True  # Add this line


class DecryptRequest(BaseModel):
    encrypted_text: str