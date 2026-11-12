# app.db must be imported FIRST: it tells Python where PostgreSQL's libpq.dll is.
from app.db import get_connection, get_schema, run_query

import psycopg  # noqa: E402
import pytest  # noqa: E402


def test_can_connect():
    with get_connection() as conn:
        assert not conn.closed


def test_film_table_has_rows():
    rows = run_query("SELECT COUNT(*) AS total FROM film")
    assert rows[0]["total"] > 0


def test_customer_count():
    rows = run_query("SELECT COUNT(*) AS n FROM customer")
    assert rows[0]["n"] == 599


def test_query_with_params():
    rows = run_query("SELECT title FROM film WHERE film_id = %s", (1,))
    assert len(rows) == 1


def test_schema_includes_film_table():
    assert "film:" in get_schema()


def test_writes_are_blocked():
    with pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
        run_query("DELETE FROM actor WHERE actor_id = -1")


def test_row_limit():
    rows = run_query("SELECT * FROM rental", max_rows=10)
    assert len(rows) == 10


def test_slow_query_is_cancelled():
    with pytest.raises(psycopg.errors.QueryCanceled):
        run_query("SELECT pg_sleep(10)")