from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "auth",
    }


def test_signup_returns_created_patient_response():
    response = client.post(
        "/signup",
        json={
            "email": "patient@example.com",
            "password": "secret123",
            "first_name": "John",
            "last_name": "Doe",
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": "pat_001",
        "email": "patient@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "patient",
    }


def test_signup_rejects_invalid_email():
    response = client.post(
        "/signup",
        json={
            "email": "not-an-email",
            "password": "secret123",
            "first_name": "John",
            "last_name": "Doe",
        },
    )
    assert response.status_code == 422
