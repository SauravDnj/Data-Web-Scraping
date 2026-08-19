# Architecture Decisions

## ADR-001

Use MySQL as durable system of record.

## ADR-002

Use FastAPI as backend/control plane.

## ADR-003

Use Next.js for dashboard.

## ADR-004

Use Redis for background job coordination.

## ADR-005

Long-running collection executes in workers.

## ADR-006

Provider-specific logic is isolated behind adapters.

## ADR-007

Start without Docker.

## ADR-008

Do not implement provider-control bypass mechanisms.

## ADR-009

Use configuration versioning so historical jobs remain reproducible.

## ADR-010

Use deterministic record identity and database constraints to reduce
duplicates.
