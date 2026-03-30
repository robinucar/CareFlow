from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.identifiers import normalize_email
from app.models import EmailVerificationSecurityState, UserAccount
from app.password_policy import validate_password_policy
from app.schemas import (
    AccountResponse,
    AccountSignupRequest,
    AccountVerificationDeliveryResponse,
)
from app.security import hash_password
from app.verification import issue_email_verification_challenge


def create_account(
    db: Session,
    payload: AccountSignupRequest,
) -> tuple[UserAccount, str]:
    validate_password_policy(payload.password)
    now = datetime.now(timezone.utc)
    normalized_email = normalize_email(str(payload.email))

    account = UserAccount(
        email=normalized_email,
        password_hash=hash_password(payload.password),
        role="patient",
        status="pending_verification",
    )
    db.add(account)
    db.flush()

    security_state = EmailVerificationSecurityState(
        account_id=account.id,
        last_sent_at=now,
    )
    db.add(security_state)
    verification_code = issue_email_verification_challenge(
        db=db,
        account=account,
        security_state=security_state,
        now=now,
    )

    db.commit()
    db.refresh(account)
    return account, verification_code


def build_account_response(account: UserAccount) -> AccountResponse:
    return AccountResponse(
        id=str(account.id),
        email=account.email,
        role=account.role,
        status=account.status,
    )


def build_account_verification_delivery_response(
    account: UserAccount,
    verification_code: str,
) -> AccountVerificationDeliveryResponse:
    return AccountVerificationDeliveryResponse(
        id=str(account.id),
        email=account.email,
        role=account.role,
        status=account.status,
        verification_code=verification_code,
    )
