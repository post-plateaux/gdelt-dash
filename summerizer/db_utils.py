import os
import psycopg2
import psycopg2.extras

def run_sql_query(query):
    host = os.environ.get("POSTGRES_HOST", "postgres")
    dbname = os.environ.get("POSTGRES_DB")
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    port = int(os.environ.get("POSTGRES_PORT", 5432))
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result
