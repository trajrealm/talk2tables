import psycopg2
# from config.config import DB_CONN_PARAMS

def execute_sql(sql: str, DB_CONN_PARAMS: dict):
    try:
        conn = psycopg2.connect(**DB_CONN_PARAMS)
        cur = conn.cursor()
        cur.execute(sql)
        
        if cur.description:  # If the query returns rows
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return columns, rows
        else:  # For UPDATE, INSERT, etc.
            conn.commit()
            cur.close()
            conn.close()
            return [], [["Query executed successfully."]]
    except Exception as e:
        return [], [[f"⚠️ Error: {str(e)}"]]
