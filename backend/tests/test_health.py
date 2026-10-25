import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "health_check" in data


def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["environment"] == "development"
    assert data["database"]["status"] == "connected"
    assert data["database"]["engine"] == "PostgreSQL 16"
    assert isinstance(data["database"]["latency_ms"], (int, float))
    assert data["database"]["latency_ms"] >= 0
