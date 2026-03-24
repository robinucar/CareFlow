from pydantic import BaseModel, EmailStr


class PatientSignupRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class PatientResponse(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
