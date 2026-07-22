from pydantic import BaseModel, Field


class AdminCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str | None = None
    password: str = Field(min_length=8, max_length=128)
    
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class AdminUpdate(BaseModel):
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    email: Optional[EmailStr] = None

    password: Optional[str] = Field(
        default=None,
        min_length=8,
    )

    is_active: Optional[bool] = None


class AdminOut(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    role: str
    is_active: bool

    model_config = {
        "from_attributes": True,
    }