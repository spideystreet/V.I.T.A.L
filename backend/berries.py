"""Alan Play berries: reward ledger for V.I.T.A.L engagement.

Berries are awarded for actions that reflect genuine engagement with the
burnout prevention loop, not raw activity. The schedule lives in BERRIES.
"""

from datetime import UTC, datetime, timedelta

from backend.health_store import _connect

# Action → berries earned. Only actions the server can independently verify
# are listed here. Each row notes the proof required before award() is called.
#
# - weekly_checkup        proof: conversation has ≥3 user turns + a score in
#                                the assistant's final message
# - daily_nudge_accepted  proof: a nudges row exists for today AND a
#                                conversation started within the response window
# - streak_4_weeks        proof: derived from berries_ledger itself
#                                (see weekly_checkup_streak)
BERRIES = {
    "weekly_checkup": 50,
    "daily_nudge_accepted": 5,
    "streak_4_weeks": 100,
}

_CREATE_BERRIES = """
CREATE TABLE IF NOT EXISTS berries_ledger (
    id SERIAL PRIMARY KEY,
    earned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    action TEXT NOT NULL,
    amount INTEGER NOT NULL,
    metadata JSONB
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_berries_action_date
ON berries_ledger (action, earned_at);
"""


def init_berries() -> None:
    """Create the berries ledger table."""
    with _connect() as conn:
        conn.execute(_CREATE_BERRIES)
        conn.execute(_CREATE_INDEX)


def award(action: str) -> int:
    """Record a berries award for an action. Returns berries granted."""
    if action not in BERRIES:
        raise ValueError(f"Unknown berries action: {action!r}")
    amount = BERRIES[action]
    with _connect() as conn:
        conn.execute(
            "INSERT INTO berries_ledger (action, amount) VALUES (%s, %s)",
            (action, amount),
        )
    return amount


def total() -> int:
    """Return the user's total berries balance."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM berries_ledger"
        ).fetchone()
    return int(row["total"])


def weekly_checkup_streak() -> int:
    """Count consecutive ISO weeks ending this week with a weekly_checkup award."""
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT date_trunc('week', earned_at) AS week
            FROM berries_ledger
            WHERE action = 'weekly_checkup'
            ORDER BY week DESC
            """
        ).fetchall()

    if not rows:
        return 0

    this_week = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    this_week -= timedelta(days=this_week.weekday())

    streak = 0
    expected = this_week
    for r in rows:
        week = r["week"]
        if week.date() == expected.date():
            streak += 1
            expected -= timedelta(days=7)
        else:
            break
    return streak
