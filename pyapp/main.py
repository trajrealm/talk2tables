from fastapi import FastAPI
from src.core.app import create_app
from src.api import auth, query, databases

app = create_app()

app.include_router(auth.router)
app.include_router(query.router)
app.include_router(databases.router)
