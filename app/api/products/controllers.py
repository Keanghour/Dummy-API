# app/api/products/controllers.py

from sqlalchemy.orm import Session
from app.api.products.models import Product
from app.api.products.schemas import ProductCreate, ProductResponse, ProductCreates_Optional
from app.utils.encryption import encrypt_data
from fastapi import HTTPException
import json

from cryptography.fernet import Fernet
from app.core.config import settings

from typing import List

SECRET_KEY = settings.ENCRYPTION_KEY
fernet = Fernet(SECRET_KEY)


def create_products_Optional(product: ProductCreates_Optional, db: Session) -> str:
    try:
        # Create a new product with the provided optional fields
        db_product = Product(
            title=product.title,
            price=product.price,
            description=product.description,
            brand=product.brand,
            model=product.model,
            color=product.color,
            category=product.category,
            image=product.image,
            discount=product.discount,
            rating=product.rating  # Assuming this field can be JSON
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        # Convert to response schema and encrypt
        response_data = ProductResponse.from_orm(db_product).dict()
        encrypted_data = encrypt_data(json.dumps(response_data))

        return encrypted_data
    except Exception as e:
        db.rollback()
        raise

def create_product(product: ProductCreate, db: Session) -> str:
    try:
        # Convert the Rating object to a dictionary
        rating_dict = {
            "rate": product.rating['rate'],
            "count": product.rating['count']
        }

        # Create a new product with rating as JSON
        db_product = Product(
            title=product.title,
            price=product.price,
            description=product.description,
            category=product.category,
            image=product.image,
            rating=rating_dict  # Assign dictionary directly
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        # Convert to response schema and encrypt
        response_data = ProductResponse.from_orm(db_product).dict()
        encrypted_data = encrypt_data(json.dumps(response_data))

        return encrypted_data
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred during product creation")

def update_product(product_id: int, product_data: ProductCreate, db: Session) -> ProductResponse:
    try:
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Update fields
        db_product.title = product_data.title
        db_product.price = product_data.price
        db_product.description = product_data.description
        db_product.category = product_data.category
        db_product.image = product_data.image
        db_product.rating = {
            "rate": product_data.rating['rate'],
            "count": product_data.rating['count']
        }
        
        db.commit()
        db.refresh(db_product)
        return ProductResponse.from_orm(db_product)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred during product update")

def delete_product(product_id: int, db: Session) -> None:
    try:
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        db.delete(db_product)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred during product deletion")

def get_all_products(db: Session) -> list:
    try:
        products = db.query(Product).all()
        return [ProductResponse.from_orm(p) for p in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while retrieving products")

def decrypt_data(encrypted_text: str) -> str:
    try:
        decrypted_data = fernet.decrypt(encrypted_text.encode()).decode()
        return decrypted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption error: {str(e)}")

def get_product_by_id(product_id: int, db: Session) -> ProductResponse:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise Exception("Product not found")
    return ProductResponse.from_orm(product)

def get_all_products(db: Session, limit: int, offset: int) -> List[Product]:
    try:
        print(f"Fetching products with limit={limit} and offset={offset}")
        products = db.query(Product).offset(offset).limit(limit).all()
        print(f"Retrieved {len(products)} products")
        return products
    except Exception as e:
        print(f"Error: {str(e)}")  # Print the error for debugging
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving products: {str(e)}")



