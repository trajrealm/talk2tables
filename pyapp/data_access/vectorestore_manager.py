
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from sqlalchemy.orm import Session
from pyapp.data_access.models import UserDbSchema
from pyapp.data_access.database import get_db
from pyapp.utils.schema_json_util import load_schema_json, flatten_table
from pyapp.config.settings import settings

import os
import subprocess
import sys
import shutil
import argparse
from typing import List
from uuid import UUID



def add_info_schema(vectordb: Chroma) -> Chroma:
    """
    Adds general info schema document about information_schema.tables and columns.
    """
    info_schema_doc = Document(
        page_content="""
        Table: information_schema.tables
        - table_schema: name of the schema
        - table_name: name of the table

        Table: information_schema.columns
        - table_name: name of the table
        - column_name: name of the column
        - data_type: data type of the column
        """
    )
    vectordb.add_documents([info_schema_doc])
    return vectordb


def get_schema_documents() -> List[Document]:
    """
    Loads documents from the first JSON schema file in SCHEMA_JSON_DIR.
    """
    docs = []
    for file in os.listdir(settings.SCHEMA_JSON_DIR):
        if file.endswith(".json"):
            schema = load_schema_json(os.path.join(settings.SCHEMA_JSON_DIR, file))
            for table in schema.get("tables", []):
                text = flatten_table(table)
                table_name = table.get('name', 'unknown_table')
                docs.append(Document(page_content=text, metadata={"id": f"table_{table_name}"}))
            break  # Only process the first JSON schema file
    return docs


def add_info_schema_docs() -> List[Document]:
    """
    Returns a list with the informational schema document.
    """
    info_text = """Table: information_schema.tables
        - table_schema: name of the schema
        - table_name: name of the table

        Table: information_schema.columns
        - table_name: name of the table
        - column_name: name of the column
        - data_type: data type of the column"""    
    return [Document(page_content=info_text, metadata={"id": "info_schema"})]


def create_vectorstore_from_schema() -> Chroma:
    """
    Creates and persists a vectorstore from a schema JSON file and info schema docs.
    """
    docs = get_schema_documents()
    docs += add_info_schema_docs()
    
    embeddings = OpenAIEmbeddings()  # API key should be set in environment or config
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=settings.VECTORSTORE_DIR,
    )
    vectorstore.persist()
    return vectorstore


def create_vectorstore_from_text(text: str, persist_dir: str = settings.VECTORSTORE_DIR) -> Chroma:
    """
    Creates a vectorstore from a given text, splitting into chunks first.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    docs = splitter.create_documents([text])
    
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(docs, embeddings, persist_directory=persist_dir)
    vectordb = add_info_schema(vectordb)
    
    return vectordb


def create_vectorstore_for_user_db(user_id: str, db_id: str, db: Session) -> Chroma:
    """
    Creates and persists a vectorstore for a given user's database.
    Reads all schemas for the user's database, flattens tables to documents.
    Clears existing persisted vectorstore for this user-db before recreating.
    """
    docs: List[Document] = []

    # Query all schemas for the user database
    schemas = (
        db.query(UserDbSchema)
        .filter(UserDbSchema.user_database_id == db_id)
        .all()
    )

    for schema_obj in schemas:
        print(f"schema_obj: {schema_obj.schema_name}")
        schema = schema_obj.schema_json_info or {}
        schema_name = schema_obj.schema_name or "unknown_schema"

        for table in schema.get("tables", []):
            # print(f"table: {table}")
            table_name = table.get("name", "unknown_table")
            text = flatten_table(table)

            docs.append(Document(
                page_content=text,
                metadata={
                    "db_id": db_id,
                    "schema_name": schema_name,
                    "table_name": table_name,
                }
            ))

    docs += add_info_schema_docs()

    embeddings = OpenAIEmbeddings()
    user_vectorstore_dir = os.path.join(settings.VECTORSTORE_DIR, str(user_id), str(db_id))

    # Remove existing vectorstore directory to rebuild cleanly
    if os.path.exists(user_vectorstore_dir):
        shutil.rmtree(user_vectorstore_dir)

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=user_vectorstore_dir,
    )
    vectorstore.persist()

    return vectorstore


def cli_run_create_vectorstore_for_user_db(user_id: str, db_id: str) -> None:
    # Validate UUIDs
    try:
        user_id = str(UUID(user_id))
        db_id = str(UUID(db_id))
    except ValueError:
        print("Invalid UUID format.")
        raise ValueError("Invalid UUID format.")

    # Create DB session and run
    db_gen = get_db()
    db = next(db_gen)

    try:
        cmd = [
            sys.executable,
            "-c",
            (
                "import sys, os;"
                "sys.path.insert(0, os.path.abspath('..'))  # add parent of current directory;"
                "from pyapp.data_access.vectorstore_manager import create_vectorstore_for_user_db;"
                "from pyapp.data_access.database import get_db;"
                "db = next(get_db());"
                f"create_vectorstore_for_user_db(user_id='{user_id}', db_id='{db_id}', db=db);"
                "db.close()"
            )
        ]
        cmd = subprocess.run(cmd, capture_output=True, text=True, check=True)
    finally:
        db.close()


