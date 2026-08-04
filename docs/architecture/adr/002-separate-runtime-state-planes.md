# ADR-002: Separate Runtime State Planes

## Status

Proposed

## Date

2026-08-02

## Context

The database may be healthy while a model provider is unavailable. An event may be committed while candidate extraction is still running. A task may finish while client visibility fails. A snapshot may be stale while the underlying ledger remains correct.

One `status` field cannot represent this truthfully.

## Decision

The system will model provider runtime, execution attempt, visibility, continuity, and assertion lifecycle as separate state planes.

Acceptance of work means only that the specific acceptance boundary succeeded. It does not imply eventual completion.

## Invariants

- provider state is not inferred from one request outcome
- event persistence does not imply candidate extraction completed
- candidate extraction does not imply approval
- compilation completion does not imply client visibility
- UI wording preserves these distinctions

## Consequences

More vocabulary and UI mapping are required. Incident reasoning, retry behavior, and demo truth become substantially clearer.

## Source lineage

Adapted from Codexify ADR-001 and ADR-002.
