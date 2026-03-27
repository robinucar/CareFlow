from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.password_policy import PasswordPolicyError
from app.schemas import AccountResponse, AccountSignupRequest
from app.signup import build_account_signup_response, create_account

app = FastAPI(title="CareFlow Auth Service")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "auth",
    }


@app.post("/signup", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
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
    return build_account_signup_response(account)
