# app/api/products/schemas.py

from pydantic import BaseModel, Field
from typing import Dict

from typing import Optional

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
    image: Optional[str]
    brand: Optional[str]
    model: Optional[str] 
    color: Optional[str] 
    discount: Optional[float]
    rating: Rating

    class Config:
        orm_mode = True
        from_attributes = True  # Add this line


class DecryptRequest(BaseModel):
    encrypted_text: str




class ProductCreates_Optional(BaseModel):
    title: Optional[str] = Field(None, description="Title of the product")
    price: Optional[float] = Field(None, description="Price of the product")
    description: Optional[str] = Field(None, description="Description of the product")
    brand: Optional[str] = Field(None, description="Brand of the product")
    model: Optional[str] = Field(None, description="Model of the product")
    color: Optional[str] = Field(None, description="Color of the product")
    category: Optional[str] = Field(None, description="Category of the product")
    image: Optional[str] = Field(None, description="Image URL of the product")
    discount: Optional[float] = Field(None, description="Discount on the product")
    rating: Optional[dict] = Field(None, description="Rating of the product")

    class Config:
        schema_extra = {
            "example": {
                "title": "Sample Product",
                "price": 19.99,
                "description": "A description of the product",
                "brand": "Brand Name",
                "model": "Model XYZ",
                "color": "Red",
                "category": "Category Name",
                "image": "image_url",
                "discount": 10.0,
                "rating": {
                    "rate": 4.5,
                    "count": 150
                }
            }
        }