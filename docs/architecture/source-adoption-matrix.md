# Source Adoption Matrix

> Purpose: preserve provenance for pre-existing architectural insight and support honest hackathon disclosure.
> Source project: [Resonant-Jones/Codexify](https://github.com/Resonant-Jones/Codexify)
> Review date: 2026-08-02

## Disclosure statement

Cockroach Continuity is a new project created for the hackathon. Its implementation must be built during the submission period.

The project deliberately reuses architectural concepts, terminology patterns, and documentation discipline developed in Codexify. No Codexify runtime source code is included in this architecture package. Any future copied or adapted code must be identified separately in the repository and Devpost submission.

## Adoption map

| Codexify source | Concept retained | Cockroach Continuity destination | Transformation |
|---|---|---|---|
| [`ADR-001 Queue-Based Completion Acceptance Model`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/001-queue-based-completion-acceptance-model.md) | Acceptance does not equal completion | [`ADR-002`](adr/002-separate-runtime-state-planes.md), critical flows | Generalized from chat queue semantics to event, extraction, and compilation operations |
| [`ADR-002 Dual State Machine Model`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/002-dual-state-machine-model.md) | Runtime and request truth are distinct | [`ADR-002`](adr/002-separate-runtime-state-planes.md) | Expanded into provider, execution, visibility, continuity, and assertion lifecycle planes |
| [`ADR-003 Message Identity vs Request Identity`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/003-message-identity-vs-request-identity.md) | Authored identity differs from attempt identity | [`ADR-003`](adr/003-separate-event-and-attempt-identity.md) | Renamed message to project event and request to execution attempt |
| [`ADR-004 Retrieval Policy as Control Plane`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/004-retrieval-policy-as-control-plane.md) | Retrieval is explicit backend policy | [`ADR-004`](adr/004-retrieval-policy-is-a-control-plane.md) | Applied to project scope, lifecycle filters, vector retrieval, and trace visibility |
| [`ADR-005 Imprint UI Deprecation and Identity Ownership`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/005-imprint-ui-deprecation-and-identity-ownership.md) | Identity ownership is separate from persona or agent behavior | [`ADR-005`](adr/005-durable-memory-promotion-is-user-governed.md), security boundary | Reduced to project-scoped memory governance and prohibition on silent trait inference |
| [`ADR-015 Continuity Engine Working Set and Decay Contract`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/015-continuity-engine-working-set-and-decay-contract.md) | Working set, provenance, decay, imported lineage | [`ADR-001`](adr/001-continuity-is-compiled-from-ledger-evidence.md), domain model | Reframed as evidence-backed project continuity rather than account-wide continuity |
| [`ADR-016 Continuity Governance Surface Contract`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/016-continuity-governance-surface-contract.md) | Scope, exclusions, inspection, reset, reversibility | [`ADR-005`](adr/005-durable-memory-promotion-is-user-governed.md) | Reduced to the minimum hackathon approval, revocation, exclusion, and provenance surface |
| [`ADR-017 Graph Write Idempotency and Receipt Semantics`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/017-graph-write-idempotency-and-receipt-semantics.md) | Deterministic task identity and replay receipts | [`ADR-006`](adr/006-writes-are-idempotent-and-receipted.md) | Applied to CockroachDB writes and compiler triggers; graph-specific assumptions removed |
| [`Continuity Protocol Suite`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/continuity-protocol-suite.md) | Context packets, compiled project reality, resume packet, open loops, rejected paths | system overview, domain model, critical flows | Simplified into events, assertions, snapshots, and briefs for one project boundary |
| [`ADR-030 Continuity Protocol Suite Runtime Gate`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/030-continuity-protocol-suite-runtime-gate.md) | Small independently provable slices; token, storage, provenance, retrieval, identity, graph-off, UI, rollback, proof gates | documentation law, current state, data and storage, proof plan | Retained as architecture governance; Codexify-specific paths removed |
| [`ADR-031 Continuity Phase A Storage Migration Gate`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/031-continuity-phase-a-storage-migration-gate.md) | Schema does not authorize writes; migration proof; graph-off baseline | data and storage | Recast for CockroachDB-native tables and vector indexes |
| [`Continuity Storage Schema Proposal`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/continuity-storage-schema-proposal.md) | Distinct packet, state, commit, provenance, and proof boundaries | data and storage, domain model | Consolidated into event, assertion, snapshot, link, trace, and receipt tables |
| [`ADR-042 Canonical Audit Evidence Contract`](https://github.com/Resonant-Jones/Codexify/blob/main/docs/architecture/adr/042-canonical-audit-evidence-contract.md) | Independent proof axes, freshness, supersession, claim evidence | [`ADR-010`](adr/010-claims-require-evidence.md), observability and proof | Applied to hackathon claims and demo evidence |

## Concepts intentionally not adopted

- Codexify account-wide identity substrate
- persona composition surfaces
- local node federation
- optional Neo4j graph topology
- Campaign Runner and Guardian delegation topology
- browser automation
- Codexify-specific runtime token registries
- Codexify release support claims
- Codexify database migrations or application code

## Devpost disclosure draft

> Cockroach Continuity is a new greenfield implementation created during the hackathon submission period. The project reuses architectural concepts and documentation patterns developed in my prior open-source Codexify work, including provenance-aware continuity, user-governed memory promotion, state-plane separation, idempotent receipts, and evidence-backed claims. The CockroachDB schema, AWS deployment, application runtime, user interface, and hackathon demonstration were built specifically for this project. No pre-existing Codexify runtime is presented as newly created work.
