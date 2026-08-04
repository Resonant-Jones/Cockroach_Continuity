# ADR-004: Retrieval Policy Is a Control Plane

## Status

Proposed

## Date

2026-08-02

## Context

If retrieval scope is hidden in prompts, frontend heuristics, or provider behavior, the system cannot explain why evidence was selected or prevent cross-project leakage.

## Decision

Retrieval policy will be explicit, backend-owned, inspectable, and resolved before vector search or prompt construction.

The canonical chain is:

```text
user intent and project scope
  -> retrieval override
  -> effective policy
  -> structured eligibility filters
  -> vector and lexical retrieval
  -> selected evidence
  -> retrieval trace
```

## Invariants

- prompt text cannot widen retrieval scope
- project filtering occurs before semantic ranking
- rejected, revoked, expired, and excluded assertions are ineligible by default
- vector score does not certify truth
- traces reflect backend policy, not frontend reconstruction

## Consequences

Policy vocabulary and trace storage must stay aligned, but retrieval becomes testable and explainable.

## Source lineage

Adapted from Codexify ADR-004.
