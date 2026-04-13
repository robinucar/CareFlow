from pydantic import BaseModel, EmailStr, Field, model_validator


class AccountSignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=15, max_length=64)
    confirm_password: str = Field(min_length=15, max_length=64)

    @model_validator(mode="after")
    def passwords_match(self) -> "AccountSignupRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class EmailVerificationRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class EmailVerificationResendRequest(BaseModel):
    email: EmailStr


class AccountResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    status: str


class AccountVerificationDeliveryResponse(AccountResponse):
    verification_code: str
