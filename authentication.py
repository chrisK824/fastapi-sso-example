from passlib.context import CryptContext
from jose import JWTError, jwt
from jose.constants import ALGORITHMS
from fastapi.security import OAuth2PasswordBearer, APIKeyCookie
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db_models import User
from database import get_db
from pathlib import Path
from dotenv import load_dotenv
import os

directory_path = Path(__file__).parent
env_file_path = directory_path / '.env'

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME")
COOKIE = APIKeyCookie(name=SESSION_COOKIE_NAME, auto_error=False)


class BearAuthException(Exception):
    pass


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: str):
    to_encode = {"sub": data}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHMS.HS256)
    return encoded_jwt


def get_token_payload(session_token: str):
    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHMS.HS256])
        payload_sub: str = payload.get("sub")
        if payload_sub is None:
            raise BearAuthException("Token could not be validated")
        return payload_sub
    except JWTError as e:
        raise BearAuthException("Token could not be validated")


def authenticate_user(db: Session, user_email: str, password: str):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_current_user(db: Session = Depends(get_db), session_token: str = Depends(COOKIE)):
    try:
        if not session_token:
            return None
        user_email = get_token_payload(session_token)
    except BearAuthException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized, could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user
