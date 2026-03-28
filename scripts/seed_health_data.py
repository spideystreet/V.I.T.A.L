"""Seed the health database with realistic fake data for testing.

Simulates what the Apple Shortcut would POST over a 24h period.
Usage: uv run python scripts/seed_health_data.py [--url http://localhost:8420]
"""

import argparse
import random
from datetime import datetime, timedelta, timezone

import httpx


def generate_metrics(hours: int = 24) -> list[dict]:
    """Generate realistic health data for the last N hours."""
    now = datetime.now(timezone.utc)
    metrics = []

    for h in range(hours, 0, -1):
        ts = (now - timedelta(hours=h)).isoformat()

        # Heart rate — varies by time of day
        hour_of_day = (now - timedelta(hours=h)).hour
        if 0 <= hour_of_day < 6:  # sleeping
            hr = random.gauss(58, 4)
        elif 6 <= hour_of_day < 9:  # waking up
            hr = random.gauss(72, 6)
        elif 12 <= hour_of_day < 14:  # post-lunch
            hr = random.gauss(75, 5)
        else:
            hr = random.gauss(68, 8)
        metrics.append({"metric": "heart_rate", "value": round(hr, 1), "unit": "bpm", "recorded_at": ts})

        # SpO2 — mostly stable
        spo2 = random.gauss(97.5, 0.8)
        spo2 = max(92, min(100, spo2))
        metrics.append({"metric": "spo2", "value": round(spo2, 1), "unit": "%", "recorded_at": ts})

        # HRV — varies inversely with stress
        hrv = random.gauss(45, 12)
        hrv = max(10, hrv)
        metrics.append({"metric": "hrv", "value": round(hrv, 1), "unit": "ms", "recorded_at": ts})

    # Steps — hourly accumulation
    total_steps = 0
    for h in range(hours, 0, -1):
        ts = (now - timedelta(hours=h)).isoformat()
        hour_of_day = (now - timedelta(hours=h)).hour
        if 0 <= hour_of_day < 7:
            steps = random.randint(0, 20)
        elif 7 <= hour_of_day < 9:
            steps = random.randint(200, 800)
        elif 12 <= hour_of_day < 13:
            steps = random.randint(300, 1200)
        elif 17 <= hour_of_day < 19:
            steps = random.randint(500, 2000)
        else:
            steps = random.randint(50, 400)
        total_steps += steps
        metrics.append({"metric": "steps", "value": total_steps, "unit": "count", "recorded_at": ts})

    # Calories — correlates loosely with steps
    metrics.append({
        "metric": "calories",
        "value": round(total_steps * 0.04 + random.gauss(200, 30)),
        "unit": "kcal",
        "recorded_at": now.isoformat(),
    })

    # Resting heart rate — one daily reading
    metrics.append({
        "metric": "resting_heart_rate",
        "value": round(random.gauss(62, 3), 1),
        "unit": "bpm",
        "recorded_at": now.replace(hour=7, minute=0).isoformat(),
    })

    # Sleep — one entry for last night
    sleep_hours = round(random.gauss(7.2, 0.8), 1)
    sleep_hours = max(3.0, min(10.0, sleep_hours))
    metrics.append({
        "metric": "sleep",
        "value": sleep_hours,
        "unit": "hours",
        "recorded_at": now.replace(hour=7, minute=0).isoformat(),
    })

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Seed V.I.T.A.L with fake health data")
    parser.add_argument("--url", default="http://localhost:8420", help="Server base URL")
    parser.add_argument("--hours", type=int, default=24, help="Hours of data to generate")
    args = parser.parse_args()

    metrics = generate_metrics(args.hours)
    print(f"Generated {len(metrics)} data points over {args.hours}h")

    resp = httpx.post(f"{args.url}/health", json={"metrics": metrics})
    resp.raise_for_status()
    print(f"Server response: {resp.json()}")

    # Show summary
    summary = httpx.get(f"{args.url}/health/summary").json()
    print("\n--- Health Summary ---")
    for metric, stats in summary.items():
        unit = stats.get("unit") or ""
        print(f"  {metric}: latest={stats['latest']} {unit} (avg={stats['avg']}, range={stats['min']}–{stats['max']}, n={stats['count']})")


if __name__ == "__main__":
    main()
