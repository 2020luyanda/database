"""Read-only database access for the dvdrental database."""

import os

from dotenv import load_dotenv

load_dotenv()  # load settings from the .env file

# On Windows, psycopg needs PostgreSQL's libpq.dll. Point it at the
# PostgreSQL install folder (set PG_BIN in .env if yours is different).
PG_BIN = os.getenv("PG_BIN", r"C:\Program Files\PostgreSQL\18\bin")
if os.name == "nt" and os.path.isdir(PG_BIN):
    os.environ["PATH"] = PG_BIN + os.pathsep + os.environ.get("PATH", "")

import psycopg  # noqa: E402  (must come after the PATH fix above)
from psycopg.rows import dict_row  # noqa: E402


def get_connection() -> psycopg.Connection:
    """Open a read-only connection to the dvdrental database."""
    timeout_ms = os.getenv("DB_STATEMENT_TIMEOUT_MS", "5000")
    conn = psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "dvdrental"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        row_factory=dict_row,
        options=f"-c statement_timeout={timeout_ms}",  # cancel queries after 5 seconds
    )
    conn.read_only = True  # this connection can only read, never change data
    return conn


def run_query(query: str, params: tuple | None = None, max_rows: int = 500) -> list[dict]:
    """Run a query and return at most max_rows rows as dictionaries."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchmany(max_rows)


def get_schema() -> str:
    """Return a text description of all tables and columns."""
    rows = run_query(
        """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
        """,
        max_rows=10_000,  # the schema has more than 500 columns' worth of rows? keep them all
    )
    tables: dict[str, list[str]] = {}
    for row in rows:
        column = f"{row['column_name']} ({row['data_type']})"
        tables.setdefault(row["table_name"], []).append(column)

    return "\n".join(f"{table}: {', '.join(cols)}" for table, cols in tables.items())


if __name__ == "__main__":
    # Quick check: python -m app.db
    print("Sample films:", run_query("SELECT title, rental_rate FROM film LIMIT 5"))
    print("Database schema:")
    print(get_schema())