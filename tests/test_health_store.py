"""Tests for health_store module."""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from vital.config import DB_PATH, DATA_DIR


@pytest.fixture(autouse=True)
def tmp_db(monkeypatch, tmp_path):
    """Override DB_PATH and DATA_DIR to use a temporary database."""
    db_file = tmp_path / "test_health.db"
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)
    monkeypatch.setattr("vital.config.DB_PATH", str(db_file))
    monkeypatch.setattr("vital.config.DATA_DIR", data_dir)
    # Re-import the module to ensure the new paths are used
    import importlib
    import sys
    if 'vital.health_store' in sys.modules:
        importlib.reload(sys.modules['vital.health_store'])
    from vital.health_store import init_db, insert_metrics, get_latest, get_summary, get_recent_raw
    init_db()
    return db_file


class TestInitDB:
    """Test database initialization."""

    def test_init_db_creates_table(self, tmp_db):
        """Test that init_db creates the health_data table."""
        with sqlite3.connect(tmp_db) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='health_data'"
            )
            assert cursor.fetchone() is not None

    def test_init_db_creates_index(self, tmp_db):
        """Test that init_db creates the idx_health_metric_date index."""
        with sqlite3.connect(tmp_db) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_health_metric_date'"
            )
            assert cursor.fetchone() is not None


