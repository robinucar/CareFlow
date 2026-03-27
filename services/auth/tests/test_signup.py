from app.models import UserAccount
from app.signup import build_account_signup_response


def test_build_account_signup_response_returns_account_response():
    account = UserAccount(
        id=1,
        email="patient@example.com",
        password_hash="hashed-password",
        role="patient",
        status="active",
    )

    response = build_account_signup_response(account)

    assert response.id == "1"
    assert response.email == "patient@example.com"
    assert response.role == "patient"
