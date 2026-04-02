# Docker for Python Services — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Containerize a minimal FastAPI app to learn Dockerfile anatomy, multi-stage builds, docker-compose, environment variables, and `.dockerignore`.

**Architecture:** A two-endpoint FastAPI app (`/health`, `/`) packaged in a multi-stage Docker image. Docker Compose orchestrates the single service with `APP_ENV=docker` injected as an environment variable. No automated tests — verification is manual via `curl`.

**Tech Stack:** Python 3.11, FastAPI, Uvicorn, Docker, Docker Compose

---

## File Structure

```
exercises/07-docker/
├── pyproject.toml          # project config + deps (fastapi, uvicorn)
├── src/
│   └── app.py              # minimal FastAPI app (2 endpoints)
├── Dockerfile              # multi-stage build (builder + runtime)
├── docker-compose.yml      # single service, port 8000, APP_ENV=docker
└── .dockerignore           # excludes __pycache__, .git, .env, .venv, *.pyc
```

---

### Task 1: Project Setup + FastAPI App

**Files:**
- Create: `exercises/07-docker/pyproject.toml`
- Create: `exercises/07-docker/src/app.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "docker-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["fastapi>=0.115.0", "uvicorn[standard]>=0.32.0"]
```

- [ ] **Step 2: Create the FastAPI app**

```python
# exercises/07-docker/src/app.py
import os
from fastapi import FastAPI

app = FastAPI(title="Dockerized API")


@app.get("/health")
def health():
    return {"status": "ok", "environment": os.getenv("APP_ENV", "development")}


@app.get("/")
def root():
    return {"message": "Hello from Docker!"}
```

- [ ] **Step 3: Verify locally (optional sanity check)**

```bash
cd C:/codebase/quant_lab/exercises/07-docker
pip install -e .
uvicorn src.app:app --port 8000
# In another terminal: curl http://localhost:8000/health
# Expected: {"status":"ok","environment":"development"}
# Stop uvicorn with Ctrl+C
```

---

### Task 2: Dockerfile (Multi-Stage)

**Files:**
- Create: `exercises/07-docker/Dockerfile`

- [ ] **Step 1: Create the Dockerfile**

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY src/ src/

EXPOSE 8000
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Notes:**
- Stage 1 installs dependencies in an isolated layer.
- Stage 2 copies only the installed packages and app code — no pip, no build cache.
- `--no-cache-dir` prevents pip from storing wheel files in the builder layer.

---

### Task 3: .dockerignore

**Files:**
- Create: `exercises/07-docker/.dockerignore`

- [ ] **Step 1: Create .dockerignore**

```
__pycache__
*.pyc
.git
.env
.venv
```

---

### Task 4: docker-compose.yml

**Files:**
- Create: `exercises/07-docker/docker-compose.yml`

- [ ] **Step 1: Create docker-compose.yml**

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=docker
    restart: unless-stopped
```

---

### Task 5: Build, Run, and Verify

- [ ] **Step 1: Build and start the container**

```bash
cd C:/codebase/quant_lab/exercises/07-docker
docker compose up --build -d
```

Expected: Image builds successfully, container starts in detached mode.

- [ ] **Step 2: Verify /health endpoint**

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok","environment":"docker"}`

The key check: `environment` is `"docker"` (from `APP_ENV=docker` in compose), not `"development"`.

- [ ] **Step 3: Verify / endpoint**

```bash
curl http://localhost:8000/
```

Expected: `{"message":"Hello from Docker!"}`

- [ ] **Step 4: Stop the container**

```bash
docker compose down
```

Expected: Container stops and is removed.

---

### Task 6: Commit

- [ ] **Step 1: Stage and commit all exercise files**

```bash
cd C:/codebase/quant_lab
git add exercises/07-docker/
git commit -m "feat(exercises): 07 Docker for FastAPI services"
```

---

### Task 7: Teaching Conversation

Cover these Docker concepts interactively:

- [ ] **Step 1: Why containers matter for financial services** — reproducibility, consistent environments, deployment confidence
- [ ] **Step 2: Dockerfile anatomy** — FROM, WORKDIR, COPY, RUN, CMD, EXPOSE and what each does
- [ ] **Step 3: Multi-stage builds** — why separate build and runtime, image size impact
- [ ] **Step 4: docker-compose** — orchestrating services, port mapping, env vars, restart policies
- [ ] **Step 5: .dockerignore** — what it excludes and why (security, size, speed)
- [ ] **Step 6: Volumes** — concept overview for persistent data (hands-on in Task 8 with PostgreSQL)
- [ ] **Step 7: Environment variables and secrets** — how they're injected, why not to hardcode secrets

---

### Task 8: Blog Post

**Files:**
- Create: blog post in `finbytes_git/docs/_posts/` (exact date TBD at write time)

- [ ] **Step 1: Write blog post**

Content sections:
1. **Installing Docker Desktop on Windows** — WSL 2 prerequisite (`wsl --install`), reboot, `winget install Docker.DockerDesktop`, reboot, verify with `docker --version` and `docker compose version`
2. **What is Docker and why use it** — containers vs VMs, reproducibility
3. **Building the app** — the minimal FastAPI app
4. **Writing the Dockerfile** — walkthrough of each line, explain multi-stage
5. **docker-compose** — what it adds, how to use it
6. **.dockerignore** — why and what to exclude
7. **Running it** — `docker compose up --build`, curl, verify

- [ ] **Step 2: Commit blog post**

```bash
cd C:/codebase/quant_lab
git add finbytes_git/docs/_posts/
git commit -m "docs(blog): 07 Docker for Python services"
```

- [ ] **Step 3: PR working -> master, merge, sync**

Follow standard workflow: create PR from `working` to `master`, merge, pull master, rebase working.
