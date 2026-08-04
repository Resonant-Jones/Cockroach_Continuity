# ADR-005: Durable Memory Promotion Is User Governed

## Status

Proposed

## Date

2026-08-02

## Context

Agent-generated candidates may be useful, wrong, sensitive, stale, or phrased more strongly than the evidence supports. Automatically treating them as durable truth would let inference silently rewrite continuity.

## Decision

Model output enters the system as a `MemoryCandidate`. It becomes an active `MemoryAssertion` only after an explicit user-authored approve or revise decision.

Users may reject, revoke, exclude, or expire assertions. Every lifecycle transition preserves provenance and decision history.

## Invariants

- models cannot approve their own candidates
- confidence is not authority
- silence is not consent
- revocation does not erase audit history
- project memory does not silently become personal identity
- exclusions override retrieval convenience

## Consequences

The interface requires a review surface. In return, the system preserves user sovereignty and can explain why durable continuity changed.

## Source lineage

Adapted from Codexify ADR-005, ADR-015, and ADR-016.
