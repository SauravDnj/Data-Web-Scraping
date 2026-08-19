"""Verifies connection failures surface as clear, understandable
errors — using a deterministically-unreachable target (not the local
dev MySQL, whose availability changes as T012 progresses) so this
test's outcome doesn't depend on local environment state."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.session import build_engine, build_session_factory, session_scope

UNREACHABLE_DATABASE_URL = "mysql+pymysql://nobody:nothing@127.0.0.1:1/does_not_exist"


def test_unreachable_database_raises_a_clear_operational_error():
    engine = build_engine(UNREACHABLE_DATABASE_URL, pool_pre_ping=False)
    factory = build_session_factory(engine)

    with pytest.raises(OperationalError) as excinfo, session_scope(factory) as session:
        session.execute(text("SELECT 1"))

    # The error should be a real, readable message — not a bare/opaque
    # exception, and it must not contain a password.
    message = str(excinfo.value)
    assert message
    assert "nothing" not in message
