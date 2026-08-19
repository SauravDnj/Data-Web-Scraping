# Risks and Blockers

## Current risks

### R001 --- Provider policy changes

Risk: Google products, APIs, pricing, quotas, or terms may change.

Mitigation: - isolate provider adapter; - verify current documentation
before provider implementation/release; - avoid hard-coded assumptions.

### R002 --- Duplicate records

Risk: business identity is not always deterministic.

Mitigation: - provider IDs where permitted; - canonical keys; -
false-merge tests; - do not use name alone.

### R003 --- Worker failure

Risk: long-running job can stop unexpectedly.

Mitigation: - heartbeat; - state machine; - recovery; - idempotency.

### R004 --- Excessive provider usage

Risk: user config accidentally creates a large job.

Mitigation: - explicit limits; - estimates; - usage budget; - review
step.

### R005 --- Data/privacy risk

Risk: collecting unnecessary personal data.

Mitigation: - field allowlist; - minimization; - retention policy; -
export controls.
