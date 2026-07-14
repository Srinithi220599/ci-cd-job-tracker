from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class WorkflowRun(db.Model):
    __tablename__ = "workflow_runs"

    id = db.Column(db.Integer, primary_key=True)

    run_id = db.Column(db.BigInteger, unique=True, nullable=False)

    workflow_name = db.Column(db.String(200))

    workflow_file = db.Column(db.String(200))

    run_number = db.Column(db.Integer)

    branch = db.Column(db.String(100))

    event = db.Column(db.String(100))

    status = db.Column(db.String(50))

    conclusion = db.Column(db.String(50))

    actor = db.Column(db.String(100))

    duration_seconds = db.Column(db.Integer)

    html_url = db.Column(db.String(500))

    created_at = db.Column(db.DateTime)

    updated_at = db.Column(db.DateTime)

    synced_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
