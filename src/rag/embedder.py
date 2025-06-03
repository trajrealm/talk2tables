from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document


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



def create_vectorstore_from_text(text: str, persist_dir: str = "./chroma_db"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    docs = splitter.create_documents([text])
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(docs, embeddings, persist_directory=persist_dir)
    vectordb = add_info_schema(vectordb)
    return vectordb
