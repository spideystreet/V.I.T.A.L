"""Migrate existing health data from SQLite to PostgreSQL (normalized schema).

Usage:
    PYTHONPATH=. uv run python scripts/migrate_sqlite_to_pg.py [--sqlite-path ~/.vital/health.db]
"""

import argparse
import sqlite3
from pathlib import Path

import psycopg

from vital.config import DATABASE_URL
from vital.health_store import init_db


def migrate(sqlite_path: Path) -> int:
    """Copy all rows from SQLite health_data into PostgreSQL. Returns row count."""
    if not sqlite_path.exists():
        print(f"SQLite database not found: {sqlite_path}")
        return 0

    init_db()

    conn_sqlite = sqlite3.connect(sqlite_path)
    conn_sqlite.row_factory = sqlite3.Row
    rows = conn_sqlite.execute("SELECT * FROM health_data ORDER BY id").fetchall()
    conn_sqlite.close()

    if not rows:
        print("No rows to migrate.")
        return 0

    with psycopg.connect(DATABASE_URL) as conn:
        # Build metric name → id lookup
        catalog = {
            r[0]: r[1]
            for r in conn.execute("SELECT name, id FROM metric_catalog").fetchall()
        }

        skipped = 0
        inserted = 0
        for row in rows:
            metric_name = row["metric"]
            metric_id = catalog.get(metric_name)
            if metric_id is None:
                print(f"  Skipping unknown metric: {metric_name}")
                skipped += 1
                continue

            conn.execute(
                "INSERT INTO health_data (recorded_at, received_at, metric_id, value, metadata) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    row["recorded_at"],
                    row["received_at"],
                    metric_id,
                    row["value"],
                    row["metadata"],
                ),
            )
            inserted += 1

    print(f"Migrated {inserted} rows to PostgreSQL ({skipped} skipped).")
    return inserted


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate SQLite health data to PostgreSQL")
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=Path.home() / ".vital" / "health.db",
        help="Path to SQLite database",
    )
    args = parser.parse_args()
    migrate(args.sqlite_path)
