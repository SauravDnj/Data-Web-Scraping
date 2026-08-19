# apps/api

FastAPI backend. Scaffolded starting T010/T014. Control plane only: auth,
validation, job creation, record query. Never performs long-running
collection work in-request — that belongs to `workers/`.
