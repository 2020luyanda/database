"""This file contain the code access the database"""
import os
from dotenv import load_dotenv

load_dotenv() # this will load the environment variables from the .env file

# On Windows, psycopg needs PostgreSQL's libpq.dll. Point it at the
# PostgreSQL install folder (set PG_BIN in .env if yours is different).
PG_BIN = os.getenv("PG_BIN", r"C:\Program Files\PostgreSQL\18\bin")
if os.name == "nt" and os.path.isdir(PG_BIN):
    os.environ["PATH"] = PG_BIN + os.pathsep + os.environ.get("PATH", "")

import psycopg  # noqa: E402  (must come after the PATH fix above)
from psycopg.rows import dict_row  # noqa: E402

def get_connection()-> psycopg.Connection:
    """This function will return a connection to the database"""
    conn = psycopg.connect(
      host=os.getenv("DB_HOST", "localhost"),
      port=os.getenv("DB_PORT", "5432"),
      dbname=os.getenv("DB_NAME", "dvdrental"),
      user=os.getenv("DB_USER", "postgres"),
      password=os.getenv("DB_PASSWORD", ""),
      row_factory=dict_row,
    )
    conn.read_only = True  # safety: this connection can only READ, never change data
    return conn
def run_query(query: str, params: tuple = None) -> list[dict]:
    """This function will run a query and return the results as a list of dictionaries"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

def get_schema() -> str:
    """Return a text description of all tables and columns."""
    rows = run_query(
        """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
        """
    )
    tables: dict[str, list[str]] = {}
    for row in rows:
        column = f"{row['column_name']} ({row['data_type']})"
        tables.setdefault(row["table_name"], []).append(column)

    return "\n".join(f"{table}: {', '.join(cols)}" for table, cols in tables.items())

if __name__ == "__main__":
    # Quick check: python -m app.db
    print("Films in database:", run_query("SELECT title, rental_rate FROM film ;"))
    print("Database schema:")
    print(get_schema())