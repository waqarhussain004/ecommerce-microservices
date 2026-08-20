from fastapi import FastAPI

from app.api.routes.products import router as products_router
from app.db.base import Base
from app.db.session import engine
from app.db.models import product


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Product Service",
    version="1.0.0"
)


app.include_router(
    products_router,
    prefix="/products",
    tags=["Products"]
)


@app.get("/")
def health_check():
    return {
        "service": "product-service",
        "status": "running"
    }