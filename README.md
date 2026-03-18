# CareFlow

CareFlow is a portfolio-focused outpatient clinic workflow platform designed to demonstrate strong backend, frontend, and system design skills through a realistic healthcare product.

The project is being built step by step to balance two goals:

1. build a real software system with credible engineering decisions
2. learn and explain those decisions clearly in interviews

## Current Status

CareFlow is currently in the planning and architecture definition stage.

The project scope, MVP, delivery phases, and service boundaries are being defined before implementation begins.

## Product Definition

CareFlow is an outpatient clinic workflow platform that helps patients and staff move through the care journey in one place: secure access, patient records, doctor availability, appointments, triage, lab orders and results, notifications, and a traceable history of care activity.

The goal is to reduce manual coordination and make the patient journey visible from first contact to follow-up.

## Project Goals

This project is intended to help demonstrate and learn:

- FastAPI
- Python backend architecture
- SQLAlchemy ORM
- Alembic migrations
- PostgreSQL
- microservices architecture
- database per service
- event-driven architecture
- RabbitMQ
- idempotency for APIs and event consumers
- Docker and Docker Compose
- automated testing
- CI/CD with GitHub Actions
- React frontend with Vite
- TanStack Query
- Zustand
- React Hook Form
- Zod
- Tailwind CSS
- Playwright
- system design thinking

## Core Domain Areas

- auth
- patients
- doctors
- appointments
- triage
- labs
- notifications
- timeline
- audit

## User Types

- Patient
- Front Desk / Scheduler
- Triage Nurse
- Doctor
- Lab Staff
- Clinic Admin

## Timeline vs Audit

### Timeline

Timeline is the patient-centered operational history of care events such as appointment booked, checked in, triaged, lab ordered, and result released.

Its purpose is to support care delivery and operational visibility.

### Audit

Audit is the security and compliance history of sensitive access and change such as who viewed a record, who changed demographics, who changed a role, when they did it, and what changed.

Its purpose is to support accountability, investigation, and compliance.

## Story Labels

- `[MVP]` must-have for the first usable version
- `[After MVP]` important next capability after the MVP
- `[Maturity]` later operational or compliance-oriented capability

## User Stories

### Auth

- `AUTH-01 [MVP]` As a patient, I want to create an account so I can access my care information and appointments.
- `AUTH-02 [MVP]` As a patient or staff user, I want to sign in securely so I can access the parts of the system relevant to me.
- `AUTH-03 [MVP]` As a clinic admin, I want to create staff accounts and assign roles so the right people can use the system.
- `AUTH-04 [Maturity]` As a clinic admin, I want to disable or restore staff access so the system reflects staffing changes safely.

### Patients

- `PAT-01 [After MVP]` As a patient, I want to update my contact details so the clinic can keep my record current.
- `PAT-02 [MVP]` As front desk staff, I want to register a new patient so first-time visitors can enter the clinic workflow.
- `PAT-03 [MVP]` As front desk staff, I want to search for and verify an existing patient so I can avoid duplicate records and use the correct chart.
- `PAT-04 [MVP]` As a doctor, I want to view a patient summary so I can prepare for the visit quickly.

### Doctors

- `DOC-00 [MVP]` As a clinic admin or front desk staff, I want to create and maintain basic doctor profiles, specialties, and availability so appointments can be booked correctly.
- `DOC-01 [MVP]` As front desk staff, I want to see doctor specialties and availability so I can book the right clinician.
- `DOC-02 [After MVP]` As a doctor, I want to update my own availability so my schedule stays accurate without staff mediation.
- `DOC-03 [After MVP]` As a clinic admin, I want to manage doctor roster details such as active status, clinic assignment, and specialty changes so scheduling data stays reliable over time.

### Appointments

- `APPT-01 [MVP]` As a patient, I want to book, reschedule, or cancel an appointment so I can manage my visit.
- `APPT-02 [MVP]` As front desk staff, I want to create or change appointments on a patient’s behalf so I can support phone and walk-in scheduling.
- `APPT-03 [MVP]` As front desk staff, I want to check patients in and update visit status so the clinic knows where each appointment stands.
- `APPT-04 [After MVP]` As a triage nurse, I want to recommend or trigger the next appointment step so urgent patients are routed correctly.
- `APPT-05 [MVP]` As a doctor, I want to see my daily schedule so I can prepare for visits.

### Triage

- `TRI-01 [MVP]` As a patient, I want to submit symptoms and intake details before my visit so the clinic can prepare and prioritize care.
- `TRI-02 [MVP]` As a triage nurse, I want to review submitted symptoms and intake details so I can assess urgency.
- `TRI-03 [MVP]` As a triage nurse, I want to assign a triage outcome so the patient can be routed appropriately.
- `TRI-04 [MVP]` As a doctor, I want to review triage notes before the appointment so I start with the right context.

