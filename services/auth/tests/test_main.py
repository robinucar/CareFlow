import os
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://careflow:careflow@localhost:55432/careflow_auth",
)

client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "auth",
    }


def test_signup_returns_created_account_response():
    email = f"patient-{uuid4().hex}@example.com"
    password = "verysecurepass1"
    response = client.post(
        "/signup",
        json={
            "email": email,
            "password": password,
            "confirm_password": password,
        },
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["id"].isdigit()
    assert response_data["email"] == email
    assert response_data["role"] == "patient"


def test_signup_rejects_invalid_email():
    response = client.post(
        "/signup",
        json={
            "email": "not-an-email",
            "password": "verysecurepass1",
            "confirm_password": "verysecurepass1",
        },
    )
    assert response.status_code == 422


def test_signup_rejects_password_mismatch():
    response = client.post(
        "/signup",
        json={
            "email": f"patient-{uuid4().hex}@example.com",
            "password": "verysecurepass1",
            "confirm_password": "verysecurepass2",
        },
    )

    assert response.status_code == 422


def test_signup_rejects_short_password():
    response = client.post(
        "/signup",
        json={
            "email": f"patient-{uuid4().hex}@example.com",
            "password": "shortpass",
            "confirm_password": "shortpass",
        },
    )

    assert response.status_code == 422


def test_signup_rejects_common_password():
    response = client.post(
        "/signup",
        json={
            "email": f"patient-{uuid4().hex}@example.com",
            "password": "Password1234567",
            "confirm_password": "Password1234567",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Password is too common",
    }


def test_signup_rejects_duplicate_email():
    email = f"patient-{uuid4().hex}@example.com"
    password = "verysecurepass1"

    first_response = client.post(
        "/signup",
        json={
            "email": email,
            "password": password,
            "confirm_password": password,
        },
    )
    second_response = client.post(
        "/signup",
        json={
            "email": email,
            "password": password,
            "confirm_password": password,
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Account with this email already exists",
    }
