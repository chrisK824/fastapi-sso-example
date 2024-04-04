from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from database_crud import users_db_crud as db_crud
from schemas import UserSignUp
from sqlalchemy.orm import Session
from database import get_db
from fastapi_sso.sso.spotify import SpotifySSO
from starlette.requests import Request
from authentication import create_access_token, SESSION_COOKIE_NAME
from dotenv import load_dotenv
import os


load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


spotify_sso = SpotifySSO(
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    f"{os.getenv('HOST')}/v1/spotify/callback",
    allow_insecure_http=True
)

router = APIRouter(prefix="/v1/spotify")


@router.get("/login", tags=['Spotify SSO'])
async def spotify_login():
    with spotify_sso:
        return await spotify_sso.get_login_redirect()


@router.get("/callback", tags=['Spotify SSO'])
async def spotify_callback(request: Request, db: Session = Depends(get_db)):
    """Process login response from Spotify and return user info"""

    try:
        with spotify_sso:
            user = await spotify_sso.verify_and_process(request)
        user_stored = db_crud.get_user(db, user.email, user.provider)
        if not user_stored:
            user_to_add = UserSignUp(
                username=user.email,
                fullname=user.display_name
            )
            user_stored = db_crud.add_user(db, user_to_add, provider=user.provider)
        access_token = create_access_token(username=user_stored.username, provider=user.provider)
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(SESSION_COOKIE_NAME, access_token)
        return response
    except db_crud.DuplicateError as e:
        raise HTTPException(status_code=403, detail=f"{e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")