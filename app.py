from flask import Flask, jsonify
from models import db
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


@app.route("/")
def home():
    return jsonify({
        "application": "GitHub Workflow Analytics Platform",
        "status": "Running"
    })


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
