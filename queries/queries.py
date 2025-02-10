import os
import json
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

def main():
    SQL_QUERY = "SELECT * FROM some_table;"  # Replace with your actual SQL query
    results = run_sql_query(SQL_QUERY)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
