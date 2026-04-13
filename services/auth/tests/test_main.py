import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

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


def test_signup_returns_pending_verification_account_response():
    email = f"patient-{uuid4().hex}@example.com"
    password = "verysecurepass1"

    with patch("app.verification.generate_verification_code", return_value="123456"):
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
    assert response_data["status"] == "pending_verification"
    assert response_data["verification_code"] == "123456"


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
    email = f"Patient-{uuid4().hex}@Example.com"
    password = "verysecurepass1"

    with patch("app.verification.generate_verification_code", return_value="123456"):
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
            "email": email.casefold(),
            "password": password,
            "confirm_password": password,
        },
    )

    assert first_response.status_code == 201
    assert first_response.json()["email"] == email.casefold()
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Account with this email already exists",
    }


def test_signup_returns_generic_500_for_non_duplicate_integrity_errors():
    class FakeDiag:
        constraint_name = "email_verification_security_states_pkey"

    class FakeOrig(Exception):
        diag = FakeDiag()

    with patch(
        "app.main.create_account",
        side_effect=IntegrityError("insert", {}, FakeOrig()),
    ):
        response = client.post(
            "/signup",
            json={
                "email": f"patient-{uuid4().hex}@example.com",
                "password": "verysecurepass1",
                "confirm_password": "verysecurepass1",
            },
        )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Could not create account",
    }


def test_verify_email_activates_pending_account():
    email = f"patient-{uuid4().hex}@example.com"
    password = "verysecurepass1"

    with patch("app.verification.generate_verification_code", return_value="123456"):
        signup_response = client.post(
            "/signup",
            json={
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )

    assert signup_response.status_code == 201

    verify_response = client.post(
        "/verify-email",
        json={
            "email": email,
            "code": "123456",
        },
    )

    assert verify_response.status_code == 200
    assert verify_response.json()["email"] == email
    assert verify_response.json()["status"] == "active"


def test_verify_email_rejects_invalid_code():
    email = f"patient-{uuid4().hex}@example.com"
    password = "verysecurepass1"

    with patch("app.verification.generate_verification_code", return_value="123456"):
        signup_response = client.post(
            "/signup",
            json={
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )

    assert signup_response.status_code == 201

    verify_response = client.post(
        "/verify-email",
        json={
            "email": email,
            "code": "999999",
        },
    )

    assert verify_response.status_code == 400
    assert verify_response.json() == {
        "detail": "Verification code is invalid or expired",
    }


def test_resend_verification_returns_new_code_after_cooldown():
    email = f"patient-{uuid4().hex}@example.com"
    password = "verysecurepass1"

    with patch(
        "app.verification.generate_verification_code",
        side_effect=["123456", "654321"],
    ):
        signup_response = client.post(
            "/signup",
            json={
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )

        assert signup_response.status_code == 201

        future_now = datetime.now(timezone.utc) + timedelta(seconds=120)
        with patch("app.verification.utc_now", return_value=future_now):
            resend_response = client.post(
                "/verify-email/resend",
                json={"email": email},
            )

    assert resend_response.status_code == 200
    assert resend_response.json()["status"] == "pending_verification"
    assert resend_response.json()["verification_code"] == "654321"


def test_resend_verification_enforces_cooldown():
    email = f"patient-{uuid4().hex}@example.com"
    password = "verysecurepass1"

    with patch("app.verification.generate_verification_code", return_value="123456"):
        signup_response = client.post(
            "/signup",
            json={
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )

    assert signup_response.status_code == 201

    resend_response = client.post(
        "/verify-email/resend",
        json={"email": email},
    )

    assert resend_response.status_code == 429
    assert resend_response.json() == {
        "detail": "Verification resend is temporarily unavailable. Try again later.",
    }


def test_resend_verification_recovers_after_lock_expires():
    email = f"patient-{uuid4().hex}@example.com"
    password = "verysecurepass1"

    with patch(
        "app.verification.generate_verification_code",
        side_effect=["123456", "654321"],
    ):
        signup_response = client.post(
            "/signup",
            json={
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )

        assert signup_response.status_code == 201

        for _ in range(4):
            failed_response = client.post(
                "/verify-email",
                json={"email": email, "code": "999999"},
            )
            assert failed_response.status_code == 400

        locked_response = client.post(
            "/verify-email",
            json={"email": email, "code": "999999"},
        )
        assert locked_response.status_code == 429

        locked_resend = client.post(
            "/verify-email/resend",
            json={"email": email},
        )
        assert locked_resend.status_code == 429

        future_now = datetime.now(timezone.utc) + timedelta(minutes=16)
        with patch("app.verification.utc_now", return_value=future_now):
            resend_response = client.post(
                "/verify-email/resend",
                json={"email": email},
            )

    assert resend_response.status_code == 200
    assert resend_response.json()["verification_code"] == "654321"
