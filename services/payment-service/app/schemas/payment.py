from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentCreate(BaseModel):
    order_id: int


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    amount: float
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )