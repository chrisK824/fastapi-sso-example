from sqlalchemy.orm import Session
from db_models import User
import schemas as schemas
from sqlalchemy.exc import IntegrityError
from authentication import get_password_hash


class DuplicateError(Exception):
    pass


def add_user(db: Session, user: schemas.UserSignUp, provider: str = None):
    user = User(
        email=user.email,
        password=get_password_hash(user.password),
        name=user.name,
        surname=user.surname,
        provider=provider
    )
    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateError(
            f"Email {user.email} is already attached to a registered user.")
    return user


def get_users(db: Session):
    users = list(db.query(User).all())
    return users


