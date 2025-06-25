from config.config import VECTORSTORE_DIR

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from src.utils.schema_json_util import load_schema_json, flatten_table

from sqlalchemy.orm import Session
from src.data_access.models import User, UserDatabase, UserDbSchema

from config.config import SCHEMA_JSON_DIR
import json
import os
import shutil

def add_info_schema(vectordb):
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

def get_schema_documents() -> list[Document]:
    docs = []
    for file in os.listdir(SCHEMA_JSON_DIR):
        if file.endswith(".json"):
            schema = load_schema_json(os.path.join(SCHEMA_JSON_DIR, file))
            for table in schema.get("tables", []):
                text = flatten_table(table)
                table_name = table['name']
                docs.append(Document(page_content=text, metadata={"id": f"table_{table_name}"}))
            break  # handle only one file for now
    return docs

def add_info_schema_docs() -> list[Document]:
    info_text = """Table: information_schema.tables
        - table_schema: name of the schema
        - table_name: name of the table

        Table: information_schema.columns
        - table_name: name of the table
        - column_name: name of the column
        - data_type: data type of the column"""    
    return [Document(page_content=info_text, metadata={"id": "info_schema"})]


def create_vectorstore_from_schema():
    docs = get_schema_documents()
    docs += add_info_schema_docs()
    
    embeddings = OpenAIEmbeddings()  # set API key via env var or manually
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR,
    )
    vectorstore.persist()
    return vectorstore


def create_vectorstore_from_text(text: str, persist_dir: str = VECTORSTORE_DIR):
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    docs = splitter.create_documents([text])
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(docs, embeddings, persist_directory=persist_dir)
    vectordb = add_info_schema(vectordb)
    return vectordb


def create_vectorstore_for_user_db(user_id: str, db_id: str, db: Session):
    docs = []

    # Query only schemas for this user and database
    schemas = (
        db.query(UserDbSchema)
        .filter(
            UserDbSchema.user_database_id == db_id
        )
        .all()
    )

    for schema_obj in schemas:
        schema = schema_obj.schema_json_info
        schema_name = schema_obj.schema_name

        for table in schema.get("tables", []):
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
    user_vectorstore_dir = os.path.join(VECTORSTORE_DIR, str(user_id), str(db_id))

    # Optional: clear previous vectorstore before rebuilding
    if os.path.exists(user_vectorstore_dir):
        shutil.rmtree(user_vectorstore_dir)

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=user_vectorstore_dir,
    )
    vectorstore.persist()
    return vectorstore