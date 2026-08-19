# Import every model module here so Base.metadata sees it (required
# for Alembic autogenerate — see database/migrations/env.py) and so
# `from app.db.models import User` works. Further models land T023-T026.
from app.db.models.user import User, UserStatus

__all__ = ["User", "UserStatus"]
