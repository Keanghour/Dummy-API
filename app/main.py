# app/main.py

from fastapi import FastAPI
from app.db.database import init_db
from app.api.v1.routers import router as v1_router
from app.api.products.routers import p_router as products_router

from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize database
init_db()

# Include routers
app.include_router(v1_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
