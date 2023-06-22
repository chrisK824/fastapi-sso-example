from fastapi import APIRouter, Depends, HTTPException
from database_crud import users_db_crud as db_crud
from schemas import UserSignUp
from sqlalchemy.orm import Session
from database import get_db
from fastapi_sso.sso.google import GoogleSSO
from starlette.requests import Request


google_sso = GoogleSSO(
    "431321506734-mi9nlucicks7dbat0a70fs94bblfls42.apps.googleusercontent.com",
    "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", 
    "http://localhost:9999/v1/google/callback",
    allow_insecure_http=True
)

router = APIRouter(prefix="/v1/google")


@router.get("/login", tags=['Google SSO'])
async def google_login():
    return await google_sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@router.get("/callback", tags=['Google SSO'])
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Process login response from Google and return user info"""

    try:
        user = await google_sso.verify_and_process(request)
        user_to_add = UserSignUp(
            email=user.email,
            fullname=user.display_name
        )
        print(user)
        user_created = db_crud.add_user(db, user_to_add, provider=user.provider)
    except db_crud.DuplicateError as e:
        raise HTTPException(status_code=403, detail=f"{e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")
    return user_created