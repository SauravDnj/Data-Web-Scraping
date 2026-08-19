import os

# Settings() is evaluated at app import time (app/main.py:create_app()),
# so mandatory infrastructure variables must exist before any test in
# this directory imports app.main. These are dummy values — no real
# service needs to be reachable for these tests, since dependency
# health is exercised through app.dependency_overrides.
os.environ.setdefault("APP_SECRET", "test-secret")
os.environ.setdefault(
    "DATABASE_URL",
    "mysql+pymysql://app_user:test@localhost:3306/google_data_platform_test",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
