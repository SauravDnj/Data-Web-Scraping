# Memory

Primary product: local-first Google Maps Platform data collection platform.

Stack: Next.js, FastAPI, Python, MySQL, Redis, SQLAlchemy, Alembic.

Architecture: UI → API → services → repositories/provider adapters → MySQL/external provider; long-running work → Redis → worker.

Safety: no CAPTCHA/anti-bot/access-control/rate-limit bypass.

Build strategy: fake provider first, real provider after the complete internal vertical slice works.
