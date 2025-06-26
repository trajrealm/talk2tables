from fastapi import FastAPI
from pyapp.core.app import create_app
from pyapp.api import auth, query, databases

app = create_app()

app.include_router(auth.router)
app.include_router(query.router)
app.include_router(databases.router)
