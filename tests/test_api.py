# Unit tests for FastAPI health and admin auth.
from unittest.mock import patch

from fastapi.testclient import TestClient

from stellarhydra.api.main import app
from stellarhydra.config import get_settings
from stellarhydra.models.predictions import CycleResult


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "components" in body


def test_admin_requires_api_key():
    client = TestClient(app)
    response = client.post("/admin/cycle/trigger")
    assert response.status_code == 401


def test_metrics_endpoint_exposes_prometheus_counters():
    client = TestClient(app)
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"hydra_http_requests_total" in response.content


def test_admin_with_valid_key():
    settings = get_settings()
    client = TestClient(app)
    mock_result = CycleResult(cycle_id="x", execution_status="dry_run")

    with patch("stellarhydra.api.main.run_cycle", return_value=mock_result):
        response = client.post(
            "/admin/cycle/trigger",
            headers={"X-API-Key": settings.hydra_admin_api_key},
        )
    assert response.status_code == 200
