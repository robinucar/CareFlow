from sqlalchemy.orm import Session

from app.models import UserAccount
from app.password_policy import validate_password_policy
from app.schemas import AccountResponse, AccountSignupRequest
from app.security import hash_password


def create_account(db: Session, payload: AccountSignupRequest) -> UserAccount:
    validate_password_policy(payload.password)

    account = UserAccount(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="patient",
        status="active",
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def build_account_signup_response(account: UserAccount) -> AccountResponse:
    return AccountResponse(
        id=str(account.id),
        email=account.email,
        role=account.role,
    )
