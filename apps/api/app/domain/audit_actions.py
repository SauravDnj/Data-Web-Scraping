"""Centralized audit action name registry (T037). Services must use
these rather than ad-hoc strings — this is what makes "action names
are defined" a real guarantee instead of a convention someone can
forget. Export actions land here once the export service (T076+)
exists — don't add unused placeholders before then."""

from enum import StrEnum


class AuditAction(StrEnum):
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_ARCHIVED = "project.archived"

    CONFIG_CREATED = "config.created"
    CONFIG_ACTIVATED = "config.activated"

    JOB_CREATED = "job.created"
    JOB_CANCELLED = "job.cancelled"
    JOB_PAUSED = "job.paused"
    JOB_RESUMED = "job.resumed"
    JOB_RETRIED = "job.retried"
