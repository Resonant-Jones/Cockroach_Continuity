# Architecture Decision Hub

## Status

All decisions in this directory are **Proposed** until explicitly ratified by the project owner. Their presence in the repository does not silently convert them to accepted policy.

## Reading order

1. [`ADR-001 Continuity Is Compiled From Ledger Evidence`](adr/001-continuity-is-compiled-from-ledger-evidence.md)
2. [`ADR-002 Separate Runtime State Planes`](adr/002-separate-runtime-state-planes.md)
3. [`ADR-003 Separate Event and Attempt Identity`](adr/003-separate-event-and-attempt-identity.md)
4. [`ADR-004 Retrieval Policy Is a Control Plane`](adr/004-retrieval-policy-is-a-control-plane.md)
5. [`ADR-005 Durable Memory Promotion Is User Governed`](adr/005-durable-memory-promotion-is-user-governed.md)
6. [`ADR-006 Writes Are Idempotent and Receipted`](adr/006-writes-are-idempotent-and-receipted.md)
7. [`ADR-007 Models Are Replaceable Compute`](adr/007-models-are-replaceable-compute.md)
8. [`ADR-008 CockroachDB Is the Canonical Continuity Store`](adr/008-cockroachdb-is-the-canonical-continuity-store.md)
9. [`ADR-009 AWS Hosts the Runtime, Not User Truth`](adr/009-aws-hosts-runtime-not-user-truth.md)
10. [`ADR-010 Claims Require Evidence`](adr/010-claims-require-evidence.md)
11. [`ADR-011 Managed MCP Is an Inspection Boundary`](adr/011-managed-mcp-is-an-inspection-boundary.md)

## Doctrine

Cockroach Continuity does not confuse generated language with durable truth.

It records evidence, asks for authority, preserves lineage, and explains what it carried forward.
