import json
import os
from typing import Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.config.settings import settings
from src.data_access.models import UserDatabase, UserDbSchema


def load_schema_json(path: str) -> dict:
    """Load JSON schema from file."""
    print(f"Loading schema JSON from: {path}")
    with open(path, "r") as f:
        return json.load(f)


def flatten_table(table: dict) -> str:
    """Convert a single table schema dict to a flattened text representation."""
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
    """Convert full schema dict to a flattened text representation."""
    text = f"Schema: {schema.get('schema', '')}\n\n"
    for table in schema.get("tables", []):
        text += f"Table: {table['name']}\n"
        for col in table.get('columns', []):
            line = f"  - {col['name']} ({col['type']})"
            if col.get("is_primary"):
                line += " [PK]"
            if col.get("is_foreign"):
                line += f" [FK -> {col.get('references')}]"
            text += line + "\n"
        text += "\n"
    return text


def load_schema_from_files(schema_dir: str = settings.SCHEMA_JSON_DIR) -> Tuple[Optional[dict], Optional[str]]:
    """
    Load the first JSON schema file found in the given directory.
    Returns a tuple of (schema_dict, flattened_text) or (None, None) if no file found.
    """
    for file in os.listdir(schema_dir):
        if file.endswith(".json"):
            json_path = os.path.join(schema_dir, file)
            schema = load_schema_json(json_path)
            schema_text = flatten_schema(schema)  # TODO: Optionally flatten each table separately
            return schema, schema_text
    return None, None


def load_schema_from_db(user_id: UUID, db_id: UUID, db: Session) -> Tuple[UserDbSchema, str]:
    """
    Load schema for a specific user's database from the DB.
    Raises HTTPException if not found.
    Returns the UserDbSchema ORM object and flattened schema text.
    """
    user_db = db.query(UserDatabase).filter(
        UserDatabase.id == db_id,
        UserDatabase.user_id == user_id
    ).first()

    if not user_db:
        raise HTTPException(status_code=404, detail="Database not found for user.")

    schema_entry = db.query(UserDbSchema).filter(
        UserDbSchema.user_database_id == db_id
    ).first()

    if not schema_entry:
        raise HTTPException(status_code=404, detail="Schema not found for this database.")

    schema_text = flatten_schema(schema_entry.schema_json_info)
    return schema_entry, schema_text
