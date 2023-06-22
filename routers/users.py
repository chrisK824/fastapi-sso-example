from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from authentication import create_access_token, authenticate_user
from database import get_db
from database_crud import users_db_crud as db_crud
from schemas import User, UserSignUp, Token



router = APIRouter(prefix="/v1")


@router.post("/sign_up", response_model=User, summary="Register a user", tags=["Users"])
def create_user(user_signup: UserSignUp, db: Session = Depends(get_db)):
    """
    Registers a user.
    """
    try:
        user_created = db_crud.add_user(db, user_signup)
        return user_created
    except db_crud.DuplicateError as e:
        raise HTTPException(status_code=403, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")


@router.get("/users", response_model=List[User], summary="Get all users", tags=["Users"])
def get_users(db: Session = Depends(get_db)):
    """
    Returns all users.
    """
    try:
        users = db_crud.get_users(db)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")


@router.post("/token", response_model=Token, summary="Authorize as a user", tags=["Users"])
def authorize(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Logs in a user.
    """
    user = authenticate_user(db=db, user_email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid user email or password.")
    try:
        access_token = create_access_token(data=user.email)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")
