from src.utils.schema_json_util import load_schema
from src.data_access.vectorestore_manager import create_vectorstore_from_text
from src.data_access.vectorstore_singleton import set_vectorstore
from src.services.handle_query import handle_query
from src.utils.load_api_key import load_api_key
from config.config import SCHEMA_JSON_DIR

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_api_key()
    schema, schema_text = load_schema()
    vectorstore = create_vectorstore_from_text(schema_text)
    set_vectorstore(vectorstore)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can tighten this later
    allow_methods=["*"],
    allow_headers=["*"],
)

load_api_key()
class QueryRequest(BaseModel):
    query: str

@app.post("/api/query")
async def query_api(request: QueryRequest):
    return handle_query(request.query)


def get_vectorstore():
    return vectorstore