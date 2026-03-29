from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.identifiers import normalize_email
from app.models import (
    EmailVerificationChallenge,
    EmailVerificationSecurityState,
    UserAccount,
)
from app.security import (
    generate_verification_code,
    hash_verification_code,
    verify_verification_code,
)

VERIFICATION_CODE_EXPIRY_MINUTES = 10
MAX_FAILED_VERIFY_ATTEMPTS = 5
VERIFY_LOCK_MINUTES = 15


class VerificationError(Exception):
    pass


class InvalidVerificationCodeError(VerificationError):
    pass


class VerificationLockedError(VerificationError):
    def __init__(self, locked_until: datetime):
        self.locked_until = locked_until
        super().__init__("Verification is temporarily locked")


class AccountAlreadyVerifiedError(VerificationError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def issue_email_verification_challenge(
    db: Session,
    account: UserAccount,
    security_state: EmailVerificationSecurityState,
    now: datetime | None = None,
) -> str:
    current_time = now or utc_now()
    open_challenge = get_open_verification_challenge(db, account.id)
    if open_challenge is not None:
        open_challenge.revoked_at = current_time

    code = generate_verification_code()
    challenge = EmailVerificationChallenge(
        account_id=account.id,
        code_hash=hash_verification_code(code),
        expires_at=current_time + timedelta(minutes=VERIFICATION_CODE_EXPIRY_MINUTES),
    )
    db.add(challenge)

    security_state.last_sent_at = current_time
    return code


def verify_account_email(
    db: Session,
    email: str,
    code: str,
    now: datetime | None = None,
) -> UserAccount:
    current_time = now or utc_now()
    normalized_email = normalize_email(email)

    account = db.scalar(
        select(UserAccount).where(UserAccount.email == normalized_email)
    )
    if account is None:
        raise InvalidVerificationCodeError

    if account.status == "active":
        raise AccountAlreadyVerifiedError

    security_state = db.get(EmailVerificationSecurityState, account.id)
    if security_state is None:
        raise InvalidVerificationCodeError

    reset_verification_lock_if_elapsed(security_state, current_time)

    if (
        security_state.locked_until is not None
        and security_state.locked_until > current_time
    ):
        raise VerificationLockedError(security_state.locked_until)

    challenge = get_open_verification_challenge(db, account.id)
    if challenge is None:
        raise InvalidVerificationCodeError

    if challenge.expires_at <= current_time:
        challenge.revoked_at = current_time
        db.commit()
        raise InvalidVerificationCodeError

    if not verify_verification_code(code, challenge.code_hash):
        if security_state.failed_attempt_count == 0:
            security_state.failed_attempt_window_started_at = current_time

        security_state.failed_attempt_count += 1

        if security_state.failed_attempt_count >= MAX_FAILED_VERIFY_ATTEMPTS:
            security_state.locked_until = current_time + timedelta(
                minutes=VERIFY_LOCK_MINUTES
            )
            challenge.revoked_at = current_time
            db.commit()
            raise VerificationLockedError(security_state.locked_until)

        db.commit()
        raise InvalidVerificationCodeError

    challenge.used_at = current_time
    account.status = "active"
    security_state.failed_attempt_count = 0
    security_state.failed_attempt_window_started_at = None
    security_state.locked_until = None

    db.commit()
    db.refresh(account)
    return account


def get_open_verification_challenge(
    db: Session,
    account_id: int,
) -> EmailVerificationChallenge | None:
    statement = (
        select(EmailVerificationChallenge)
        .where(EmailVerificationChallenge.account_id == account_id)
        .where(EmailVerificationChallenge.used_at.is_(None))
        .where(EmailVerificationChallenge.revoked_at.is_(None))
        .order_by(EmailVerificationChallenge.created_at.desc())
    )
    return db.scalar(statement)


def reset_verification_lock_if_elapsed(
    security_state: EmailVerificationSecurityState,
    now: datetime,
) -> None:
    if security_state.locked_until is None:
        return

    if security_state.locked_until <= now:
        security_state.locked_until = None
        security_state.failed_attempt_count = 0
        security_state.failed_attempt_window_started_at = None
