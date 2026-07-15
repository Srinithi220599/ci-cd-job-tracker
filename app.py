from flask import Flask, jsonify
from models import db, WorkflowRun
from github_service import fetch_workflow_runs
from datetime import datetime
import os
import time

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/cicd_db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

# GitHub Configuration
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_API_URL = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs"
)

@app.route("/sync", methods=["POST"])
def sync():

    github_data = fetch_workflow_runs()

    if "workflow_runs" not in github_data:
        return jsonify(github_data), 500

    new_runs = 0
    duplicates = 0

    for run in github_data["workflow_runs"]:

        existing = WorkflowRun.query.filter_by(
            run_id=run["id"]
        ).first()

        if existing:
            duplicates += 1
            continue

        workflow = WorkflowRun(
            run_id=run["id"],
            workflow_name=run["name"],
            workflow_file=run["path"],
            run_number=run["run_number"],
            branch=run["head_branch"],
            event=run["event"],
            status=run["status"],
            conclusion=run["conclusion"],
            actor=run["actor"]["login"],
            html_url=run["html_url"],
            created_at=datetime.fromisoformat(
                run["created_at"].replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                run["updated_at"].replace("Z", "+00:00")
            ),
            duration_seconds=0
        )

        db.session.add(workflow)

        new_runs += 1

    db.session.commit()

    return jsonify({
        "new_runs_added": new_runs,
        "duplicates_skipped": duplicates
    })

@app.route("/workflows", methods=["GET"])
def get_workflows():

    workflows = WorkflowRun.query.order_by(
        WorkflowRun.run_number.desc()
    ).all()

    output = []

    for workflow in workflows:

        output.append({
            "run_id": workflow.run_id,
            "workflow_name": workflow.workflow_name,
            "run_number": workflow.run_number,
            "branch": workflow.branch,
            "event": workflow.event,
            "status": workflow.status,
            "conclusion": workflow.conclusion,
            "actor": workflow.actor,
            "duration_seconds": workflow.duration_seconds,
            "html_url": workflow.html_url,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        })

    return jsonify(output)
@app.route("/health")
def health():
    return jsonify({
        "status": "UP"
    })


@app.route("/github-config")
def github_config():

    return jsonify({
        "owner": GITHUB_OWNER,
        "repository": GITHUB_REPO,
        "api_url": GITHUB_API_URL
    })


if __name__ == "__main__":

    # Wait for PostgreSQL container
    time.sleep(10)

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000)
