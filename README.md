# GitHub Workflow Analytics Platform

## Overview

I built a Dockerized GitHub Workflow Analytics Platform using **Flask**, **PostgreSQL**, **Docker Compose**, and **GitHub Actions**.

The application integrates with the **GitHub REST API** to fetch GitHub Actions workflow execution details. The `/sync` endpoint synchronizes workflow runs into PostgreSQL while preventing duplicate entries using the GitHub **Run ID** as the unique identifier. Workflow execution duration is calculated using the workflow start and end timestamps and stored in the database.

The `/workflows` endpoint retrieves workflow history from PostgreSQL and displays it as an HTML dashboard with color-coded workflow statuses. The application is fully containerized using Docker Compose and its CI pipeline is automated using GitHub Actions running on a self-hosted runner.

---

# Project Overview

This project is a containerized CI/CD monitoring application that fetches GitHub Actions workflow execution details, stores them in PostgreSQL, and displays them through a Flask dashboard.
![Uploading image.png…]()

---

# Technologies Used

- Python
- Flask
- SQLAlchemy
- PostgreSQL
- Docker
- Docker Compose
- GitHub Actions
- GitHub REST API
- Self Hosted GitHub Runner

---

# Project Architecture

```
                    Git Push
                        │
                        ▼
                GitHub Actions
                        │
                        ▼
             Docker Compose (CI)
                        │
                        ▼
          Flask Container + PostgreSQL
                        │
                        ▼
               POST /sync Endpoint
                        │
                        ▼
             GitHub Actions REST API
                        │
                        ▼
          Store Workflow Runs in PostgreSQL
                        │
                        ▼
              GET /workflows Dashboard
```

---

# Project Structure

```
ci-cd-job-tracker
│
├── app.py
├── models.py
├── github_service.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .github/
│    └── workflows/
│          └── docker-ci.yml
└── README.md
```

---

# Environment Variables

```
DATABASE_URL
GITHUB_OWNER
GITHUB_REPO
GITHUB_TOKEN
```

---

# Docker Containers

## Flask Container

Responsible for

- Running Flask application
- Calling GitHub REST API
- Storing workflow data
- Displaying Workflow Dashboard

---

## PostgreSQL Container

Responsible for

- Storing workflow execution history
- Persisting workflow data
- Avoiding data loss using Docker Volumes

---

# REST API Endpoints

---

## 1. Home Endpoint

```
GET /
```

### Purpose

Checks whether the Flask application is running.

### Flow

```
Browser
   │
GET /
   │
Flask
   │
Application Status
```

### Response

```json
{
    "application":"GitHub Workflow Analytics Platform",
    "status":"Running"
}
```

---

## 2. Health Endpoint

```
GET /health
```

### Purpose

Checks application health.

### Why?

Used by GitHub Actions before executing API tests.

### Flow

```
GitHub Actions
      │
GET /health
      │
Flask
      │
Returns UP
```

### Response

```json
{
    "status":"UP"
}
```

---

## 3. GitHub Configuration

```
GET /github-config
```

### Purpose

Verifies that Docker Compose correctly passed GitHub environment variables to the Flask application.

### Flow

```
Docker Compose
      │
Environment Variables
      │
Flask
      │
GET /github-config
      │
Browser
```

### Returns

- GitHub Owner
- Repository Name
- GitHub API URL

---

## 4. Synchronize Workflow Runs ⭐

```
POST /sync
```

### Purpose

Synchronizes GitHub Actions workflow runs into PostgreSQL.

### Complete Flow

```
POST /sync
      │
      ▼
GitHub REST API
      │
      ▼
Download Workflow Runs
      │
      ▼
Check Duplicate Run IDs
      │
      ▼
Calculate Workflow Duration
      │
      ▼
Store into PostgreSQL
      │
      ▼
Return Summary
```

### Internal Steps

1. Calls GitHub REST API.
2. Downloads workflow execution history.
3. Checks whether the Run ID already exists.
4. Skips duplicate workflow runs.
5. Calculates workflow duration.
6. Stores workflow details in PostgreSQL.

### Sample Response

```json
{
    "new_runs_added":20,
    "duplicates_skipped":5
}
```

### Why POST?

Because this endpoint modifies database records.

---

## 5. Workflow Dashboard

```
GET /workflows
```

### Purpose

Displays workflow history stored in PostgreSQL.

### Flow

```
Browser
      │
GET /workflows
      │
Flask
      │
Read PostgreSQL
      │
Generate HTML Dashboard
      │
Browser
```

### Dashboard Displays

- Workflow Name
- Run ID
- Branch
- Event
- Status
- Conclusion
- Triggered By
- Workflow Duration
- Created Time
- GitHub Workflow Link

### Status Colors

🟩 Green → Success

🟥 Light Red → Failure

🟨 Yellow → Cancelled

🟦 Blue → Running

---

# Running the Project

## Build and Start Containers

```bash
docker compose up --build
```

---

## Synchronize Workflow Runs

```
POST http://localhost:5000/sync
```

---

## Open Dashboard

```
http://localhost:5000/workflows
```

---

# GitHub Actions CI Pipeline

The CI pipeline performs the following steps:

1. Checkout Repository
2. Build Docker Image
3. Start Docker Containers
4. Verify Application Health
5. Verify GitHub Configuration
6. Synchronize Workflow Runs
7. Validate Application
8. Display Container Logs

---

# Key Concepts Demonstrated

- Docker Image Creation
- Docker Compose
- Multi-Container Applications
- PostgreSQL Integration
- SQLAlchemy ORM
- Flask REST APIs
- GitHub REST API Integration
- GitHub Actions CI
- Self Hosted GitHub Runner
- Docker Volumes
- Environment Variables
- REST API Design
- Duplicate Data Prevention
- HTML Dashboard Generation

---

# Future Enhancements

- Workflow Statistics Dashboard
- Average Workflow Duration
- Success Rate Analytics
- Filter by Branch
- Filter by Status
- Search Workflow Runs
- Grafana Dashboard
- AWS EC2 Deployment
- Kubernetes Deployment
- Scheduled Synchronization using Cron

---

# Interview Questions to Prepare

### Why did you use Docker Compose?

To orchestrate multiple containers (Flask and PostgreSQL) using a single configuration file and manage networking, volumes, and environment variables consistently.

---

### Why PostgreSQL?

To persist workflow execution history so it remains available even after the Flask container restarts.

---

### Why did you calculate workflow duration?

The GitHub API provides only `created_at` and `updated_at` timestamps. I calculated the duration once during synchronization and stored it, making later reporting and analytics faster.

---

### Why use POST for `/sync`?

Because it changes application state by inserting new workflow records into the database.

---

### Why use GitHub Run ID?

GitHub guarantees each workflow run has a unique Run ID, making it an ideal key to prevent duplicate records.

---

### Why use a self-hosted runner?

To execute GitHub Actions directly on my laptop, leveraging the locally installed Docker Desktop and enabling local verification of the application while learning.
