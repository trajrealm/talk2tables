from config.config import VECTORSTORE_DIR

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from src.utils.schema_json_util import load_schema_json, flatten_table

from config.config import SCHEMA_JSON_DIR
import json
import os


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
