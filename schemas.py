from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserSignUp(BaseModel):
    username: str
    password: Optional[str] = None
    fullname: Optional[str] = None


class User(BaseModel):
    username: str
    fullname: Optional[str]
    provider: Optional[str]
    register_date: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class UserStat(BaseModel):
    provider: str
    count: int
