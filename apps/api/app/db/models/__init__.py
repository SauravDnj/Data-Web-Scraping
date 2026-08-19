# Import every model module here so Base.metadata sees it (required
# for Alembic autogenerate — see database/migrations/env.py) and so
# `from app.db.models import User` works. Further models land T026.
from app.db.models.collection_config import CollectionConfig
from app.db.models.job import Job, JobRun, JobRunStatus, JobStatus
from app.db.models.project import Project, ProjectStatus
from app.db.models.record import Record, RecordProvenance
from app.db.models.user import User, UserStatus

__all__ = [
    "User",
    "UserStatus",
    "Project",
    "ProjectStatus",
    "CollectionConfig",
    "Job",
    "JobStatus",
    "JobRun",
    "JobRunStatus",
    "Record",
    "RecordProvenance",
]
