import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db_models import Base
from database import engine
from routers import users, google_sso
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os 


description = """
Example API to demonstrate SSO login in fastAPI
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title='SSO login example API',
    description=description,
    version="1.0.0",
    docs_url="/v1/documentation",
    redoc_url="/v1/redocs",
    lifespan=lifespan
)

app.add_middleware(SessionMiddleware, secret_key="!secret")
app.add_middleware(
    CORSMiddleware, 
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=["*"]
)

app.include_router(users.router)
app.include_router(google_sso.router)

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    uvicorn.run(app, host="0.0.0.0", port=9999)
