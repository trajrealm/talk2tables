
from src.data_access.db_executor import execute_sql
from src.services.llm_ambiguity_checker import check_ambiguity
from src.services.retriever_chain import get_qa_chain
from src.utils.schema_json_util import load_schema
from src.utils.md_utils import strip_sql_markdown
from src.data_access.vectorstore_singleton import get_vectorstore

from dateutil.parser import parse

import json
import traceback

MOCK_MODE = False

def _is_date_string(value: str) -> bool:
    try:
        parse(value)
        return True
    except Exception:
        return False


def get_llm_generated_query(message: str) -> dict:
    if MOCK_MODE:
        return {
            "sql": "SELECT date, cam1 FROM cam1_history WHERE ticker = 'AAPL' LIMIT 10",
            "plot": False,
            "x_axis": "date",
            "y_axis": "cam1",
            "chart_type": "line"
        }
    vectorstore = get_vectorstore()
    chain = get_qa_chain(vectorstore)
    result = chain.invoke({"query": message})
    print("LLM result:\n", result["result"])
    return json.loads(result["result"])


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


def handle_query(nl_query: str):    
    try:
        schema, schema_text = load_schema()

        # Step 1: Check for ambiguity
        if not MOCK_MODE:
            ambiguity_msg = check_for_ambiguity(nl_query, schema_text)
            if ambiguity_msg:
                return ambiguity_msg, None

        try:
            parsed = get_llm_generated_query(nl_query)
        except Exception as e:
            traceback.print_exc()
            return f"⚠️ Failed to parse assistant response: {e}", None
    
        clean_sql = strip_sql_markdown(parsed.get("sql", ""))
        print("clean sql:", clean_sql)  
        columns, rows = execute_sql(clean_sql)

        # return {"result": {"rows": rows, "columns": columns}}
        column_types = []
        for col_index in range(len(columns)):
            sample_value = next((row[col_index] for row in rows if row[col_index] is not None), None)
            if isinstance(sample_value, (int, float)):
                column_types.append("number")
            elif isinstance(sample_value, str) and _is_date_string(sample_value):
                column_types.append("date")
            else:
                column_types.append("string")

        return {
            "sql": clean_sql,
            "ambiguity": False,
            "plot": True,
            "result": {
                "columns": columns,
                "rows": rows,
                "types": column_types,
                "plot": True
            }
        }        

    except Exception as e:
        return {
            "sql": "",
            "result": [],
            "ambiguity": None,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
