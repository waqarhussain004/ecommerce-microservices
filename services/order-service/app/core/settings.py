from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    PRODUCT_SERVICE_URL: str
    SERVICE_SECRET: str

    class Config:
        env_file = ".env"


settings = Settings()

DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
PRODUCT_SERVICE_URL = settings.PRODUCT_SERVICE_URL
SERVICE_SECRET = settings.SERVICE_SECRET