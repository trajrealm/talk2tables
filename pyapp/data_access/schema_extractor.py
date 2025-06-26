import psycopg2
from psycopg2.extras import RealDictCursor
import json

DEFAULT_SCHEMA_NAME = "public"

def get_schema_json(conn_params: dict, schema_name: str = DEFAULT_SCHEMA_NAME) -> dict:
    """
    Extracts the schema of a PostgreSQL database as a JSON object.
    """
    print("Extracting schema...", conn_params, schema_name)
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        tables = _extract_table_columns(cur, schema_name)
        _annotate_primary_keys(cur, schema_name, tables)
        relationships = _extract_foreign_keys(cur, schema_name, tables)

        return {
            "schema": schema_name,
            "tables": [{"name": name, **info} for name, info in tables.items()],
            "relationships": relationships,
        }

    finally:
        cur.close()
        conn.close()


# -----------------------------
# Private helper functions
# -----------------------------

def _extract_table_columns(cur, schema_name: str) -> dict:
    cur.execute("""
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = %s
        ORDER BY table_name, ordinal_position;
    """, (schema_name,))
    
    tables = {}
    for row in cur.fetchall():
        table = row["table_name"]
        column_info = {
            "name": row["column_name"],
            "type": row["data_type"],
            "nullable": row["is_nullable"] == "YES"
        }
        if table not in tables:
            tables[table] = {"columns": []}
        tables[table]["columns"].append(column_info)
    
    return tables


def _annotate_primary_keys(cur, schema_name: str, tables: dict):
    cur.execute("""
        SELECT kcu.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_schema = %s;
    """, (schema_name,))
    
    for row in cur.fetchall():
        table, column = row["table_name"], row["column_name"]
        for col in tables[table]["columns"]:
            if col["name"] == column:
                col["is_primary"] = True


def _extract_foreign_keys(cur, schema_name: str, tables: dict) -> list:
    cur.execute("""
        SELECT
            kcu.table_name, kcu.column_name,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = %s;
    """, (schema_name,))
    
    relationships = []
    for row in cur.fetchall():
        table, column = row["table_name"], row["column_name"]
        ref_table, ref_column = row["foreign_table"], row["foreign_column"]

        for col in tables[table]["columns"]:
            if col["name"] == column:
                col["is_foreign"] = True
                col["references"] = f"{ref_table}.{ref_column}"

        relationships.append({
            "from": f"{table}.{column}",
            "to": f"{ref_table}.{ref_column}",
            "type": "many-to-one"
        })
    
    return relationships


# -----------------------------
# Debug CLI entry point
# -----------------------------
if __name__ == "__main__":
    # Local override for testing
    conn_params = {
        "dbname": "",
        "user": "",
        "password": "",
        "host": "localhost",
        "port": 5432
    }
    schema_name = "public"

    schema = get_schema_json(conn_params, schema_name)
    print(json.dumps(schema, indent=2))

    # Uncomment to write to file
    # output_path = f"{cfg.SCHEMA_JSON_DIR}/{schema_name}_schema.json"
    # with open(output_path, "w") as f:
    #     json.dump(schema, f, indent=2)
    # print(f"Schema saved to: {output_path}")
