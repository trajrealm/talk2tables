from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID

from pyapp.data_access.database import get_db
from pyapp.services.handle_query import handle_query
from pyapp.api.auth import get_current_user

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    history: list[dict] = []
    db_id: UUID


@router.post("/api/query")
async def query_api(request: QueryRequest, db: Session = Depends(get_db), user_data=Depends(get_current_user)):
    user_id = UUID(user_data["sub"])
    return handle_query(request.query, history=request.history, db_id=request.db_id, user_id=user_id, db=db)
