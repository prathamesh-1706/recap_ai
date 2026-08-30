from tests.conftest import client


def test_health_endpoint():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "recap-api"}
