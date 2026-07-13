from pydantic import BaseModel, Field


class AdminCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str | None = None
    password: str = Field(min_length=8, max_length=128)