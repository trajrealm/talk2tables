import gradio as gr
from rag.schema_loader import load_schema_json, flatten_schema
from rag.embedder import create_vectorstore_from_text
from rag.retriever_chain import get_qa_chain
from rag.query_runner import run_query
from rag.load_api_key import load_api_key
import re
from db_executor import execute_sql
from rag.llm_ambiguity_checker import check_ambiguity
from rag.schema_loader import flatten_schema



def strip_sql_markdown(text: str) -> str:
    # Remove ```sql or ``` block fences
    return re.sub(r"^```sql\s*|^```\s*|```$", "", text.strip(), flags=re.MULTILINE).strip()

def chat_with_sql_bot(message, history):
    load_api_key()
    schema = load_schema_json("public_schema.json")
    schema_text = flatten_schema(schema)

    ambiguity = check_ambiguity(message, schema_text)

    if ambiguity.get("ambiguous"):
        clarify_items = ambiguity.get("clarify", [])
        clarification_msg = "⚠️ Ambiguity detected in your question:\n\n"

        for item in clarify_items:
            if isinstance(item, dict):
                for term, matches in item.items():
                    clarification_msg += f"**{term}** could refer to: {', '.join(matches)}\n"
            elif isinstance(item, str):
                clarification_msg += f"- {item}\n"

        clarification_msg += "\nPlease rephrase your query or specify the exact table/column."

        return clarification_msg

    flat_text = schema_text
    vectordb = create_vectorstore_from_text(flat_text)
    chain = get_qa_chain(vectordb)
    generated_sql = run_query(chain, message)
    clean_sql = strip_sql_markdown(generated_sql["result"])

    print("Generated SQL:\n", clean_sql)

    columns, rows = execute_sql(clean_sql)

    if not columns:
        return f"**Assistant:**\n{rows[0][0]}"
    
    # Format rows into markdown table
    table_md = "| " + " | ".join(columns) + " |\n"
    table_md += "| " + " | ".join(["---"] * len(columns)) + " |\n"
    for row in rows:
        table_md += "| " + " | ".join(map(str, row)) + " |\n"
    
 
    return f"**Assistant:**\n{table_md}"

if __name__ == "__main__":
    chat_ui = gr.ChatInterface(
        fn=chat_with_sql_bot,
        title="Talk2Tables: SQL Assistant",
        chatbot=gr.Chatbot(height=550),
        textbox=gr.Textbox(placeholder="Ask a question in natural language...", lines=1),
        theme="default"
    )

    chat_ui.launch()