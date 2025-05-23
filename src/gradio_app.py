import gradio as gr
import json
from rag.schema_loader import load_schema_json, flatten_schema, load_schema_with_tags
from rag.embedder import create_vectorstore_from_text, create_vectorstore_from_docs
from rag.retriever_chain import get_qa_chain
from rag.query_runner import run_query
from rag.load_api_key import load_api_key
from sql_validator import validate_sql_against_schema


def chat_with_sql_bot(message, history):
    load_api_key()
    schema = load_schema_json("public_schema.json")
    flat_text = flatten_schema(schema)
    # docs = load_schema_with_tags(schema)
    vectordb = create_vectorstore_from_text(flat_text)
    # vectordb = create_vectorstore_from_docs(docs)
    chain = get_qa_chain(vectordb)

    generated_sql = run_query(chain, message)

    print("Generated SQL:\n", generated_sql["result"])
    # validation = validate_sql_against_schema(generated_sql, schema)

 
    # valid = validation["is_valid"]
    # invalid_parts = validation["invalid_tables_or_columns"]

    # # Feedback
    # if valid:
    #     feedback = "✅ SQL is valid and conforms to schema."
    # else:
    #     feedback = f"❌ SQL contains invalid references: {', '.join(invalid_parts)}"

    return f"**Assistant:**\n```sql\n{generated_sql['result']}\n```"

if __name__ == "__main__":
    chat_ui = gr.ChatInterface(
        fn=chat_with_sql_bot,
        title="Talk2Tables: SQL Assistant",
        chatbot=gr.Chatbot(height=300),
        textbox=gr.Textbox(placeholder="Ask a question in natural language...", lines=1),
        theme="default"
    )

    chat_ui.launch()