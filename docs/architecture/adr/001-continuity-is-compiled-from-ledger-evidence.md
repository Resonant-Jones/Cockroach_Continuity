# ADR-001: Continuity Is Compiled From Ledger Evidence

## Status

Proposed

## Date

2026-08-02

## Context

A transcript, a vector search result, and a model summary answer different questions. Treating any one of them as current project truth creates stale snapshots, unverifiable claims, and provider dependence.

## Decision

Cockroach Continuity will preserve canonical project events and user governance decisions in an append-oriented ledger. It will compile continuity snapshots from eligible evidence without rewriting source events.

Continuity snapshots are derived, versioned, provenance-linked, and recomputable.

## Invariants

- canonical events remain distinct from compiled state
- every snapshot names its source assertion versions
- a snapshot may be superseded without deleting history
- imported evidence remains visibly imported
- continuity state does not become a personal identity claim

## Consequences

The system carries more explicit lineage, but it can explain what it believes is current and rebuild that state after provider or runtime changes.

## Source lineage

Adapted from Codexify ADR-015, ADR-016, and the Continuity Protocol Suite. See [`../source-adoption-matrix.md`](../source-adoption-matrix.md).
