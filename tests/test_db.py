from app.db import get_connection, run_query


def test_can_connect():
    with get_connection() as conn:
        assert not conn.closed


def test_film_table_has_rows():
    rows = run_query("SELECT COUNT(*) AS total FROM film;")
    assert rows[0]["total"] > 0
import psycopg
import pytest

from app.db import get_schema, run_query


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