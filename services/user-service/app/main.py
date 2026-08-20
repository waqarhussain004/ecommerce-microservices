from fastapi import FastAPI
from app.api.routes.users import router as users_router
from app.db.base import Base
from app.db.session import engine
from app.db.models import user
from app.api.routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://127.0.0.1:8001", "http://127.0.0.1:8002", "http://127.0.0.1:8003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

@app.get("/")
def health_check():
    return {
        "service": "user-service",
        "status": "running"
    }