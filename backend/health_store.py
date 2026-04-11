"""PostgreSQL storage for Apple Watch health data."""

import json
from datetime import UTC, datetime, timedelta

import psycopg
from psycopg.rows import dict_row

from backend.config import DATABASE_URL

_CREATE_METRIC_CATALOG = """
CREATE TABLE IF NOT EXISTS metric_catalog (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    unit TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT
);
"""

_CREATE_HEALTH_DATA = """
CREATE TABLE IF NOT EXISTS health_data (
    id SERIAL PRIMARY KEY,
    recorded_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metric_id INTEGER NOT NULL REFERENCES metric_catalog(id),
    value DOUBLE PRECISION NOT NULL,
    value_end DOUBLE PRECISION,
    source TEXT,
    metadata JSONB
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_health_metric_date
ON health_data (metric_id, recorded_at);
"""

# Default metrics seeded on init
_DEFAULT_METRICS = [
    ("heart_rate", "bpm", "vitals", "Instantaneous heart rate"),
    ("resting_hr", "bpm", "vitals", "Resting heart rate"),
    ("hrv", "ms", "vitals", "Heart rate variability (SDNN)"),
    ("spo2", "%", "vitals", "Blood oxygen saturation"),
    ("respiratory_rate", "brpm", "vitals", "Respiratory rate (breaths per minute)"),
    ("wrist_temperature", "C", "vitals", "Wrist temperature deviation from baseline"),
    ("steps", "count", "activity", "Step count"),
    ("active_calories", "kcal", "activity", "Active energy burned"),
    ("distance", "km", "activity", "Walking + running distance"),
    ("sleep", "hours", "sleep", "Sleep duration"),
    ("sleep_deep", "hours", "sleep", "Deep sleep duration"),
    ("sleep_rem", "hours", "sleep", "REM sleep duration"),
    ("vo2_max", "mL/kg/min", "vitals", "VO2 max (cardio fitness)"),
    ("resting_energy", "kcal", "activity", "Resting energy burned (basal metabolism)"),
    ("workout", "min", "activity", "Workout duration"),
    ("stand_time", "min", "activity", "Standing time"),
    ("mindful_minutes", "min", "activity", "Mindful / meditation sessions"),
    ("walking_hr_avg", "bpm", "vitals", "Walking heart rate average"),
    ("audio_exposure", "dBASPL", "environment", "Environmental audio exposure level"),
    ("exercise_time", "min", "activity", "Apple exercise time (moderate+ activity)"),
]


def _connect(**kwargs):
    """Open a connection to PostgreSQL."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row, **kwargs)


def init_db() -> None:
    """Create tables, indexes, and seed default metrics."""
    with _connect() as conn:
        conn.execute(_CREATE_METRIC_CATALOG)
        conn.execute(_CREATE_HEALTH_DATA)
        conn.execute(_CREATE_INDEX)
        for name, unit, category, description in _DEFAULT_METRICS:
            conn.execute(
                "INSERT INTO metric_catalog (name, unit, category, description) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO NOTHING",
                (name, unit, category, description),
            )


def _resolve_metric_id(cur, metric_name: str) -> int:
    """Get metric_id from name, raising ValueError if unknown."""
    row = cur.execute("SELECT id FROM metric_catalog WHERE name = %s", (metric_name,)).fetchone()
    if row is None:
        raise ValueError(f"Unknown metric: {metric_name!r}. Register it in metric_catalog first.")
    return row["id"]


def insert_metrics(metrics: list[dict]) -> int:
    """Insert a batch of health metrics. Returns count of inserted rows."""
    if not metrics:
        return 0
    with _connect() as conn:
        with conn.cursor() as cur:
            # Batch-resolve all metric IDs in one query to avoid N+1
            unique_names = list({m["metric"] for m in metrics})
            catalog_rows = cur.execute(
                "SELECT name, id FROM metric_catalog WHERE name = ANY(%s)",
                (unique_names,),
            ).fetchall()
            id_map = {r["name"]: r["id"] for r in catalog_rows}
            missing = set(unique_names) - set(id_map)
            if missing:
                raise ValueError(
                    f"Unknown metric(s): {missing!r}. Register in metric_catalog first."
                )

            rows = []
            for m in metrics:
                rows.append(
                    (
                        m["recorded_at"],
                        id_map[m["metric"]],
                        m["value"],
                        m.get("value_end"),
                        m.get("source"),
                        json.dumps(m["metadata"]) if m.get("metadata") else None,
                    )
                )
            cur.executemany(
                "INSERT INTO health_data "
                "(recorded_at, metric_id, value, value_end, source, metadata) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                rows,
            )
    return len(rows)


def get_latest(metric: str, limit: int = 1) -> list[dict]:
    """Get the N most recent values for a given metric."""
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT d.*, c.name as metric, c.unit
            FROM health_data d
            JOIN metric_catalog c ON c.id = d.metric_id
            WHERE c.name = %s
            ORDER BY d.recorded_at DESC
            LIMIT %s
            """,
            (metric, limit),
        ).fetchall()
    return rows


