from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.password_policy import PasswordPolicyError
from app.schemas import AccountResponse, AccountSignupRequest, EmailVerificationRequest
from app.signup import build_account_response, create_account
from app.verification import (
    AccountAlreadyVerifiedError,
    InvalidVerificationCodeError,
    VerificationLockedError,
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
    "/signup", response_model=AccountResponse, status_code=status.HTTP_201_CREATED
)
def account_signup(
    payload: AccountSignupRequest,
    db: Session = Depends(get_db),
):
    try:
        account = create_account(db, payload)
    except PasswordPolicyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account with this email already exists",
        )
    return build_account_response(account)


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
