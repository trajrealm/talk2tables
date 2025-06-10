from config.config import SCHEMA_JSON_DIR
import json
import os

def load_schema_json(path: str):
    print(path)
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


def load_schema() -> tuple:
    for file in os.listdir(SCHEMA_JSON_DIR):
        if file.endswith(".json"):
            json_path = file
            schema = load_schema_json(f"""{SCHEMA_JSON_DIR}/{json_path}""")
            schema_text = flatten_schema(schema)
            break
            ## TODO : handle multiple json files
    return schema, schema_text

