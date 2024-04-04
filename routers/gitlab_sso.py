from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from database_crud import users_db_crud as db_crud
from schemas import UserSignUp
from sqlalchemy.orm import Session
from database import get_db
from fastapi_sso.sso.gitlab import GitlabSSO
from starlette.requests import Request
from authentication import create_access_token, SESSION_COOKIE_NAME
from dotenv import load_dotenv
import os


load_dotenv()
GITLAB_CLIENT_ID = os.getenv("GITLAB_CLIENT_ID")
GITLAB_CLIENT_SECRET = os.getenv("GITLAB_CLIENT_SECRET")


gitlab_sso = GitlabSSO(
    GITLAB_CLIENT_ID,
    GITLAB_CLIENT_SECRET,
    f"{os.getenv('HOST')}/v1/gitlab/callback"
)

router = APIRouter(prefix="/v1/gitlab")


@router.get("/login", tags=['GitLab SSO'])
async def gitlab_login():
    with gitlab_sso:
        return await gitlab_sso.get_login_redirect()


@router.get("/callback", tags=['GitLab SSO'])
async def gitlab_callback(request: Request, db: Session = Depends(get_db)):
    """Process login response from GitLab and return user info"""

    try:
        with gitlab_sso:
            user = await gitlab_sso.verify_and_process(request)
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
