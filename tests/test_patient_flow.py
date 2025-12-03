from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_and_get_patient():
    # Create patient
    payload = {
        "name": "Test User",
        "age": 30,
        "disability_type": "Hearing impairment",
        "assistive_needs": ["vibration_alerts"],
    }
    create_resp = client.post("/patients", json=payload)
    assert create_resp.status_code == 200
    patient = create_resp.json()
    assert patient["name"] == payload["name"]
    assert patient["age"] == payload["age"]
    assert patient["disability_type"] == payload["disability_type"]

    # Get patient
    pid = patient["id"]
    get_resp = client.get(f"/patients/{pid}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == pid
    assert fetched["name"] == payload["name"]


def test_create_appointment_and_summary():
    # Create patient
    patient_resp = client.post(
        "/patients",
        json={"name": "Summary User", "age": 45, "assistive_needs": ["voice_instructions"]},
    )
    assert patient_resp.status_code == 200
    patient_id = patient_resp.json()["id"]

    # Create appointment
    appointment_payload = {
        "patient_id": patient_id,
        "doctor_name": "Dr. Test",
        "department": "Neurology",
        "date": "2025-12-03T10:30:00",
        "is_virtual": True,
    }
    app_resp = client.post("/appointments", json=appointment_payload)
    assert app_resp.status_code == 200

    # Create reminder
    reminder_payload = {
        "patient_id": patient_id,
        "message": "Time for test reminder",
        "reminder_time": "15:30:00",
        "channel": "voice",
    }
    rem_resp = client.post("/reminders", json=reminder_payload)
    assert rem_resp.status_code == 200

    # Get summary
    summary_resp = client.get(f"/assistant/summary/{patient_id}")
    assert summary_resp.status_code == 200
    data = summary_resp.json()
    assert data["patient_name"] == "Summary User"
    assert data["appointments_count"] >= 1
    assert data["reminders_count"] >= 1
    assert "Hello Summary User" in data["message"]
