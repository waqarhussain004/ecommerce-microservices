from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine
from app.db.models.order import Order, OrderItem
from app.api.routes.order import router as order_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Order Service",
    version="1.0.0"
)

app.include_router(
    order_router,
    prefix="/orders",
    tags=["Orders"]
)

@app.get("/")
def health_check():
    return {
        "service": "order-service",
        "status": "running"
    }