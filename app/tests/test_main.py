from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_papers_endpoint():
    response = client.get("/api/v1/papers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "title" in data[0]
