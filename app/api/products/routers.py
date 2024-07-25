# app/api/products/routers.py
from fastapi import APIRouter, HTTPException, Depends, Body, Header, Path
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import PlainTextResponse
import json

from .schemas import ProductCreate, ProductResponse
from app.db.database import get_db
from app.utils.security import get_current_active_user
from app.api.products.controllers import create_product, get_all_products, decrypt_data, update_product, delete_product
from app.core.config import settings

p_router = APIRouter()

@p_router.post("/products", response_class=PlainTextResponse)
async def create_product_route(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_active_user)
):
    try:
        encrypted_data = create_product(product, db)
        return PlainTextResponse(content=encrypted_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during product creation")

@p_router.get("/products", response_model=List[ProductResponse])
def get_products_route(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_active_user)
):
    try:
        products = get_all_products(db)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while retrieving products")

@p_router.post("/decrypt", response_class=PlainTextResponse)
def decrypt_product(
    encrypted_text: str = Body(..., description="The encrypted text to decrypt"),
    secret_key: str = Header(..., alias="Key", description="The secret key used for decryption")
):
    try:
        if secret_key != settings.ENCRYPTION_KEY:
            raise HTTPException(status_code=403, detail="Invalid secret key")

        decrypted_data = decrypt_data(encrypted_text)
        
        return PlainTextResponse(content=decrypted_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Decrypted data is not valid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption error: {str(e)}")

@p_router.put("/products/{product_id}", response_model=ProductResponse)
def update_product_route(
    product_id: int = Path(..., description="The ID of the product to update"),
    product: ProductCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_active_user)
):
    try:
        return update_product(product_id, product, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during product update")

@p_router.delete("/products/{product_id}", response_class=PlainTextResponse)
def delete_product_route(
    product_id: int = Path(..., description="The ID of the product to delete"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_active_user)
):
    try:
        delete_product(product_id, db)
        return PlainTextResponse(content="Product successfully deleted")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during product deletion")