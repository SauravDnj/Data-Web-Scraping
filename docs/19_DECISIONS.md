# Architecture Decision Records

## ADR-001 --- Local-first, no Docker for V1

Decision: develop locally without Docker.

Reason: reduces setup complexity while the architecture is being learned
and validated.

Future: Docker may be introduced for deployment consistency.

## ADR-002 --- MySQL as system of record

Decision: use MySQL.

Reason: user preference, mature ecosystem, relational integrity, JSON
support, and sufficient capability for V1.

## ADR-003 --- Provider adapter boundary

Decision: isolate Google-specific operations behind an adapter.

Reason: prevents provider logic from contaminating the application
domain and allows future providers.

## ADR-004 --- Worker-based long-running jobs

Decision: long-running collection work must not run inside HTTP
requests.

Reason: reliability, retries, cancellation, and scalability.

## ADR-005 --- No access-control bypass

Decision: do not build mechanisms intended to defeat CAPTCHAs, anti-bot
controls, rate limits, or authentication.

Reason: security, compliance, maintainability, and provider
requirements.

## ADR-006 --- Documentation-driven coding

Decision: architecture and task documents are the source of truth.

Reason: enables Claude Code sessions to resume without losing project
context.
