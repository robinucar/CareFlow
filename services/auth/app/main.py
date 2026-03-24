from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI(title="CareFlow Auth Service")


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


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "auth",
    }


@app.post("/signup", response_model=PatientResponse, status_code=201)
def patient_signup(payload: PatientSignupRequest):
    return PatientResponse(
        id="pat_001",
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        role="patient",
    )
