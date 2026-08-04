# Data and Storage

## Decision summary

CockroachDB is the canonical store for durable project continuity. Transactional records and vector-searchable evidence live in one system so approval state, provenance, and semantic retrieval do not drift across independent databases.

Object bytes may live in Amazon S3. S3 references are artifacts, not continuity truth. Provider caches, container filesystems, and in-memory queues are operational state only.

## Proposed Phase A tables

| Table | Purpose |
|---|---|
| `projects` | Project scope and ownership |
| `sessions` | Interaction session metadata |
| `project_events` | Immutable project event ledger |
| `execution_attempts` | Attempt-level model and worker execution history |
| `memory_candidates` | Pending agent-proposed assertions |
| `memory_assertions` | Approved, versioned durable assertions |
| `approval_decisions` | User governance decisions |
| `evidence_links` | Assertion and snapshot provenance edges |
| `continuity_snapshots` | Derived project reality snapshots |
| `retrieval_traces` | Retrieval policy and evidence selection traces |
| `operation_receipts` | Idempotency and task receipts |
| `artifact_references` | S3 or external artifact metadata and hashes |

## Vector placement

Distributed Vector Indexing should be used on evidence that participates in semantic retrieval, initially:

- `project_events.embedding`
- `memory_assertions.embedding`

The embedding dimension remains **TBD until the embedding provider is selected**. Schema migrations must not hardcode a dimension before the provider contract is accepted.

Vector results are filtered by structured policy fields such as:

- `project_id`
- assertion lifecycle
- sensitivity
- source type
- created time
- revocation state
- import provenance

Semantic nearest-neighbor order is never the only eligibility rule.

## Transaction boundaries

### Approving a candidate

One transaction should:

1. lock the candidate row
2. verify pending lifecycle state
3. insert the approval decision
4. create or version the durable assertion
5. create evidence links
6. mark the candidate approved
7. write the operation receipt

Compilation happens after commit. A failed compiler must not roll back the user-authored approval.

### Revoking an assertion

Revocation creates a new lifecycle decision and preserves prior versions. Derived snapshots referencing the old assertion become stale or superseded and may be rebuilt.

## Idempotency

Every externally retryable mutation carries an idempotency key scoped to the operation owner and intent.

Recommended uniqueness boundaries:

```text
(project_id, operation_kind, idempotency_key)
(event_id, attempt_number)
(candidate_id, decision_id)
(snapshot_id, source_assertion_version_id)
```

Receipts are durable where replay can cross process or deployment boundaries.

## Provenance

Every derived record must preserve:

- producer attempt ID
- source event or assertion IDs
- source content hashes where practical
- policy version
- model and provider metadata
- creation time
- import or native lineage

A generated summary cannot be its own sole source.

## Deletion and retention

- Canonical events should use append-only correction or tombstone semantics during the hackathon slice.
- Candidates may expire without becoming assertions.
- Assertions may be revoked but remain auditable.
- Snapshots may be superseded or rebuilt.
- Retrieval traces may use bounded retention if their proof role is preserved.
- Restricted artifacts require explicit deletion and access policy.

## Migration gate

Before accepting a migration:

1. clean database upgrade succeeds
2. existing database upgrade succeeds
3. downgrade succeeds when practical
4. indexes and constraints are introspected
5. minimal valid rows can be inserted in tests
6. vector extension and index behavior are proven
7. no runtime writes are smuggled into the schema task
8. the application works without any optional graph system

## Deliberate exclusions

Phase A does not require:

- Neo4j or another graph database
- cross-user continuity
- federated node sync
- automatic browser capture
- durable personal trait inference
- event sourcing infrastructure beyond the bounded ledger tables
- a separate vector database
