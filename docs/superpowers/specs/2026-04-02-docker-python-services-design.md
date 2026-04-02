# Task 7: Docker for Python Services — Design Spec

**Date:** 2026-04-02
**Exercise:** `exercises/07-docker/`
**Concept:** Containerize a minimal FastAPI app. Learn Dockerfile anatomy, multi-stage builds, docker-compose, environment variables, and `.dockerignore`.

---

## App: Minimal FastAPI

Two endpoints, no external dependencies beyond FastAPI + Uvicorn.

### Endpoints

| Route | Method | Response | Notes |
|-------|--------|----------|-------|
| `/health` | GET | `{"status": "ok", "environment": "<APP_ENV>"}` | `APP_ENV` from env var, defaults to `"development"` |
| `/` | GET | `{"message": "Hello from Docker!"}` | Simple root |

### Dependencies

| Package | Version |
|---------|---------|
| fastapi | >=0.115.0 |
| uvicorn[standard] | >=0.32.0 |

Python version: 3.11 (matches local 3.11.9)

---

## Dockerfile (Multi-Stage)

### Stage 1: Builder
- Base: `python:3.11-slim`
- Copies `pyproject.toml`, installs dependencies
- Purpose: isolate dependency installation

### Stage 2: Runtime
- Base: `python:3.11-slim`
- Copies installed packages + `uvicorn` binary from builder
- Copies `src/` application code
- Exposes port 8000
- CMD: `uvicorn app:app --host 0.0.0.0 --port 8000`

**Why multi-stage:** Final image contains only runtime dependencies + app code. No build tools, no pip cache — smaller and more secure.

---

## docker-compose.yml

Single service configuration:

| Key | Value | Notes |
|-----|-------|-------|
| build | `.` | Builds from local Dockerfile |
| ports | `8000:8000` | Maps container port to host |
| environment | `APP_ENV=docker` | Injected into container |
| restart | `unless-stopped` | Auto-restart on failure |

---

## .dockerignore

Excludes from build context:

```
__pycache__
*.pyc
.git
.env
.venv
```

**Why:** Faster builds (less data sent to Docker daemon), smaller images, no secrets leaked into the image.

---

## Files to Create

| File | Purpose |
|------|---------|
| `exercises/07-docker/pyproject.toml` | Project metadata + dependencies |
| `exercises/07-docker/src/app.py` | FastAPI application |
| `exercises/07-docker/Dockerfile` | Multi-stage container build |
| `exercises/07-docker/docker-compose.yml` | Service orchestration |
| `exercises/07-docker/.dockerignore` | Build context exclusions |

---

## Verification

```bash
cd exercises/07-docker
docker compose up --build -d
curl http://localhost:8000/health
# Expected: {"status":"ok","environment":"docker"}
curl http://localhost:8000/
# Expected: {"message":"Hello from Docker!"}
docker compose down
```

---

## Blog Post Additions

- Include a section on installing Docker Desktop on Windows (WSL 2 prerequisite, `winget install Docker.DockerDesktop`, restart steps)
- Windows-only for now

---

## Out of Scope

- Volume mounts (covered in Task 8 with PostgreSQL)
- Live reload / dev mode
- Automated tests (verification is manual via curl)
- Multi-service compose (covered in Task 8)
- Mac/Linux install instructions
