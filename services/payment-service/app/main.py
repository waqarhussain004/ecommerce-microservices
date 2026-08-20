from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine

from app.db.models.payment import Payment

from app.api.routes.payment import router as payment_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Payment Service"
)


app.include_router(
    payment_router,
    prefix="/payments",
    tags=["Payments"]
)


@app.get("/")
def root():
    return {
        "message": "Payment Service is running"
    }