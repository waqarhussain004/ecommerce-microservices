from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(...,min_length=6)
    role: Literal["user", "admin"] = "user"
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Waqar Hussain",
                "email": "waqar@gmail.com",
                "password": "6 chr",
                "role": "user"
            }
        }
    }


class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)
    model_config = {
            "json_schema_extra": {
                "example": {
                    "name": "Waqar Hussain",
                    "email": "waqar@gmail.com",
                    "password": "6 chr",
                }
            }
        }


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True