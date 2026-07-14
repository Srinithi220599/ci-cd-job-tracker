from flask import Flask, request, jsonify
from models import db, WorkflowRun
from datetime import datetime
import os
import requests
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/cicd_db"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_API_URL = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs"
)


@app.route("/")
def home():
    return jsonify({
        "message": "CI/CD Job Tracking Platform Running"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "UP"
    })

@app.route("/jobs", methods=["GET"])
def get_jobs():

    jobs = Job.query.all()

    output = []

    for job in jobs:

        output.append({
            "id": job.id,
            "job_name": job.job_name,
            "status": job.status,
            "duration": job.duration,
            "triggered_by": job.triggered_by,
            "timestamp": job.timestamp
        })

    return jsonify(output)

@app.route("/jobs/add", methods=["POST"])
def add_job():

    data = request.json

    job = Job(
        job_name=data.get("job_name"),
        status=data.get("status"),
        duration=data.get("duration"),
        triggered_by=data.get("triggered_by")
    )

    db.session.add(job)

    db.session.commit()

    return jsonify({
        "message": "Job added successfully"
    }), 201

@app.route("/jobs/stats", methods=["GET"])
def job_stats():

    total = Job.query.count()

    success = Job.query.filter_by(status="SUCCESS").count()

    failed = Job.query.filter_by(status="FAILED").count()

    success_rate = 0

    if total > 0:
        success_rate = round((success / total) * 100, 2)

    return jsonify({
        "total_jobs": total,
        "successful_jobs": success,
        "failed_jobs": failed,
        "success_rate": success_rate
    })

if __name__ == "__main__":

    time.sleep(10)

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000)
