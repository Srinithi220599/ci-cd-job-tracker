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

        created_at = datetime.fromisoformat(
            run["created_at"].replace("Z", "+00:00")
        )

        updated_at = datetime.fromisoformat(
            run["updated_at"].replace("Z", "+00:00")
        )

        duration = int(
            (updated_at - created_at).total_seconds()
        )

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
            created_at=created_at,
            updated_at=updated_at,
            duration_seconds=duration
        )

        db.session.add(workflow)

        new_runs += 1

    db.session.commit()

    return jsonify({
        "message": "Workflow synchronization completed successfully.",
        "new_runs_added": new_runs,
        "duplicates_skipped": duplicates
    })
@app.route("/workflows", methods=["GET"])
def get_workflows():

    workflows = WorkflowRun.query.order_by(
        WorkflowRun.run_number.desc()
    ).all()

    html = """
    <html>
    <head>
        <title>GitHub Workflow Dashboard</title>

        <style>

        body{
            font-family:Arial;
            margin:20px;
            background:#f5f7fa;
        }

        h2{
            color:#2d6cdf;
        }

        table{
            width:100%;
            border-collapse:collapse;
        }

        th{
            background:#2d6cdf;
            color:white;
            padding:12px;
            text-align:left;
        }

        td{
            padding:10px;
            border:1px solid #ddd;
        }

        tr:nth-child(even){
            background:#f2f2f2;
        }

        tr:hover{
            background:#e8f0ff;
        }

        .success{
            background:#d4edda;
            color:#155724;
            font-weight:bold;
            text-align:center;
        }

        .failure{
            background:#f8d7da;
            color:#721c24;
            font-weight:bold;
            text-align:center;
        }

        .cancelled{
            background:#fff3cd;
            color:#856404;
            font-weight:bold;
            text-align:center;
        }

        .running{
            background:#d1ecf1;
            color:#0c5460;
            font-weight:bold;
            text-align:center;
        }

        a{
            text-decoration:none;
            color:#2d6cdf;
            font-weight:bold;
        }

        </style>

    </head>

    <body>

    <h2>GitHub Workflow Dashboard</h2>

    <table>

    <tr>
        <th>Run ID</th>
        <th>Workflow</th>
        <th>Run No</th>
        <th>Branch</th>
        <th>Event</th>
        <th>Status</th>
        <th>Conclusion</th>
        <th>Triggered By</th>
        <th>Duration (sec)</th>
        <th>Created At</th>
        <th>GitHub</th>
    </tr>
    """

    for workflow in workflows:

        conclusion = workflow.conclusion if workflow.conclusion else "running"

        if conclusion.lower() == "success":
            css_class = "success"
        elif conclusion.lower() == "failure":
            css_class = "failure"
        elif conclusion.lower() == "cancelled":
            css_class = "cancelled"
        else:
            css_class = "running"

        html += f"""
        <tr>
            <td>{workflow.run_id}</td>
            <td>{workflow.workflow_name}</td>
            <td>{workflow.run_number}</td>
            <td>{workflow.branch}</td>
            <td>{workflow.event}</td>
            <td>{workflow.status}</td>
            <td class="{css_class}">{conclusion.upper()}</td>
            <td>{workflow.actor}</td>
            <td>{workflow.duration_seconds}</td>
            <td>{workflow.created_at.strftime("%d-%m-%Y %H:%M:%S") if workflow.created_at else ""}</td>
            <td><a href="{workflow.html_url}" target="_blank">View Run</a></td>
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
