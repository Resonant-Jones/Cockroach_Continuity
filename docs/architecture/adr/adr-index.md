# ADR Index

| ADR | Status | Decision |
|---|---|---|
| [001](001-continuity-is-compiled-from-ledger-evidence.md) | Proposed | Continuity is compiled from ledger evidence |
| [002](002-separate-runtime-state-planes.md) | Proposed | Runtime state planes remain separate |
| [003](003-separate-event-and-attempt-identity.md) | Proposed | Authored events and execution attempts use different identities |
| [004](004-retrieval-policy-is-a-control-plane.md) | Proposed | Retrieval policy is backend-owned and inspectable |
| [005](005-durable-memory-promotion-is-user-governed.md) | Proposed | Durable memory promotion is user governed |
| [006](006-writes-are-idempotent-and-receipted.md) | Proposed | Retryable writes are idempotent and receipted |
| [007](007-models-are-replaceable-compute.md) | Proposed | Models are replaceable compute, not continuity owners |
| [008](008-cockroachdb-is-the-canonical-continuity-store.md) | Proposed | CockroachDB is the canonical continuity store |
| [009](009-aws-hosts-runtime-not-user-truth.md) | Proposed | AWS hosts runtime components, not user truth |
| [010](010-claims-require-evidence.md) | Proposed | Claims require scoped evidence and freshness |
| [011](011-managed-mcp-is-an-inspection-boundary.md) | Proposed | Managed MCP is a read-only inspection boundary |

Use [`000-template.md`](000-template.md) for new decisions.
