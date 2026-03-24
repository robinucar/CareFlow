from app.schemas import PatientSignupRequest
from app.signup import build_patient_signup_response


def test_build_patient_signup_response_returns_patient_response():
    payload = PatientSignupRequest(
        email="patient@example.com",
        password="secret123",
        first_name="John",
        last_name="Doe",
    )

    response = build_patient_signup_response(payload)

    assert response.id == "pat_001"
    assert response.email == "patient@example.com"
    assert response.first_name == "John"
    assert response.last_name == "Doe"
    assert response.role == "patient"
