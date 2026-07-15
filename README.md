# GitHub Workflow Analytics Platform

## Project Overview

This project is a containerized CI/CD monitoring application that collects GitHub Actions workflow execution details, stores them in PostgreSQL, and displays them through a Flask web application.

The project is completely Dockerized and uses GitHub Actions to automatically build and test the application.

---

## Technologies Used

- Python
- Flask
- SQLAlchemy
- PostgreSQL
- Docker
- Docker Compose
- GitHub Actions
- GitHub REST API

---

## Project Architecture

```
                GitHub Actions
                      │
                      ▼
             GitHub REST API
                      │
             POST /sync Endpoint
                      │
                      ▼
                Flask Application
                      │
                      ▼
                 PostgreSQL
                      │
                      ▼
            GET /workflows Dashboard
```

---

## Features

- Fetches workflow runs from GitHub Actions
- Stores workflow history in PostgreSQL
- Avoids duplicate records using GitHub Run ID
- Displays workflow details in a dashboard
- Calculates workflow execution duration
- Runs inside Docker containers
- Automated CI using GitHub Actions

---

## Project Structure

```
ci-cd-job-tracker
│
├── app.py
├── github_service.py
├── models.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .github
│   └── workflows
│       └── docker-ci.yml
└── README.md
```

---

## Docker Containers

### Flask Container

- Runs the Flask application
- Calls GitHub REST API
- Stores workflow data

### PostgreSQL Container

- Stores workflow execution history

---

## Environment Variables

```
DATABASE_URL
GITHUB_OWNER
GITHUB_REPO
GITHUB_TOKEN
```

---

## REST APIs

### Home

```
GET /
```

Returns application status.

---

### Health Check

```
GET /health
```

Checks whether the application is running.

---

### GitHub Configuration

```
GET /github-config
```

Displays configured GitHub repository information.

---

### Synchronize Workflow Runs

```
POST /sync
```

Fetches workflow runs from GitHub and stores them in PostgreSQL.

Example Response

```json
{
    "new_runs_added": 20,
    "duplicates_skipped": 5
}
```

---

### Workflow Dashboard

```
GET /workflows
```

Displays all workflow runs stored in PostgreSQL.

---

## How It Works

1. GitHub Actions workflow starts.
2. Docker Compose creates Flask and PostgreSQL containers.
3. Flask connects to GitHub REST API.
4. Workflow execution details are retrieved.
5. Data is stored in PostgreSQL.
6. Workflow dashboard displays execution history.

---

## Running Locally

Build and start containers

```bash
docker compose up --build
```

Open

```
http://localhost:5000/workflows
```

Synchronize latest workflow runs

```
POST http://localhost:5000/sync
```

---

## GitHub Actions Pipeline

The CI pipeline performs the following:

- Checkout Repository
- Build Docker Image
- Start Containers
- Verify Health Endpoint
- Verify GitHub Configuration
- Synchronize Workflow Runs
- Verify Application
- Display Container Logs

---

## Key Learning Outcomes

- Docker Image creation
- Docker Compose
- Multi-container applications
- PostgreSQL integration
- Flask REST APIs
- GitHub REST API
- GitHub Actions CI
- Self-hosted GitHub Runner
- Environment Variables
- Persistent Docker Volumes

---

## Future Enhancements

- Workflow statistics dashboard
- Success rate visualization
- Average workflow duration
- Search by workflow name
- Filter by branch
- Filter by status
- Grafana dashboard integration
- Deploy on AWS EC2
