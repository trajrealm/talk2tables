from config.config import SCHEMA_JSON_DIR
import json
import os

def load_schema_json(path: str):
    print(path)
    with open(path, "r") as f:
        return json.load(f)


def flatten_table(table: dict) -> str:
    lines = [f"Table: {table['name']}"]
    for col in table.get("columns", []):
        line = f"- {col['name']} ({col['type']})"
        if col.get("is_primary"):
            line += " [PK]"
        if col.get("is_foreign"):
            line += f" [FK -> {col.get('references')}]"
        lines.append(line)
    return "\n".join(lines)
    

def flatten_schema(schema: dict) -> str:
    text = f"Schema: {schema.get('schema', '')}\n\n"
    for table in schema.get("tables", []):
        text += f"Table: {table['name']}\n"
        for col in table['columns']:
            line = f"  - {col['name']} ({col['type']})"
            if col.get("is_primary"):
                line += " [PK]"
            if col.get("is_foreign"):
                line += f" [FK -> {col.get('references')}]"
            text += line + "\n"
        text += "\n"
    return text


def load_schema() -> tuple:
    for file in os.listdir(SCHEMA_JSON_DIR):
        if file.endswith(".json"):
            json_path = file
            schema = load_schema_json(f"""{SCHEMA_JSON_DIR}/{json_path}""")
            schema_text = flatten_schema(schema) # TODO: Use flatten_table for each table with metadata is better option
            break
            ## TODO : handle multiple json files
    return schema, schema_text


from uuid import UUID
from sqlalchemy.orm import Session
from src.data_access.database import get_db
from src.data_access.models import UserDatabase, UserDbSchema
from fastapi import HTTPException, Depends



def load_schema_from_db(user_id: UUID, db_id: UUID, db:Session) -> tuple:
    user_db = db.query(UserDatabase).filter(
        UserDatabase.id == db_id,
        UserDatabase.user_id == user_id
    ).first()

    if not user_db:
        raise HTTPException(status_code=404, detail="Database not found for user.")

    # Fetch schema
    schema_entry = db.query(UserDbSchema).filter(
        UserDbSchema.user_database_id == db_id
    ).first()# optional: latest schema version

    if not schema_entry:
        raise HTTPException(status_code=404, detail="Schema not found for this database.")

    schema_text = flatten_schema(schema_entry.schema_json_info)

    return schema_entry, schema_text