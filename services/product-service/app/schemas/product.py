from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., max_length=500)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=150)
    description: str | None = Field(None, max_length=500)
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

    model_config = {
        "from_attributes": True
    }

class StockUpdate(BaseModel):
    quantity: int = Field(..., gt=0)