def get_summary(hours: int = 24) -> dict:
    """Get aggregated summary of all metrics over the last N hours."""
    since = datetime.now(UTC) - timedelta(hours=hours)
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT c.name as metric, c.unit,
                   COUNT(*) as count,
                   ROUND(AVG(d.value)::numeric, 1) as avg,
                   ROUND(MIN(d.value)::numeric, 1) as min,
                   ROUND(MAX(d.value)::numeric, 1) as max,
                   ROUND((SELECT d2.value FROM health_data d2
                          WHERE d2.metric_id = c.id AND d2.recorded_at >= %s
                          ORDER BY d2.recorded_at DESC LIMIT 1)::numeric, 1) as latest
            FROM health_data d
            JOIN metric_catalog c ON c.id = d.metric_id
            WHERE d.recorded_at >= %s
            GROUP BY c.id, c.name, c.unit
            ORDER BY c.name
            """,
            (since, since),
        ).fetchall()
    return {
        row["metric"]: {
            "unit": row["unit"],
            "count": row["count"],
            "avg": float(row["avg"]),
            "min": float(row["min"]),
            "max": float(row["max"]),
            "latest": float(row["latest"]),
        }
        for row in rows
    }


def _avg_for_window(conn, metric: str, start: datetime, end: datetime | None = None) -> dict:
    """Return {avg, count} for a metric in a time window. Shared by get_trend/compare_periods."""
    if end is None:
        row = conn.execute(
            """
            SELECT ROUND(AVG(d.value)::numeric, 1) as avg, COUNT(*) as count
            FROM health_data d
            JOIN metric_catalog c ON c.id = d.metric_id
            WHERE c.name = %s AND d.recorded_at >= %s
            """,
            (metric, start),
        ).fetchone()
    else:
        row = conn.execute(
            """
            SELECT ROUND(AVG(d.value)::numeric, 1) as avg, COUNT(*) as count
            FROM health_data d
            JOIN metric_catalog c ON c.id = d.metric_id
            WHERE c.name = %s AND d.recorded_at >= %s AND d.recorded_at < %s
            """,
            (metric, start, end),
        ).fetchone()
    return row


def get_trend(metric: str, days: int = 3) -> dict:
    """Compare the last 24h average to the previous N days average for a metric."""
    now = datetime.now(UTC)
    recent_start = now - timedelta(hours=24)
    previous_start = now - timedelta(days=days)

    with _connect() as conn:
        recent = _avg_for_window(conn, metric, recent_start)
        previous = _avg_for_window(conn, metric, previous_start, recent_start)

    recent_avg = float(recent["avg"]) if recent["avg"] else None
    previous_avg = float(previous["avg"]) if previous["avg"] else None

    if recent_avg is None or previous_avg is None or previous_avg == 0:
        return {
            "metric": metric,
            "recent_avg": recent_avg,
            "previous_avg": previous_avg,
            "direction": "unknown",
            "change_pct": None,
        }

    change_pct = round((recent_avg - previous_avg) / previous_avg * 100, 1)
    if change_pct > 5:
        direction = "up"
    elif change_pct < -5:
        direction = "down"
    else:
        direction = "stable"

    return {
        "metric": metric,
        "recent_avg": recent_avg,
        "previous_avg": previous_avg,
        "direction": direction,
        "change_pct": change_pct,
    }


def compare_periods(
    metric: str, period_a_hours: int, period_b_hours: int, period_b_offset_hours: int
) -> dict:
    """Compare two time periods for a metric.

    period_a: last N hours (e.g. 24 = today)
    period_b: N hours starting at offset (e.g. hours=24, offset=48 = two days ago)
    """
    now = datetime.now(UTC)
    a_start = now - timedelta(hours=period_a_hours)
    b_end = now - timedelta(hours=period_b_offset_hours)
    b_start = b_end - timedelta(hours=period_b_hours)

    with _connect() as conn:
        a = _avg_for_window(conn, metric, a_start)
        b = _avg_for_window(conn, metric, b_start, b_end)

    a_avg = float(a["avg"]) if a["avg"] else None
    b_avg = float(b["avg"]) if b["avg"] else None

    return {
        "metric": metric,
        "period_a_avg": a_avg,
        "period_b_avg": b_avg,
        "period_a_label": f"last {period_a_hours}h",
        "period_b_label": f"{period_b_offset_hours}-{period_b_offset_hours + period_b_hours}h ago",
    }


def get_correlation(metric_a: str, metric_b: str, days: int = 7) -> dict:
    """Compute daily averages and simple correlation between two metrics."""
    since = datetime.now(UTC) - timedelta(days=days)

    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT DATE(d.recorded_at) as day, c.name as metric,
                   ROUND(AVG(d.value)::numeric, 2) as avg
            FROM health_data d
            JOIN metric_catalog c ON c.id = d.metric_id
            WHERE c.name IN (%s, %s) AND d.recorded_at >= %s
            GROUP BY DATE(d.recorded_at), c.name
            ORDER BY day
            """,
            (metric_a, metric_b, since),
        ).fetchall()

    # Group by day
    days_a = {}
    days_b = {}
    for r in rows:
        day = str(r["day"])
        if r["metric"] == metric_a:
            days_a[day] = float(r["avg"])
        else:
            days_b[day] = float(r["avg"])

    # Find common days
    common_days = sorted(set(days_a) & set(days_b))
    if len(common_days) < 2:
        return {
            "metric_a": metric_a,
            "metric_b": metric_b,
            "correlation": None,
            "note": "Not enough overlapping data to compute correlation",
            "data_points": len(common_days),
        }

    vals_a = [days_a[d] for d in common_days]
    vals_b = [days_b[d] for d in common_days]

    # Pearson correlation
    n = len(vals_a)
    mean_a = sum(vals_a) / n
    mean_b = sum(vals_b) / n
    cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(vals_a, vals_b)) / n
    std_a = (sum((a - mean_a) ** 2 for a in vals_a) / n) ** 0.5
    std_b = (sum((b - mean_b) ** 2 for b in vals_b) / n) ** 0.5

    if std_a == 0 or std_b == 0:
        corr = 0.0
    else:
        corr = round(cov / (std_a * std_b), 2)

    if corr > 0.5:
        interpretation = "strong positive correlation"
    elif corr > 0.2:
        interpretation = "weak positive correlation"
    elif corr < -0.5:
        interpretation = "strong negative correlation"
    elif corr < -0.2:
        interpretation = "weak negative correlation"
    else:
        interpretation = "no significant correlation"

    return {
        "metric_a": metric_a,
        "metric_b": metric_b,
        "correlation": corr,
        "interpretation": interpretation,
        "data_points": n,
    }


def get_recent_raw(hours: int = 24) -> list[dict]:
    """Get all raw data points from the last N hours."""
    since = datetime.now(UTC) - timedelta(hours=hours)
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT d.*, c.name as metric, c.unit
            FROM health_data d
            JOIN metric_catalog c ON c.id = d.metric_id
            WHERE d.recorded_at >= %s
            ORDER BY d.recorded_at DESC
            """,
            (since,),
        ).fetchall()
    return rows
