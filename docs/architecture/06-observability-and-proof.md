# Observability and Proof

## Principle

Cockroach Continuity must not guess its own behavior. It records what was attempted, what completed, what evidence was selected, and what remains unresolved.

## Independent evidence axes

A single `status` field is insufficient. Proof records should keep these independent:

| Axis | Example values |
|---|---|
| Authority | canonical, provisional |
| Proof class | docs_only, implemented_unproven, current_test_proof, partial_vertical_slice, current_live_proof, blocked |
| Freshness | current, stale |
| Disposition | accepted, superseded, contradicted, rejected |
| Execution outcome | pass, fail, blocked, error, not_applicable |

## Required traces

### Write trace

- event or command ID
- request ID
- execution attempt ID
- idempotency key
- transaction result
- receipt ID
- downstream trigger status

### Candidate trace

- source event IDs
- model and provider
- prompt or extractor version identifier
- proposed candidate IDs
- confidence and sensitivity
- validation warnings

### Retrieval trace

- effective policy
- project and scope filters
- query embedding identity
- candidate scores
- excluded candidates and reasons
- selected evidence
- widening reason

### Compilation trace

- input assertion versions
- policy version
- deterministic input hash
- output snapshot ID
- warnings, blockers, and confidence
- prior snapshot relationship

## Demo proof plan

The submission video should show one uninterrupted proof narrative:

1. Record a project decision and a rejected path.
2. Show candidate generation with source evidence.
3. Approve one candidate and reject another.
4. End the session or switch model providers.
5. Start a fresh session.
6. Generate a continuity brief that recalls the approved decision and avoids the rejected candidate.
7. Open a provenance view showing source events and retrieval reasons.
8. Use the Managed MCP Server or a database inspection view to show the durable rows and vector-backed retrieval path.

The video should not rely on narration alone. The database memory layer must be visible.

## Minimum acceptance checks

- same idempotency key does not duplicate an event
- second execution attempt receives a new attempt ID
- rejected candidate is absent from active continuity
- revoked assertion makes old snapshot stale
- project-scoped retrieval does not cross project boundaries
- provider switch produces equivalent durable project facts
- continuity brief cites source evidence
- MCP inspector cannot write
- restart preserves approved assertions and snapshots

## Freshness rule

Evidence is stale when any governing input changes, including:

- application commit
- schema migration head
- policy version
- embedding provider or dimension
- deployment configuration
- model or provider contract when the claim depends on it
- proof script or fixture

A newer timestamp does not automatically supersede stronger evidence.

## Claim language

Use precise phrases:

- "documented" for architecture only
- "implemented" for code-path existence
- "test-proven" for passing bounded tests
- "live-proven" for deployed end-to-end proof
- "production-ready" only after security, resilience, operations, and scale evidence exists
