from app.schemas import PatientResponse, PatientSignupRequest


def build_patient_signup_response(payload: PatientSignupRequest) -> PatientResponse:
    return PatientResponse(
        id="pat_001",
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        role="patient",
    )
