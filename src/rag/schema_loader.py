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

def load_schema_with_tags(schema_json):
    docs = []
    for table in schema_json['tables']:
        table_metadata = {
            "table": table["name"],
            "tags": table.get("tags", []),
            "schema": schema_json["schema"]
        }

        table_text = f"Table: {table['name']}\n{table.get('description', '')}\n"
        for col in table["columns"]:
            line = f"  - {col['name']} ({col['type']})"
            if "semantic_type" in col:
                line += f" [semantic_type: {col['semantic_type']}]"
            if "tags" in col:
                line += f" [tags: {', '.join(col['tags'])}]"
            table_text += line + "\n"

        docs.append(Document(page_content=table_text, metadata=table_metadata))
    return docs
