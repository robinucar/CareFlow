from fastapi import FastAPI
from app.schemas import PatientResponse, PatientSignupRequest
from app.signup import build_patient_signup_response

app = FastAPI(title="CareFlow Auth Service")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "auth",
    }


@app.post("/signup", response_model=PatientResponse, status_code=201)
def patient_signup(payload: PatientSignupRequest):
    return build_patient_signup_response(payload)