class TestInsertMetrics:
    """Test metric insertion."""

    def test_insert_metrics_single(self, tmp_db):
        from vital.health_store import insert_metrics
        """Test inserting a single metric."""
        metrics = [
            {
                "metric": "heart_rate",
                "value": 72.0,
                "unit": "bpm",
                "recorded_at": "2026-03-28T08:30:00Z",
            }
        ]
        count = insert_metrics(metrics)
        assert count == 1

        with sqlite3.connect(tmp_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM health_data")
            assert cursor.fetchone()[0] == 1

    def test_insert_metrics_batch(self, tmp_db):
        """Test inserting multiple metrics."""
        from vital.health_store import insert_metrics
        metrics = [
            {
                "metric": "heart_rate",
                "value": 72.0,
                "unit": "bpm",
                "recorded_at": "2026-03-28T08:30:00Z",
            },
            {
                "metric": "spo2",
                "value": 98.0,
                "unit": "%",
                "recorded_at": "2026-03-28T08:35:00Z",
            },
        ]
        count = insert_metrics(metrics)
        assert count == 2

        with sqlite3.connect(tmp_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM health_data")
            assert cursor.fetchone()[0] == 2

    def test_insert_metrics_with_metadata(self, tmp_db):
        """Test inserting metrics with metadata."""
        from vital.health_store import insert_metrics
        metrics = [
            {
                "metric": "heart_rate",
                "value": 72.0,
                "unit": "bpm",
                "recorded_at": "2026-03-28T08:30:00Z",
                "metadata": {"device": "apple_watch"},
            }
        ]
        insert_metrics(metrics)

        with sqlite3.connect(tmp_db) as conn:
            cursor = conn.execute("SELECT metadata FROM health_data")
            result = cursor.fetchone()[0]
            assert json.loads(result) == {"device": "apple_watch"}

    def test_insert_metrics_missing_fields(self, tmp_db):
        """Test inserting metrics with missing fields."""
        from vital.health_store import insert_metrics
        metrics = [
            {
                "metric": "heart_rate",
                "value": 72.0,
                # Missing unit and recorded_at
            }
        ]
        with pytest.raises(KeyError):
            insert_metrics(metrics)


class TestGetLatest:
    """Test retrieving the latest metrics."""

    def test_get_latest_single(self, tmp_db):
        """Test retrieving the latest metric."""
        from vital.health_store import insert_metrics, get_latest
        metrics = [
            {
                "metric": "heart_rate",
                "value": 72.0,
                "unit": "bpm",
                "recorded_at": "2026-03-28T08:30:00Z",
            }
        ]
        insert_metrics(metrics)
        result = get_latest("heart_rate")
        assert len(result) == 1
        assert result[0]["value"] == 72.0

    def test_get_latest_multiple(self, tmp_db):
        """Test retrieving multiple latest metrics."""
        from vital.health_store import insert_metrics, get_latest
        metrics = [
            {
                "metric": "heart_rate",
                "value": 72.0,
                "unit": "bpm",
                "recorded_at": "2026-03-28T08:30:00Z",
            },
            {
                "metric": "heart_rate",
                "value": 75.0,
                "unit": "bpm",
                "recorded_at": "2026-03-28T09:30:00Z",
            },
        ]
        insert_metrics(metrics)
        result = get_latest("heart_rate", limit=2)
        assert len(result) == 2
        assert result[0]["value"] == 75.0
        assert result[1]["value"] == 72.0

    def test_get_latest_empty_db(self, tmp_db):
        """Test retrieving latest metrics from an empty database."""
        from vital.health_store import get_latest
        result = get_latest("heart_rate")
        assert len(result) == 0


class TestGetSummary:
    """Test retrieving summary statistics."""

    def test_get_summary_single_metric(self, tmp_db):
        """Test retrieving summary for a single metric."""
        from vital.health_store import insert_metrics, get_summary
        now = datetime.now(timezone.utc)
        metrics = [
            {
                "metric": "heart_rate",
                "value": 72.0,
                "unit": "bpm",
                "recorded_at": (now - timedelta(hours=1)).isoformat(),
            },
            {
                "metric": "heart_rate",
                "value": 75.0,
                "unit": "bpm",
                "recorded_at": (now - timedelta(hours=2)).isoformat(),
            },
        ]
        insert_metrics(metrics)
        summary = get_summary(hours=24)
        assert "heart_rate" in summary
        assert summary["heart_rate"]["avg"] == 73.5

    def test_get_summary_multiple_metrics(self, tmp_db):
        """Test retrieving summary for multiple metrics."""
        from vital.health_store import insert_metrics, get_summary
        now = datetime.now(timezone.utc)
        metrics = [
            {
                "metric": "heart_rate",
                "value": 72.0,
                "unit": "bpm",
                "recorded_at": (now - timedelta(hours=1)).isoformat(),
            },
            {
                "metric": "spo2",
                "value": 98.0,
                "unit": "%",
                "recorded_at": (now - timedelta(hours=1)).isoformat(),
            },
        ]
        insert_metrics(metrics)
        summary = get_summary(hours=24)
        assert "heart_rate" in summary
        assert "spo2" in summary

    def test_get_summary_empty_db(self, tmp_db):
        """Test retrieving summary from an empty database."""
        from vital.health_store import get_summary
        summary = get_summary(hours=24)
        assert len(summary) == 0


class TestGetRecentRaw:
    """Test retrieving recent raw data."""

    def test_get_recent_raw_single(self, tmp_db):
        """Test retrieving recent raw data for a single metric."""
        from vital.health_store import insert_metrics, get_recent_raw
        now = datetime.now(timezone.utc)
        metrics = [
            {
                "metric": "heart_rate",
                "value": 72.0,
                "unit": "bpm",
                "recorded_at": (now - timedelta(hours=1)).isoformat(),
            }
        ]
        insert_metrics(metrics)
        result = get_recent_raw(hours=24)
        assert len(result) == 1
        assert result[0]["metric"] == "heart_rate"

    def test_get_recent_raw_multiple(self, tmp_db):
        """Test retrieving recent raw data for multiple metrics."""
        from vital.health_store import insert_metrics, get_recent_raw
        now = datetime.now(timezone.utc)
        metrics = [
            {
                "metric": "heart_rate",
                "value": 72.0,
                "unit": "bpm",
                "recorded_at": (now - timedelta(hours=1)).isoformat(),
            },
            {
                "metric": "spo2",
                "value": 98.0,
                "unit": "%",
                "recorded_at": (now - timedelta(hours=1)).isoformat(),
            },
        ]
        insert_metrics(metrics)
        result = get_recent_raw(hours=24)
        assert len(result) == 2

    def test_get_recent_raw_empty_db(self, tmp_db):
        """Test retrieving recent raw data from an empty database."""
        from vital.health_store import get_recent_raw
        result = get_recent_raw(hours=24)
        assert len(result) == 0
