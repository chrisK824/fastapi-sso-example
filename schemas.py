from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserSignUp(BaseModel):
    email: EmailStr
    password: Optional[str]
    name: str
    surname: Optional[str] = None


class User(BaseModel):
    email: EmailStr
    name: str
    surname: Optional[str]
    provider: Optional[str]
    register_date: Optional[datetime]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

