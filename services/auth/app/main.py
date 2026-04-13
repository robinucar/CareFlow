from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.password_policy import PasswordPolicyError
from app.schemas import (
    AccountResponse,
    AccountSignupRequest,
    AccountVerificationDeliveryResponse,
    EmailVerificationRequest,
    EmailVerificationResendRequest,
)
from app.signup import (
    build_account_response,
    build_account_verification_delivery_response,
    create_account,
)
from app.verification import (
    AccountAlreadyVerifiedError,
    InvalidVerificationCodeError,
    VerificationLockedError,
    VerificationResendRateLimitedError,
    resend_account_verification_challenge,
    verify_account_email,
)

app = FastAPI(title="CareFlow Auth Service")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "auth",
    }


@app.post(
    "/signup",
    response_model=AccountVerificationDeliveryResponse,
    status_code=status.HTTP_201_CREATED,
)
def account_signup(
    payload: AccountSignupRequest,
    db: Session = Depends(get_db),
):
    try:
        account, verification_code = create_account(db, payload)
    except PasswordPolicyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        if is_duplicate_email_integrity_error(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account with this email already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create account",
        )
    return build_account_verification_delivery_response(account, verification_code)


@app.post("/verify-email", response_model=AccountResponse)
def verify_email(
    payload: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    try:
        account = verify_account_email(
            db=db,
            email=str(payload.email),
            code=payload.code,
        )
    except AccountAlreadyVerifiedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account is already verified",
        )
    except VerificationLockedError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed verification attempts. Try again later.",
        )
    except InvalidVerificationCodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code is invalid or expired",
        )

    return build_account_response(account)


@app.post(
    "/verify-email/resend",
    response_model=AccountVerificationDeliveryResponse,
)
def resend_verification_email(
    payload: EmailVerificationResendRequest,
    db: Session = Depends(get_db),
):
    try:
        account, verification_code = resend_account_verification_challenge(
            db=db,
            email=str(payload.email),
        )
    except AccountAlreadyVerifiedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account is already verified",
        )
    except (VerificationLockedError, VerificationResendRateLimitedError):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Verification resend is temporarily unavailable. Try again later.",
        )
    except InvalidVerificationCodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not eligible for verification resend",
        )

    return build_account_verification_delivery_response(account, verification_code)


def is_duplicate_email_integrity_error(exc: IntegrityError) -> bool:
    diag = getattr(exc.orig, "diag", None)
    constraint_name = getattr(diag, "constraint_name", None)
    return constraint_name == "user_accounts_email_key"
