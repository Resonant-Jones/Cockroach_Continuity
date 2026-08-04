# ADR-003: Separate Event and Attempt Identity

## Status

Proposed

## Date

2026-08-02

## Context

One project event may be processed multiple times because of retries, provider fallback, replay, or recovery. Collapsing event identity and execution identity produces duplicate truth or lost attempt history.

## Decision

`project_event_id` identifies the authored or observed event. `execution_attempt_id` identifies one processing attempt. One event may have many attempts.

Retries preserve the original event identity and create a new attempt identity.

## Invariants

- event IDs remain stable across retries
- attempt IDs identify exactly one execution attempt
- attempt history is append-only
- no downstream layer collapses event and attempt identity
- delayed results cannot attach to a different event

## Consequences

The data model gains relationships, but transcript and ledger integrity survive retries and provider changes.

## Source lineage

Adapted from Codexify ADR-003.
