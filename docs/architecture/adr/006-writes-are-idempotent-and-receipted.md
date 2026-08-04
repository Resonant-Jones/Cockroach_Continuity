# ADR-006: Writes Are Idempotent and Receipted

## Status

Proposed

## Date

2026-08-02

## Context

Public networks, application restarts, provider retries, and worker replay can repeat the same write intent. Without deterministic identity and receipts, retries may create duplicate events or contradictory assertions.

## Decision

Every retryable mutation will use a deterministic idempotency key and produce a durable operation receipt. Duplicate equivalent intent returns the original receipt or a deterministic duplicate outcome.

Execution retries create new attempt records without duplicating canonical events.

## Invariants

- equivalent write intent has stable idempotency identity
- distinct intent cannot reuse another operation's receipt
- receipt state does not replace canonical domain truth
- malformed or failed receipt claims are visible
- replay cannot silently create a second approved assertion

## Consequences

Storage constraints and receipt lifecycle must be designed explicitly. Recovery becomes safe across process and deployment boundaries.

## Source lineage

Adapted from Codexify ADR-017 with graph-specific assumptions removed.
