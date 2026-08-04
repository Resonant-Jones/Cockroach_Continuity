# Domain Model

## Canonical entities

| Entity | Canonical role |
|---|---|
| `Project` | Scope boundary for continuity |
| `Session` | One user interaction period; not durable truth by itself |
| `ProjectEvent` | Immutable authored or system-observed event in the ledger |
| `ExecutionAttempt` | One model, worker, or provider attempt associated with an event |
| `MemoryCandidate` | Agent-proposed assertion awaiting governance |
| `MemoryAssertion` | Approved durable assertion with provenance and lifecycle state |
| `ApprovalDecision` | User-authored accept, reject, revise, revoke, or expire decision |
| `EvidenceLink` | Typed edge from assertion or snapshot to source event or artifact |
| `ContinuitySnapshot` | Derived project state compiled from eligible evidence |
| `RetrievalTrace` | Explanation of policy, query, candidates, scores, and selected evidence |
| `OperationReceipt` | Idempotency and execution receipt for a write or background task |
| `ArtifactReference` | Metadata and integrity reference for external bytes or documents |

## Canonical versus derived state

### Canonical

- project records
- project events
- user approval decisions
- approved memory assertions
- revocations
- provenance links
- operation receipts

### Derived and recomputable

- embeddings
- vector search results
- candidate rankings
- continuity snapshots
- resume briefs
- suggested next actions
- model summaries

Derived state may be persisted for performance or audit, but it must retain its derivation inputs and must not overwrite canonical evidence.

## State planes

| State plane | Question answered | Example values |
|---|---|---|
| Provider runtime | Is the inference lane reachable and ready? | unavailable, warming, ready, degraded |
| Execution attempt | What is happening to this specific attempt? | queued, running, completed, retryable_failed, fatal_failed, cancelled |
| Visibility | What lifecycle evidence reached the client? | unseen, acknowledged, streaming_visible, terminal_visible, visibility_degraded |
| Continuity | What project state is currently compiled? | active, stale, superseded, rebuilding, blocked |
| Assertion lifecycle | May this assertion influence continuity? | candidate, approved, rejected, revoked, expired |

These planes are related but must never be collapsed into one overloaded `status` field.

## Identity model

A single authored event may have multiple execution attempts:

```text
project_event_id: stable authored or observed event identity
execution_attempt_id: one processing attempt
attempt_number: monotonic within the event operation
idempotency_key: stable key for equivalent write intent
```

A retry creates a new attempt. It does not create a second authored event unless the user actually authored a new event.

## Memory candidate shape

A candidate should include at minimum:

```yaml
candidate_id: uuid
project_id: uuid
kind: decision | constraint | correction | open_loop | rejected_path | next_action
statement: string
source_event_ids: [uuid]
source_excerpt_hashes: [sha256]
proposed_by_attempt_id: uuid
confidence: 0.0-1.0
sensitivity: project | private | restricted
status: pending | approved | rejected | revised | expired
created_at: timestamp
```

Confidence affects review priority. It does not grant write authority.

## Continuity snapshot shape

A continuity snapshot should carry:

- project goal
- accepted decisions
- active constraints
- corrections
- open loops
- rejected paths
- active artifacts
- known risks
- next actions
- source assertion identifiers
- compilation policy version
- retrieval trace identifier
- compiled timestamp
- freshness boundary

## Domain invariants

1. Every approved assertion has at least one evidence link.
2. A model attempt cannot approve its own candidate.
3. Revocation preserves the prior assertion and decision history.
4. A continuity snapshot points to exact assertion versions.
5. Rejected candidates are not eligible for ordinary continuity retrieval.
6. Similarity score alone cannot promote a candidate.
7. Imported evidence is visibly distinguishable from native project events.
8. Deleting a derived snapshot does not delete canonical events.
