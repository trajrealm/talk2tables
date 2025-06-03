import json
from langchain.schema import Document

def load_schema_json(path: str):
    with open(path, "r") as f:
        return json.load(f)

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
