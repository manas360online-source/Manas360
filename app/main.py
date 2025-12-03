from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, time
import uuid

app = FastAPI(
    title="Manas 360 Hospital Assistant",
    description=(
        "Accessible assistant API for patients with disabilities. "
        "Provides features like patient profiles, appointment management, "
        "and accessibility-focused reminders."
    ),
    version="1.0.0",
)

# In-memory "database" for demo / college project
patients_db = {}
appointments_db = {}
reminders_db = {}


# ---------- MODELS ----------

class Patient(BaseModel):
    id: str
    name: str = Field(..., example="Ravi Kumar")
    age: int = Field(..., ge=0, le=120, example=35)
    disability_type: Optional[str] = Field(
        None,
        example="Visual impairment",
        description="Type of disability to personalize assistance.",
    )
    assistive_needs: Optional[List[str]] = Field(
        default_factory=list,
        example=["voice_instructions", "wheelchair_navigation"],
        description="List of assistive features required by the patient.",
    )


class PatientCreate(BaseModel):
    name: str = Field(..., example="Ravi Kumar")
    age: int = Field(..., ge=0, le=120, example=35)
    disability_type: Optional[str] = Field(
        None,
        example="Visual impairment",
        description="Type of disability to personalize assistance.",
    )
    assistive_needs: Optional[List[str]] = Field(
        default_factory=list,
        example=["voice_instructions", "wheelchair_navigation"],
        description="List of assistive features required by the patient.",
    )


class Appointment(BaseModel):
    id: str
    patient_id: str
    doctor_name: str = Field(..., example="Dr. Mehta")
    department: str = Field(..., example="Orthopedics")
    date: datetime = Field(..., example="2025-12-03T10:30:00")
    is_virtual: bool = Field(
        False,
        description="If true, appointment is virtual and can be joined online.",
    )


class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_name: str = Field(..., example="Dr. Mehta")
    department: str = Field(..., example="Orthopedics")
    date: datetime = Field(..., example="2025-12-03T10:30:00")
    is_virtual: bool = Field(
        False,
        description="If true, appointment is virtual and can be joined online.",
    )


class Reminder(BaseModel):
    id: str
    patient_id: str
    message: str = Field(..., example="Time for physiotherapy session")
    reminder_time: time = Field(..., example="15:30:00")
    channel: str = Field(
        "voice",
        example="voice",
        description="voice / sms / notification. For accessibility, voice is default.",
    )


class ReminderCreate(BaseModel):
    patient_id: str
    message: str = Field(..., example="Time for physiotherapy session")
    reminder_time: time = Field(..., example="15:30:00")
    channel: str = Field(
        "voice",
        example="voice",
        description="voice / sms / notification. For accessibility, voice is default.",
    )


# ---------- BASIC ROUTES ----------

@app.get("/")
def root():
    """
    Simple welcome route so that visiting http://127.0.0.1:8000/ works
    instead of showing 404.
    """
    return {
        "message": "Welcome to Manas 360 Hospital Assistant API",
        "docs_url": "/docs",
        "health_url": "/health",
        "description": "Use /docs to explore and test all endpoints.",
    }


@app.get("/health", tags=["system"])
def health_check():
    """Simple health endpoint for uptime checks and CI tests."""
    return {"status": "ok", "service": "manas-360-assistant"}


# ---------- PATIENT ROUTES ----------

@app.post("/patients", response_model=Patient, tags=["patients"])
def create_patient(patient: PatientCreate):
    patient_id = str(uuid.uuid4())
    # pydantic v2 -> model_dump()
    new_patient = Patient(id=patient_id, **patient.model_dump())
    patients_db[patient_id] = new_patient
    return new_patient


@app.get("/patients", response_model=List[Patient], tags=["patients"])
def list_patients():
    return list(patients_db.values())


@app.get("/patients/{patient_id}", response_model=Patient, tags=["patients"])
def get_patient(patient_id: str):
    patient = patients_db.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# ---------- APPOINTMENT ROUTES ----------

@app.post("/appointments", response_model=Appointment, tags=["appointments"])
def create_appointment(appointment: AppointmentCreate):
    if appointment.patient_id not in patients_db:
        raise HTTPException(status_code=400, detail="Invalid patient_id")

    appointment_id = str(uuid.uuid4())
    new_appointment = Appointment(id=appointment_id, **appointment.model_dump())
    appointments_db[appointment_id] = new_appointment
    return new_appointment


@app.get(
    "/patients/{patient_id}/appointments",
    response_model=List[Appointment],
    tags=["appointments"],
)
def list_patient_appointments(patient_id: str):
    if patient_id not in patients_db:
            raise HTTPException(status_code=404, detail="Patient not found")

    return [a for a in appointments_db.values() if a.patient_id == patient_id]


# ---------- REMINDER (ACCESSIBILITY) ROUTES ----------

@app.post("/reminders", response_model=Reminder, tags=["accessibility"])
def create_reminder(reminder: ReminderCreate):
    if reminder.patient_id not in patients_db:
        raise HTTPException(status_code=400, detail="Invalid patient_id")

    reminder_id = str(uuid.uuid4())
    new_reminder = Reminder(id=reminder_id, **reminder.model_dump())
    reminders_db[reminder_id] = new_reminder
    return new_reminder


@app.get(
    "/patients/{patient_id}/reminders",
    response_model=List[Reminder],
    tags=["accessibility"],
)
def list_patient_reminders(patient_id: str):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    return [r for r in reminders_db.values() if r.patient_id == patient_id]


# ---------- ASSISTANT SUMMARY ROUTE ----------

@app.get(
    "/assistant/summary/{patient_id}",
    tags=["assistant"],
    summary="Accessibility-aware daily summary for a patient",
)
def assistant_summary(patient_id: str):
    """
    High-level summary that a voice assistant could read out to the patient.
    Designed for accessibility (can be converted to speech).
    """
    patient = patients_db.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appointments = [
        a for a in appointments_db.values() if a.patient_id == patient_id
    ]
    reminders = [r for r in reminders_db.values() if r.patient_id == patient_id]

    return {
        "patient_name": patient.name,
        "disability_type": patient.disability_type,
        "assistive_needs": patient.assistive_needs,
        "appointments_count": len(appointments),
        "reminders_count": len(reminders),
        "message": (
            f"Hello {patient.name}. You have {len(appointments)} appointments and "
            f"{len(reminders)} reminders scheduled. This summary can be converted "
            "to voice output for accessibility."
        ),
    }
