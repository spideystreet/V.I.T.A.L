"""Tests for health_server module."""

import pytest
from fastapi.testclient import TestClient

from vital.health_server import app
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
    from vital.health_store import init_db
    init_db()
    return db_file


class TestHealthServer:
    """Test health server endpoints."""

    def test_ping(self):
        """Test the ping endpoint."""
        client = TestClient(app)
        response = client.get("/health/ping")
        assert response.status_code == 200
        assert response.json() == {"status": "alive"}

    def test_receive_health_data_valid(self, tmp_db):
        """Test receiving valid health data."""
        client = TestClient(app)
        payload = {
            "metrics": [
                {
                    "metric": "heart_rate",
                    "value": 72.0,
                    "unit": "bpm",
                    "recorded_at": "2026-03-28T08:30:00Z",
                }
            ]
        }
        response = client.post("/health", json=payload)
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "inserted": 1}

    def test_receive_health_data_empty_metrics(self, tmp_db):
        """Test receiving health data with empty metrics list."""
        client = TestClient(app)
        payload = {"metrics": []}
        response = client.post("/health", json=payload)
        assert response.status_code == 400
        assert response.json() == {"detail": "No metrics provided"}

    def test_receive_health_data_malformed_payload(self, tmp_db):
        """Test receiving malformed payload."""
        client = TestClient(app)
        payload = {"invalid_key": "invalid_value"}
        response = client.post("/health", json=payload)
        assert response.status_code == 422

    def test_health_summary(self, tmp_db):
        """Test retrieving health summary."""
        client = TestClient(app)
        # Insert some data first
        payload = {
            "metrics": [
                {
                    "metric": "heart_rate",
                    "value": 72.0,
                    "unit": "bpm",
                    "recorded_at": "2026-03-28T08:30:00Z",
                }
            ]
        }
        client.post("/health", json=payload)
        # Retrieve summary
        response = client.get("/health/summary")
        assert response.status_code == 200
        assert "heart_rate" in response.json()
