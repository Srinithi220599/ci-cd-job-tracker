# CI/CD Job Tracker (Containerized)

Interview-focused revision notes for a simple CI/CD job tracking platform built with Flask + PostgreSQL and run using Docker Compose.

## 1. Project Goal

This project tracks CI/CD jobs (build/deploy/test runs) and exposes APIs to:

- Add a new job record
- List all jobs
- Get job statistics (success/failure rate)
- Check app health

## 2. Tech Stack

- Python 3.11 (Flask)
- PostgreSQL 15
- SQLAlchemy / Flask-SQLAlchemy
- Docker + Docker Compose

## 3. Architecture (Quick View)

- `app` service: Flask API, listens on port `5000`
- `db` service: PostgreSQL, listens on port `5432`
- Persistent volume: `postgres_data` keeps DB data across restarts

Flow:

1. Docker Compose starts `db` and `app`.
2. Flask app uses `DATABASE_URL` to connect to PostgreSQL.
3. On startup, the app creates tables automatically.
4. APIs read/write job data in PostgreSQL.

## 4. Repository Files

- `app.py`: Flask API and data model
- `Dockerfile`: Python image build instructions
- `docker-compose.yml`: Multi-container setup (app + db)
- `requirements.txt`: Python dependencies
- `README.md`: This guide

## 5. Prerequisites

Install the following on your system:

- Docker Desktop (Docker Engine + Docker Compose)
- Git (optional, for cloning)

Verify installation:

```bash
docker --version
docker compose version
```

## 6. Start From Scratch

### Step 1: Clone and move into project

```bash
git clone <your-repo-url>
cd ci-cd-job-tracker
```

### Step 2: Build and start containers

```bash
docker compose up --build
```

What happens here:

- Builds Flask image from `Dockerfile`
- Pulls PostgreSQL image (`postgres:15`) if missing
- Starts both containers
- App becomes available at `http://localhost:5000`

### Step 3: Verify platform is running

```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

Expected:

- `/` returns platform running message
- `/health` returns `{"status":"UP"}`

## 7. API Revision Sheet 

Base URL:

```text
http://localhost:5000
```

### 1) Add a job

```bash
curl -X POST http://localhost:5000/jobs/add \
	-H "Content-Type: application/json" \
	-d '{
		"job_name": "build-main",
		"status": "SUCCESS",
		"duration": 125,
		"triggered_by": "github-actions"
	}'
```

### 2) List all jobs

```bash
curl http://localhost:5000/jobs
```

### 3) Get stats

```bash
curl http://localhost:5000/jobs/stats
```

Returned stats include:

- `total_jobs`
- `successful_jobs`
- `failed_jobs`
- `success_rate`

## 8. Useful Docker Commands (Interview Ready)

### Run in detached mode

```bash
docker compose up -d --build
```

### Check running containers

```bash
docker compose ps
```

### View logs

```bash
docker compose logs -f
```

### Restart services

```bash
docker compose restart
```

### Rebuild only app image

```bash
docker compose build app
docker compose up -d
```

## 9. Stop the Platform (Start-to-Stop Complete)

### Stop containers only (keep data)

```bash
docker compose down
```

### Stop and remove volumes (delete DB data)

```bash
docker compose down -v
```

### Optional full cleanup (also remove images)

```bash
docker compose down -v --rmi all
```

## 10. Common Troubleshooting

### Port 5000 or 5432 already in use

- Stop conflicting local services/containers
- Or change host ports in `docker-compose.yml`

### App fails to connect to DB at startup

- Check DB container status: `docker compose ps`
- Check logs: `docker compose logs -f app db`
- Retry after restart: `docker compose restart`

### Reset everything to clean state

```bash
docker compose down -v
docker compose up --build
```

## 11. Interview Talking Points

Use these points to explain the project quickly:

1. Why containers: consistent environment and easy onboarding.
2. Why Compose: orchestration of app + database with one command.
3. Data persistence: Docker volume keeps PostgreSQL data.
4. Service communication: app connects to DB using service name `db`.
5. Health and observability: `/health`, container logs, and stats API.
6. Trade-offs: no auth layer yet, simple schema, basic startup wait.

## 12. One-Minute Runbook (Memorize)

```bash
docker compose up --build
curl http://localhost:5000/health
curl -X POST http://localhost:5000/jobs/add -H "Content-Type: application/json" -d '{"job_name":"test","status":"SUCCESS","duration":30,"triggered_by":"manual"}'
curl http://localhost:5000/jobs
curl http://localhost:5000/jobs/stats
docker compose down
```

This is the complete lifecycle from startup to shutdown.
