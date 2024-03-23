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
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "default_session_cookie_name")


COOKIE = APIKeyCookie(name=SESSION_COOKIE_NAME, auto_error=False)

class BearAuthException(Exception):
    pass


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(username: str, provider: str):
    to_encode = {
        "username": username,
        "provider": provider
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHMS.HS256)
    return encoded_jwt


def get_token_payload(session_token: str):
    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHMS.HS256])
        username: str = payload.get("username")
        provider: str = payload.get("provider")
        if username is None or provider is None:
            raise BearAuthException("Token could not be validated")
        return {
            "username": username,
            "provider": provider
        }
    except JWTError:
        raise BearAuthException("Token could not be validated")


def authenticate_user(db: Session, username: str, password: str, provider: str):
    user = db.query(User).filter(User.username == username).filter(User.provider == provider).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_current_user(db: Session = Depends(get_db), session_token: str = Depends(COOKIE)):
    try:
        if not session_token:
            return None
        userdata = get_token_payload(session_token)
        username = userdata.get('username')
        provider = userdata.get('provider')
    except BearAuthException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user = db.query(User).filter(User.username == username).filter(User.provider == provider).first()
    if not user:
        return None
    return user
