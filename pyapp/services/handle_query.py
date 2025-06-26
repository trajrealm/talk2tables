import json
import traceback
from uuid import UUID
from dateutil.parser import parse

from sqlalchemy.orm import Session

from src.data_access.db_executor import execute_sql
from src.data_access.vectorstore_singleton import get_or_create_vectorstore
from src.services.llm_ambiguity_checker import check_ambiguity
from src.services.retriever_chain import get_qa_chain
from src.utils.schema_json_util import load_schema_from_db
from src.utils.md_utils import strip_sql_markdown
from src.config.settings import settings
from src.data_access.models import UserDatabase, UserDbSchema
from src.utils.auth import decrypt_value




# ----------------------------- Utility Methods -----------------------------

def _is_date_string(value: str) -> bool:
    try:
        parse(value)
        return True
    except Exception:
        return False


def build_prompt_with_history(history: list[dict], latest_query: str) -> str:
    prompt = ""
    for turn in history:
        prompt += f"User: {turn.get('user', '')}\nBot: {turn.get('Bot', '')}\n"
    prompt += f"User: {latest_query}\nBot:"
    return prompt


def determine_column_types(columns: list[str], rows: list[list]) -> list[str]:
    column_types = []
    for col_index in range(len(columns)):
        sample_value = next((row[col_index] for row in rows if row[col_index] is not None), None)
        if isinstance(sample_value, (int, float)):
            column_types.append("number")
        elif isinstance(sample_value, str) and _is_date_string(sample_value):
            column_types.append("date")
        else:
            column_types.append("string")
    return column_types


# ----------------------------- Core LLM Invocation -----------------------------

def get_llm_generated_query(
    message: str,
    user_id: UUID,
    db_id: UUID,
    db: Session
) -> dict:
    if settings.MOCK_MODE:
        return {
            "sql": "SELECT date, cam1 FROM cam1_history WHERE ticker = 'AAPL' LIMIT 10",
            "plot": False,
            "x_axis": "date",
            "y_axis": "cam1",
            "chart_type": "line"
        }

    vectorstore = get_or_create_vectorstore(user_id, db_id, db)

    chain = get_qa_chain(vectorstore)
    result = chain.invoke({"query": message})
    print("LLM result:\n", result["result"])
    return json.loads(result["result"])


# ----------------------------- Ambiguity Checker -----------------------------

def check_for_ambiguity(message: str, schema_text: str) -> str | None:
    ambiguity = check_ambiguity(message, schema_text)
    if ambiguity.get("ambiguous"):
        clarify_items = ambiguity.get("clarify", [])
        clarification_msg = "🧙 Ambiguity detected in your question:\n"
        for item in clarify_items:
            if isinstance(item, dict):
                for term, matches in item.items():
                    clarification_msg += f"**{term}** could refer to: {', '.join(matches) if isinstance(matches, list) else matches}\n"
            elif isinstance(item, str):
                clarification_msg += f"- {item}\n"
        clarification_msg += "Please rephrase your query or specify the exact table/column."
        return clarification_msg
    return None


# ----------------------------- Main Handler -----------------------------

def handle_query(
    nl_query: str,
    history: list[dict],
    db_id: UUID,
    user_id: UUID,
    db: Session
):
    try:
        schema_entry, schema_text = load_schema_from_db(user_id, db_id, db)

        # Step 1: Check ambiguity
        if not settings.MOCK_MODE:
            ambiguity_msg = check_for_ambiguity(nl_query, schema_text)
            if ambiguity_msg:
                return {
                    "ambiguity": True,
                    "ambiguity_msg": ambiguity_msg,
                }

        prompt = build_prompt_with_history(history, nl_query) if history else nl_query
        parsed = get_llm_generated_query(nl_query, user_id, db_id, db)

        clean_sql = strip_sql_markdown(parsed.get("sql", ""))
        print("clean sql:", clean_sql)


        user_db = db.query(UserDatabase).filter(
            UserDatabase.id == db_id,
            UserDatabase.user_id == user_id
        ).first()

        columns, rows = execute_sql(clean_sql, {
            "host": decrypt_value(user_db.host),
            "port": user_db.port,
            "user": decrypt_value(user_db.username),
            "password": decrypt_value(user_db.password_encrypted),
            "dbname": decrypt_value(user_db.db_name)
        })

        column_types = determine_column_types(columns, rows)

        return {
            "sql": clean_sql,
            "ambiguity": False,
            "result": {
                "columns": columns,
                "rows": rows,
                "types": column_types,
                "plot": parsed.get("plot", False)
            }
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "sql": "",
            "result": [],
            "ambiguity": None,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


# ----------------------------- Legacy / Dev Test Handler -----------------------------

def handle_query_old(nl_query: str, history: list[dict]):
    try:
        schema, schema_text = None # load_schema()

        if not settings.MOCK_MODE:
            ambiguity_msg = check_for_ambiguity(nl_query, schema_text)
            if ambiguity_msg:
                return {
                    "ambiguity": True,
                    "ambiguity_msg": ambiguity_msg,
                }

        prompt = build_prompt_with_history(history, nl_query) if history else nl_query
        parsed = get_llm_generated_query(prompt, None, None, None)

        clean_sql = strip_sql_markdown(parsed.get("sql", ""))
        print("clean sql:", clean_sql)
        columns, rows = execute_sql(clean_sql)

        column_types = determine_column_types(columns, rows)

        return {
            "sql": clean_sql,
            "ambiguity": False,
            "result": {
                "columns": columns,
                "rows": rows,
                "types": column_types,
                "plot": parsed.get("plot", False)
            }
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "sql": "",
            "result": [],
            "ambiguity": None,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
