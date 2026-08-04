# ADR-010: Claims Require Evidence

## Status

Proposed

## Date

2026-08-02

## Context

Architecture documents, generated reports, passing unit tests, and deployed demos prove different things. Collapsing them into one status invites accidental hype and stale claims.

## Decision

Every material capability claim will carry independent authority, proof class, freshness, disposition, and execution outcome. Evidence records are immutable observations; corrections create linked records.

Generated summaries may project evidence. They may not certify themselves.

## Invariants

- docs-only architecture is not implementation proof
- test proof names its scope and governing commit
- failed or blocked runs remain visible
- stale evidence cannot silently support current claims
- supersession preserves prior records
- timestamp recency alone does not establish authority

## Consequences

The repository must preserve proof artifacts and claim language carefully. The Devpost submission becomes easier to defend.

## Source lineage

Adapted from Codexify ADR-042.
