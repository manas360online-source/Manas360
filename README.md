# Manas 360 Hospital Assistant (FastAPI)

An accessible hospital assistant backend designed for patients with disabilities.
Built with **FastAPI**, containerized with **Docker**, and ready for **CI/CD** integration.

## Features

- Patient profiles with disability-aware metadata
- Appointments linked to patients
- Accessibility-focused reminders (voice/sms/notification)
- Assistant summary endpoint that can be converted to speech
- Pytest-based automated tests
- Dockerfile ready for containerization

## Project Structure

```bash
mans360/
  app/
    __init__.py
    main.py          # FastAPI application
  tests/
    __init__.py
    test_health.py
    test_patient_flow.py
  Dockerfile
  requirements.txt
  README.md
  .github/
    workflows/
      deploy.yml     # CI workflow (tests + docker build)
```

## Running Locally (without Docker)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000/docs

## Running Tests

```bash
pytest
```

## Building and Running with Docker

```bash
docker build -t mans360:local .
docker run -p 8000:8000 mans360:local
```

Then open: http://127.0.0.1:8000/docs

## Notes for CI/CD

- The included GitHub Actions workflow (`.github/workflows/deploy.yml`) runs:
  - tests on each push / pull request
  - docker image build for the FastAPI app

- For a real deployment pipeline, you can extend the workflow to:
  - push images to AWS ECR
  - deploy to a Kubernetes cluster (e.g., AWS EKS) using `kubectl`.
