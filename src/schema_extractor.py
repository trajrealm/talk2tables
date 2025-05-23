import psycopg2
import json
import config as cfg

SCHEMA_NAME = "public"
def get_schema_json():
    conn = psycopg2.connect(**cfg.DB_CONN_PARAMS)
    cur = conn.cursor()

    # Get table and column info
    cur.execute("""
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = %s
        ORDER BY table_name, ordinal_position;
    """, (SCHEMA_NAME,))
    
    tables = {}
    for table_name, column_name, data_type, is_nullable in cur.fetchall():
        if table_name not in tables:
            tables[table_name] = {"columns": []}
        tables[table_name]["columns"].append({
            "name": column_name,
            "type": data_type,
            "nullable": is_nullable == "YES"
        })

    # Get primary keys
    cur.execute("""
        SELECT
            kcu.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_schema = %s;
    """, (SCHEMA_NAME,))
    for table_name, column_name in cur.fetchall():
        for col in tables[table_name]["columns"]:
            if col["name"] == column_name:
                col["is_primary"] = True

    # Get foreign keys
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
    """, (SCHEMA_NAME,))
    
    relationships = []
    for table, column, ref_table, ref_column in cur.fetchall():
        for col in tables[table]["columns"]:
            if col["name"] == column:
                col["is_foreign"] = True
                col["references"] = f"{ref_table}.{ref_column}"
        relationships.append({
            "from": f"{table}.{column}",
            "to": f"{ref_table}.{ref_column}",
            "type": "many-to-one"
        })

    schema_json = {
        "schema": SCHEMA_NAME,
        "tables": [{"name": name, **info} for name, info in tables.items()],
        "relationships": relationships
    }

    cur.close()
    conn.close()

    return schema_json


if __name__ == "__main__":
    schema = get_schema_json()
    with open(f'{SCHEMA_NAME}_schema.json', "w") as f:
        json.dump(schema, f, indent=2)
    print(f'{SCHEMA_NAME}_schema.json')
