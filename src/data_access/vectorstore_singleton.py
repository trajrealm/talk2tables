
vectorstore = None

# def get_vectorstore():
#     return vectorstore

# def set_vectorstore(vstore):
#     global vectorstore
#     vectorstore = vstore

# vectorstore_singleton.py

from typing import Dict, Tuple
from uuid import UUID
from src.data_access.vectorestore_manager import create_vectorstore_for_user_db

_vectorstore_cache: Dict[Tuple[UUID, UUID], object] = {}

def get_vectorstore(user_id: UUID, db_id: UUID):
    return _vectorstore_cache.get((user_id, db_id))

def set_vectorstore(user_id: UUID, db_id: UUID, vstore: object):
    _vectorstore_cache[(user_id, db_id)] = vstore    