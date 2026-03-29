"""Shared test fixtures."""

import psycopg
import pytest

from vital.config import DATABASE_URL


@pytest.fixture()
def test_db(monkeypatch):
    """Create a clean test schema, run the test, then tear down."""
    schema = f"test_{id(monkeypatch):x}"
    monkeypatch.setattr("vital.health_store.DATABASE_URL", DATABASE_URL)

    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
        conn.execute(f"CREATE SCHEMA {schema}")
        conn.execute(f"SET search_path TO {schema}")

    # Patch _connect to always use the test schema
    original_connect = psycopg.connect

    def _patched_connect(conninfo, **kwargs):
        c = original_connect(conninfo, **kwargs)
        c.execute(f"SET search_path TO {schema}")
        return c

    monkeypatch.setattr("psycopg.connect", _patched_connect)

    from vital.health_store import init_db
    init_db()

    yield schema

    monkeypatch.undo()
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
