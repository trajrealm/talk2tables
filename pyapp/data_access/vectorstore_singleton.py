from typing import Dict, Tuple, Optional
from uuid import UUID
from pyapp.data_access.vectorestore_manager import cli_run_create_vectorstore_for_user_db
from sqlalchemy.orm import Session
from pyapp.config.settings import settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import os

# Cache of vectorstores keyed by (user_id, db_id)
_vectorstore_cache: Dict[Tuple[UUID, UUID], object] = {}


def get_vectorstore(user_id: UUID, db_id: UUID) -> Optional[object]:
    """
    Retrieve vectorstore from cache for given user_id and db_id.
    Returns None if not found.
    """
    print(f"_vectorstore_cache: {_vectorstore_cache}")
    return _vectorstore_cache.get((user_id, db_id))


def set_vectorstore(user_id: UUID, db_id: UUID, vstore: object) -> None:
    """
    Store vectorstore instance in cache for given user_id and db_id.
    """
    _vectorstore_cache[(user_id, db_id)] = vstore


def get_or_create_vectorstore(user_id: UUID, db_id: UUID, db: Session) -> Chroma:
    """
    Helper to get vectorstore from cache or create and cache it if missing.
    """
    vstore = get_vectorstore(user_id, db_id)
    if vstore is None:
        persist_dir = os.path.join(settings.VECTORSTORE_DIR, str(user_id), str(db_id))
        if not os.path.exists(persist_dir):
            cli_run_create_vectorstore_for_user_db(str(user_id), str(db_id))
        
        vstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=OpenAIEmbeddings()
        )
        set_vectorstore(user_id, db_id, vstore)

    return vstore