### Labs

- `LAB-01 [After MVP]` As a doctor, I want to order lab tests so I can request follow-up diagnostics.
- `LAB-02 [After MVP]` As lab staff, I want to see pending lab orders so I know what to process.
- `LAB-03 [After MVP]` As lab staff, I want to update lab order status so the clinic can track progress.
- `LAB-04 [After MVP]` As a doctor, I want to review lab results so I can make informed care decisions.
- `LAB-05 [After MVP]` As a patient, I want to view released lab results so I can understand my next steps.
- `LAB-06 [After MVP]` As lab staff, I want to record lab results against the correct order so doctors can review them safely.

### Notifications

- `NOTIF-01 [MVP]` As a patient, I want to receive appointment confirmations and reminders so I know when to attend.
- `NOTIF-02 [MVP]` As a patient, I want to receive schedule change updates so I am not surprised by changes.
- `NOTIF-03 [After MVP]` As a patient, I want to receive triage and lab status updates so I know the next step in my care journey.

### Timeline

- `TIM-01 [After MVP]` As a clinician, I want to see a patient-centered care timeline so I can understand what has happened across appointments, triage, and labs.
- `TIM-02 [After MVP]` As front desk staff, I want to see recent care milestones so I can answer patient status questions accurately.
- `TIM-03 [Maturity]` As a patient, I want to see selected care milestones so I can follow my care journey.

### Audit

- `AUD-01 [Maturity]` As a clinic admin, I want to review who changed sensitive patient, appointment, or lab data so I can investigate mistakes or misuse.
- `AUD-02 [Maturity]` As a clinic admin, I want to review who accessed sensitive records so I can support compliance and incident response.
- `AUD-03 [Maturity]` As a clinic admin, I want role and permission changes to be auditable so administrative actions can be traced.

### System-Level Stories

- `SYS-01 [MVP]` As the system, I want critical write operations such as patient registration, appointment booking, and visit check-in to be idempotent so retries do not create duplicate records.
- `SYS-02 [After MVP]` As the system, I want event consumers to detect and ignore duplicate event deliveries so downstream services do not apply the same change twice.
- `SYS-03 [MVP]` As a clinic admin, I want role-based access control enforced across the product so each user can only perform actions allowed for their role.
- `SYS-04 [After MVP]` As a clinic admin, I want sensitive changes to capture actor, timestamp, and before/after details so important changes can be investigated.
- `SYS-05 [MVP]` As care staff, I want major care events such as appointment creation, check-in, triage outcome, and cancellation to be traceable in the system so the patient journey can be followed reliably.
- `SYS-06 [Maturity]` As a clinic admin, I want sensitive record access to be auditable separately from workflow history so compliance review does not depend on the care timeline.

## Small MVP Scope

The initial MVP is intentionally focused on one believable outpatient workflow.

Included MVP stories:

- `AUTH-01`, `AUTH-02`, `AUTH-03`
- `PAT-02`, `PAT-03`, `PAT-04`
- `DOC-00`, `DOC-01`
- `APPT-01`, `APPT-02`, `APPT-03`, `APPT-05`
- `TRI-01`, `TRI-02`, `TRI-03`, `TRI-04`
- `NOTIF-01`, `NOTIF-02`
- `SYS-01`, `SYS-03`, `SYS-05`

This MVP gives the project:

- secure access
- patient registration and lookup
- clinic-managed doctor availability
- appointment booking and visit status
- symptom intake and triage
- patient notifications
- traceable major care events

## Planned Service Direction

The current target service set is:

### MVP-oriented services

- Auth Service
- Patient Service
- Scheduling Service
- Triage Service
- Notification Service
- Timeline Service

### Later services

- Labs Service
- Audit Service

This boundary design may evolve, but each service is expected to own its own data and business rules.

## Guiding Principles

- build step by step
- teach new technologies before using them
- keep architecture realistic and interview-friendly
- avoid over-engineering too early
- favor clear service boundaries
- keep critical writes idempotent
- use asynchronous events where side effects and projections make sense

## Portfolio Intent

CareFlow is meant to be more than a feature demo.

By the end of the project, it should demonstrate:

- realistic domain modeling
- clear service boundaries
- one database per service
- sync and async communication patterns
- API and consumer idempotency
- automated testing
- containerized local development
- CI/CD
- frontend architecture with modern React tooling
- strong documentation and interview readiness
