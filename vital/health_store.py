"""SQLite storage for Apple Watch health data."""

import json
import sqlite3
from datetime import datetime, timedelta, timezone

from vital.config import DATA_DIR, DB_PATH

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS health_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recorded_at TEXT NOT NULL,
    received_at TEXT NOT NULL DEFAULT (datetime('now')),
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    metadata TEXT
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_health_metric_date
ON health_data (metric, recorded_at);
"""


def init_db() -> None:
    """Create database and tables if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(_CREATE_TABLE)
        conn.execute(_CREATE_INDEX)


def insert_metrics(metrics: list[dict]) -> int:
    """Insert a batch of health metrics. Returns count of inserted rows.

    Expected metric format:
    {
        "metric": "heart_rate",
        "value": 72.0,
        "unit": "bpm",
        "recorded_at": "2026-03-28T08:30:00Z",
        "metadata": {}  # optional
    }
    """
    with sqlite3.connect(DB_PATH) as conn:
        rows = [
            (
                m["recorded_at"],
                m["metric"],
                m["value"],
                m.get("unit"),
                json.dumps(m.get("metadata")) if m.get("metadata") else None,
            )
            for m in metrics
        ]
        conn.executemany(
            "INSERT INTO health_data (recorded_at, metric, value, unit, metadata) VALUES (?, ?, ?, ?, ?)",
            rows,
        )
    return len(rows)


def get_latest(metric: str, limit: int = 1) -> list[dict]:
    """Get the N most recent values for a given metric."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM health_data WHERE metric = ? ORDER BY recorded_at DESC LIMIT ?",
            (metric, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def get_summary(hours: int = 24) -> dict:
    """Get aggregated summary of all metrics over the last N hours."""
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT metric, unit,
                   COUNT(*) as count,
                   ROUND(AVG(value), 1) as avg,
                   ROUND(MIN(value), 1) as min,
                   ROUND(MAX(value), 1) as max,
                   ROUND(value, 1) as latest
            FROM health_data
            WHERE recorded_at >= ?
            GROUP BY metric
            ORDER BY metric
            """,
            (since,),
        ).fetchall()
    return {row["metric"]: dict(row) for row in rows}


def get_recent_raw(hours: int = 24) -> list[dict]:
    """Get all raw data points from the last N hours."""
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM health_data WHERE recorded_at >= ? ORDER BY recorded_at DESC",
            (since,),
        ).fetchall()
    return [dict(r) for r in rows]
