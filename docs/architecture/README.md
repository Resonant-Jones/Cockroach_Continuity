# Cockroach Continuity Architecture

> Status: docs-only architecture baseline
> Last reviewed: 2026-08-02
> Decision owner: Resonant Jones
> Implementation truth: see [`00-current-state.md`](00-current-state.md)

## Purpose

Cockroach Continuity is a greenfield agentic continuity system for the CockroachDB x AWS hackathon. It preserves project state, decisions, corrections, unresolved work, approval history, and provenance across sessions and model changes.

The architecture is intentionally smaller than Codexify. It reuses proven architectural ideas without copying the Codexify product topology or claiming that pre-existing Codexify runtime work was created for this project.

## Core thesis

> Models are replaceable compute. Continuity belongs to the ledger.

A model may propose, summarize, retrieve, or act. It does not become the canonical owner of project truth. Durable continuity is derived from evidence, governed by the user, and persisted with provenance.

## Non-negotiable invariants

1. Canonical events are never silently rewritten by model output.
2. Continuity state is derived from evidence and may be recomputed.
3. Durable memory promotion requires an explicit governance decision.
4. Retrieval selects evidence; retrieval does not certify truth.
5. Authored events and execution attempts have separate identities.
6. Retries and replays are idempotent and produce receipts.
7. Provider state, request state, visibility state, and continuity state remain distinct.
8. Every product claim must name its proof level.
9. CockroachDB is the baseline system of record for durable continuity.
10. AWS hosts the application runtime; it does not own user identity.

## Reading order

| Document | Purpose |
|---|---|
| [`00-current-state.md`](00-current-state.md) | Present-tense implementation truth |
| [`01-system-overview.md`](01-system-overview.md) | Product and component boundaries |
| [`02-domain-model.md`](02-domain-model.md) | Canonical entities and state planes |
| [`03-critical-flows.md`](03-critical-flows.md) | End-to-end behavioral contracts |
| [`04-data-and-storage.md`](04-data-and-storage.md) | CockroachDB schema and persistence rules |
| [`05-security-and-trust-boundaries.md`](05-security-and-trust-boundaries.md) | Authority, consent, and least privilege |
| [`06-observability-and-proof.md`](06-observability-and-proof.md) | Evidence, tracing, and demo proof |
| [`07-deployment-topology.md`](07-deployment-topology.md) | CockroachDB Cloud and AWS deployment shape |
| [`08-tech-debt-and-risks.md`](08-tech-debt-and-risks.md) | Known uncertainty and containment |
| [`source-adoption-matrix.md`](source-adoption-matrix.md) | Provenance of reused architectural ideas |
| [`Architecture-Decision-Hub.md`](Architecture-Decision-Hub.md) | ADR map |

## Documentation law

- `00-current-state.md` wins when target architecture and implementation status differ.
- ADRs explain why a decision exists. They do not prove that it is implemented.
- A diagram is explanatory, not evidence.
- A test result proves only the scope it exercised.
- Generated summaries may describe evidence but may not certify themselves.

## Scope boundary

This corpus defines the first submission-sized vertical slice:

```text
project event
  -> candidate continuity assertion
  -> user approval or rejection
  -> CockroachDB persistence
  -> new session or provider
  -> policy-governed semantic retrieval
  -> continuity brief with provenance
```

It does not define a general-purpose personal companion, social network, autonomous operator, or full Codexify replacement.
