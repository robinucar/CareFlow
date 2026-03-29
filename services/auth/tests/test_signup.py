from app.models import UserAccount
from app.signup import build_account_response


def test_build_account_response_returns_account_response():
    account = UserAccount(
        id=1,
        email="patient@example.com",
        password_hash="hashed-password",
        role="patient",
        status="pending_verification",
    )

    response = build_account_response(account)

    assert response.id == "1"
    assert response.email == "patient@example.com"
    assert response.role == "patient"
    assert response.status == "pending_verification"
