import os
import json
import subprocess
import psycopg2
import psycopg2.extras

from config import ACTOR_CODE

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
    SQL_QUERY = f"""
WITH ref_actor_events AS (
  SELECT globaleventid
  FROM events
  WHERE actor1type1code = '{ACTOR_CODE}'
        OR actor1type2code = '{ACTOR_CODE}'
        OR actor1type3code = '{ACTOR_CODE}'
        OR actor2type1code = '{ACTOR_CODE}'
        OR actor2type2code = '{ACTOR_CODE}'
        OR actor2type3code = '{ACTOR_CODE}'
  UNION
  SELECT globaleventid
  FROM events_translated
  WHERE actor1type1code = '{ACTOR_CODE}'
        OR actor1type2code = '{ACTOR_CODE}'
        OR actor1type3code = '{ACTOR_CODE}'
        OR actor2type1code = '{ACTOR_CODE}'
        OR actor2type2code = '{ACTOR_CODE}'
        OR actor2type3code = '{ACTOR_CODE}'
),
combined_mentions AS (
  SELECT *
  FROM mentions
  WHERE globaleventid IN (SELECT globaleventid FROM ref_actor_events)
    AND confidence >= 70
  UNION ALL
  SELECT *
  FROM mentions_translated
  WHERE globaleventid IN (SELECT globaleventid FROM ref_actor_events)
    AND confidence >= 70
),
unique_mentions AS (
  SELECT DISTINCT ON (mentionidentifier) *
  FROM combined_mentions
  ORDER BY mentionidentifier, globaleventid
)
SELECT DISTINCT ON (globaleventid) *
FROM unique_mentions
ORDER BY globaleventid, mentionidentifier;
"""
    results = run_sql_query(SQL_QUERY)
    print(json.dumps(results, indent=2))

    # For each JSON object returned, spawn a crawler container with the mentionidentifier as argument.
    for row in results:
        url_arg = row.get("mentionidentifier")
        if url_arg:
            print(f"Spawning crawler for URL: {url_arg}")
            subprocess.Popen([
                "docker", "compose", "run", "--rm", "crawler",
                "python", "crawler.py", url_arg
            ])

if __name__ == "__main__":
    main()
