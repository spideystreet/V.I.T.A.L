"""Daily nudge detector: scans biometrics and decides whether to alert the user.

Run periodically (e.g. via cron). Triggers a notification only when stress
signals warrant attention — never on a schedule. The reward (Alan Play berries)
is granted only if the user accepts the nudge, so engagement tracks need, not
compliance.
"""

from dataclasses import dataclass

from backend.health_store import get_summary, get_trend

# Thresholds — keep aligned with brain.py system prompt
HRV_DROP_PCT = -15.0
SLEEP_MIN_HOURS = 6.0
RESTING_HR_MAX = 80.0


@dataclass
class NudgeDecision:
    should_nudge: bool
    reasons: list[str]
    headline: str

    def to_dict(self) -> dict:
        return {
            "should_nudge": self.should_nudge,
            "reasons": self.reasons,
            "headline": self.headline,
        }


def evaluate() -> NudgeDecision:
    """Decide whether to send a daily nudge based on the last 24h of data."""
    reasons: list[str] = []

    summary = get_summary(24)

    sleep = summary.get("sleep")
    if sleep and sleep["latest"] < SLEEP_MIN_HOURS:
        reasons.append(f"sommeil court ({sleep['latest']}h)")

    resting = summary.get("resting_hr")
    if resting and resting["avg"] > RESTING_HR_MAX:
        reasons.append(f"FC repos élevée ({resting['avg']} bpm)")

    hrv_trend = get_trend("hrv", days=7)
    if hrv_trend.get("change_pct") is not None and hrv_trend["change_pct"] <= HRV_DROP_PCT:
        reasons.append(f"HRV en baisse ({hrv_trend['change_pct']}%)")

    if not reasons:
        return NudgeDecision(
            should_nudge=False,
            reasons=[],
            headline="Tout est dans le vert, pas besoin de check aujourd'hui.",
        )

    headline = "V.I.T.A.L a remarqué un truc, 30 secondes ?"
    return NudgeDecision(should_nudge=True, reasons=reasons, headline=headline)


def main() -> None:
    """CLI entry: print the nudge decision as JSON for cron / shortcut hooks."""
    import json

    decision = evaluate()
    print(json.dumps(decision.to_dict(), ensure_ascii=False))


if __name__ == "__main__":
    main()
