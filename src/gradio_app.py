import gradio as gr
from rag.schema_loader import load_schema_json, flatten_schema
from rag.embedder import create_vectorstore_from_text
from rag.retriever_chain import get_qa_chain
from rag.load_api_key import load_api_key
import re
from db_executor import execute_sql
from rag.llm_ambiguity_checker import check_ambiguity
from rag.schema_loader import flatten_schema
from rag.visualizer import plot_with_plotly
import json
import traceback
import os
import subprocess

MOCK_MODE = False


def start_static_server():
    static_dir = os.path.abspath("static")
    subprocess.Popen(["python", "-m", "http.server", "7861", "--directory", static_dir])


def strip_sql_markdown(text: str) -> str:
    return re.sub(r"^```sql\s*|^```\s*|```$", "", text.strip(), flags=re.MULTILINE).strip()


def load_schema() -> tuple:
    schema = load_schema_json("public_schema.json")
    schema_text = flatten_schema(schema)
    return schema, schema_text

def check_for_ambiguity(message: str, schema_text: str) -> str | None:
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
    return None

def get_llm_generated_query(message: str, vectorstore) -> dict:
    if MOCK_MODE:
        return {
            "sql": "SELECT date, cam1 FROM cam1_history WHERE ticker = 'AAPL'",
            "plot": True,
            "x_axis": "date",
            "y_axis": "cam1",
            "chart_type": "line"
        }

    chain = get_qa_chain(vectorstore)
    result = chain.invoke({"query": message})
    print("LLM result:\n", result["result"])
    return json.loads(result["result"])

def execute_sql_and_plot(sql: str, plot: bool, x_axis: str, y_axis: str, chart_type: str) -> tuple[str | None, str | None]:
    clean_sql = strip_sql_markdown(sql)
    columns, rows = execute_sql(clean_sql)

    if not columns:
        return rows[0][0], None

    if plot and x_axis in columns and y_axis in columns:
        try:
            web_path = plot_with_plotly(columns, rows, x_axis, y_axis, chart_type)
            iframe_html = f"""
                <iframe src="{web_path}" width="100%" height="500px" style="border:none;"></iframe>
            """
            print(web_path, iframe_html)
            return None, iframe_html
        except Exception as e:
            traceback.print_exc()
            return f"⚠️ Failed to generate plot: {e}", None

    # Fallback: generate markdown table
    table_md = "| " + " | ".join(columns) + " |\n"
    table_md += "| " + " | ".join(["---"] * len(columns)) + " |\n"
    for row in rows:
        table_md += "| " + " | ".join(map(str, row)) + " |\n"
    return f"**Assistant:**\n{table_md}", None


def chat_with_sql_bot(message, history):
    load_api_key()
    schema, schema_text = load_schema()

    # Step 1: Check ambiguity
    if not MOCK_MODE:
        ambiguity_msg = check_for_ambiguity(message, schema_text)
        if ambiguity_msg:
            return ambiguity_msg, None

    # Step 2: Query generation
    vectorstore = create_vectorstore_from_text(schema_text)
    try:
        parsed = get_llm_generated_query(message, vectorstore)
    except Exception as e:
        traceback.print_exc()
        return f"⚠️ Failed to parse assistant response: {e}", None

    # Step 3: SQL execution + plot or table
    return execute_sql_and_plot(
        parsed.get("sql", ""),
        parsed.get("plot", False),
        parsed.get("x_axis", ""),
        parsed.get("y_axis", ""),
        parsed.get("chart_type", "bar")
    )


if __name__ == "__main__":
    start_static_server()
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(height=550)
        user_input = gr.Textbox(placeholder="Ask a question in natural language...", lines=1, label="Query")
        html_plot = gr.HTML(visible=False)

        def handle_query(message, history):
            
            history = history + [(message, None)]

            table_output, plot_html = chat_with_sql_bot(message, [])

            if table_output:
                history[-1] = (message, table_output)
            else:
                history[-1] = (message, "✅ Plot generated below ⬇️")

            html_update = gr.update(value=plot_html, visible=bool(plot_html))
            chat_update = [] if table_output is None else [(message, table_output)]

            return history, html_update, ""

        user_input.submit(handle_query, inputs=[user_input, chatbot], outputs=[chatbot, html_plot, user_input])

    demo.launch()

