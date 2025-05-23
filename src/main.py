from rag.schema_loader import load_schema_json, flatten_schema, load_schema_with_tags
from rag.embedder import create_vectorstore_from_text, create_vectorstore_from_docs
from rag.retriever_chain import get_qa_chain
from rag.query_runner import run_query
from rag.load_api_key import load_api_key
from sql_validator import validate_sql_against_schema
import json

def main():
    load_api_key()
    schema = load_schema_json("public_schema.json")
    flat_text = flatten_schema(schema)
    # docs = load_schema_with_tags(schema)
    vectordb = create_vectorstore_from_text(flat_text)
    # vectordb = create_vectorstore_from_docs(docs)
    chain = get_qa_chain(vectordb)

    question = "How many distinct securities are there in tm1 for which scores are available?"
    result = run_query(chain, question)

    print("Generated SQL:\n", result["result"])

    validation = validate_sql_against_schema(result["result"], json.load(open("public_schema.json")))
    if not validation["is_valid"]:
        print("⚠️ Invalid SQL! Check:", validation["invalid_tables_or_columns"])

if __name__ == "__main__":
    main()
