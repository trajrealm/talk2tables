from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.utils.load_api_key import load_api_key
from src.config.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_api_key()
    # Any startup logic here
    yield
    # Any shutdown logic here

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
