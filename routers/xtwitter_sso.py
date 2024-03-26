from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from database_crud import users_db_crud as db_crud
from schemas import UserSignUp
from sqlalchemy.orm import Session
from database import get_db
from fastapi_sso.sso.twitter import TwitterSSO
from starlette.requests import Request
from authentication import create_access_token, SESSION_COOKIE_NAME
from dotenv import load_dotenv
from pathlib import Path
import os


directory_path = Path(__file__).parent
env_file_path = directory_path.parent / '.env'

load_dotenv()
XTWITTER_CLIENT_ID = os.getenv("XTWITTER_CLIENT_ID")
XTWITTER_CLIENT_SECRET = os.getenv("XTWITTER_CLIENT_SECRET")

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

xtwitter_sso = TwitterSSO(
    XTWITTER_CLIENT_ID,
    XTWITTER_CLIENT_SECRET,
    "http://localhost:9999/v1/xtwitter/callback",
    allow_insecure_http=True
)

router = APIRouter(prefix="/v1/xtwitter")


@router.get("/login", tags=['X(Twitter) SSO'])
async def xtwitter_login():
    with xtwitter_sso:
        return await xtwitter_sso.get_login_redirect()


@router.get("/callback", tags=['X(Twitter) SSO'])
async def xtwitter_callback(request: Request, db: Session = Depends(get_db)):
    """Process login response from X(Twitter) and return user info"""

    try:
        with xtwitter_sso:
            user = await xtwitter_sso.verify_and_process(request)
        username = user.email if user.email else user.display_name
        user_stored = db_crud.get_user(db, username, user.provider)
        if not user_stored:
            user_to_add = UserSignUp(
                username=username,
                fullname=user.display_name
            )
            user_stored = db_crud.add_user(
                db,
                user_to_add,
                provider=user.provider
            )
        access_token = create_access_token(
            username=user_stored.username,
            provider=user.provider
        )
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(SESSION_COOKIE_NAME, access_token)
        return response
    except db_crud.DuplicateError as e:
        raise HTTPException(status_code=403, detail=f"{e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred. Report this message to support: {e}"
        )
