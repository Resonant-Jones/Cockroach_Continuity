# 00 Current State

> Truth authority: current implementation status
> Last updated: 2026-08-02

## Current proof classification

**DOCS_ONLY**

The repository currently contains a project description and this architecture corpus. No runtime implementation is proven by these documents.

## Proven present state

- Public repository exists.
- Project name is Cockroach Continuity.
- The stated purpose is a continuity ledger for resilient AI systems.
- An architecture baseline and proposed ADR set have been prepared.

## Not yet proven

The following must not be described as implemented until direct evidence exists:

- CockroachDB Cloud cluster connectivity
- distributed vector index creation or query execution
- Managed MCP Server connectivity
- application schema migrations
- API routes or worker execution
- AWS deployment
- user authentication or authorization
- candidate memory extraction
- approval or rejection workflow
- continuity compilation
- cross-model resume behavior
- a functional public demo
- production readiness, resilience, scale, or zero-downtime behavior

## Target proof slice

The first live vertical slice should prove:

1. A project event is accepted and persisted.
2. A model proposes a continuity candidate linked to source evidence.
3. The user approves or rejects the candidate.
4. An approved assertion is stored transactionally in CockroachDB.
5. A vector query retrieves relevant evidence in a later session.
6. A continuity brief cites the exact assertions and source events it used.
7. A different model or provider can resume from the same durable state.
8. An operator or judge can inspect the data path through the Managed MCP Server without granting write authority.

## Evidence required before changing classification

| Classification | Minimum evidence |
|---|---|
| `DOCS_ONLY` | Architecture or specification exists |
| `IMPLEMENTED_UNPROVEN` | Code path exists, but no accepted runtime proof |
| `CURRENT_TEST_PROOF` | Relevant automated tests pass against the governing commit |
| `PARTIAL_VERTICAL_SLICE` | Bounded end-to-end path works, with declared exclusions |
| `CURRENT_LIVE_PROOF` | End-to-end demo succeeds on the supported deployed path |
| `BLOCKED` | Required dependency or proof path cannot currently run |

## Update rule

A future change to this file must include:

- governing commit or release identifier
- proof command or live-demo procedure
- relevant artifacts or trace identifiers
- known exclusions
- freshness boundary

Timestamp recency alone is not proof freshness.
