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
@app.route("/workflows")
def get_workflows():

    workflows = WorkflowRun.query.order_by(
        WorkflowRun.run_number.desc()
    ).all()

    html = """
    <html>
    <head>
        <title>GitHub Workflow Runs</title>
        <style>
            body{
                font-family:Arial;
                margin:20px;
            }

            table{
                border-collapse:collapse;
                width:100%;
            }

            th,td{
                border:1px solid #ddd;
                padding:10px;
                text-align:left;
            }

            th{
                background:#2d6cdf;
                color:white;
            }

            tr:nth-child(even){
                background:#f5f5f5;
            }
        </style>
    </head>

    <body>

    <h2>GitHub Workflow Runs</h2>

    <table>

    <tr>
        <th>Run ID</th>
        <th>Workflow</th>
        <th>Branch</th>
        <th>Status</th>
        <th>Conclusion</th>
        <th>Actor</th>
        <th>Run Number</th>
        <th>Duration(s)</th>
    </tr>
    """

    for workflow in workflows:

        html += f"""
        <tr>
            <td>{workflow.run_id}</td>
            <td>{workflow.workflow_name}</td>
            <td>{workflow.branch}</td>
            <td>{workflow.status}</td>
            <td>{workflow.conclusion}</td>
            <td>{workflow.actor}</td>
            <td>{workflow.run_number}</td>
            <td>{workflow.duration_seconds}</td>
        </tr>
        """

    html += """
    </table>

    </body>
    </html>
    """

    return html

@app.route("/debug")
def debug():

    workflows = WorkflowRun.query.all()

    return {
        "count": len(workflows)
    }

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
