# Cockroach Continuity Build Checklist

> Mode: autonomous
> Verification: required at every item; pause only on external credentials, destructive migration, ADR contradiction, or persistent verification failure.
> Goal: prove one narrow continuity loop end to end before adding anything else.

- [ ] **1. Install executable repository spine**
  Spec ref: `docs/architecture/07-deployment-topology.md` and `01-system-overview.md`
  What to build: Python package, FastAPI process, explicit database seam, local CockroachDB profile, stable Make targets, tests, container, and CI.
  Acceptance: process liveness is independent of database readiness; repository has one stable path for local and CI execution.
  Verify: `make bootstrap && make lint && make typecheck && make test`; `make up && make smoke`.

- [ ] **2. Add migration framework and canonical ledger schema**
  Spec ref: `docs/architecture/02-domain-model.md` and `04-data-and-storage.md`
  What to build: Alembic plus Phase A tables for projects, sessions, project events, execution attempts, memory candidates, memory assertions, approval decisions, evidence links, continuity snapshots, retrieval traces, and operation receipts.
  Acceptance: clean upgrade succeeds; constraints preserve event/attempt identity, lifecycle state, provenance, and idempotency; downgrade/re-upgrade is documented and tested where practical.
  Verify: migration tests against local CockroachDB plus schema introspection.

- [ ] **3. Implement project and event ledger writes**
  Spec ref: `docs/architecture/03-critical-flows.md > Event capture and candidate generation`
  What to build: project creation and event append service/API with durable idempotency receipts and separate execution attempts.
  Acceptance: duplicate equivalent intent returns the prior event/receipt; a retry creates a new attempt without duplicating the authored event.
  Verify: API integration tests including duplicate and retry cases.

- [ ] **4. Implement candidate extraction seam**
  Spec ref: `docs/architecture/03-critical-flows.md > Event capture and candidate generation`
  What to build: provider-neutral structured candidate extractor, deterministic fake provider for tests, live provider adapter behind configuration, evidence references and source hashes.
  Acceptance: extraction failure preserves the canonical event; candidates remain pending and cannot self-promote.
  Verify: provider contract tests plus one configured live smoke path.

- [ ] **5. Implement approval, rejection, revision, and revocation**
  Spec ref: `docs/architecture/03-critical-flows.md > Approval and durable promotion`
  What to build: governed candidate decision transaction that records decision, versions assertion when approved/revised, writes evidence links and receipt, and preserves history.
  Acceptance: atomic and idempotent; rejected/revoked assertions are ineligible for active continuity.
  Verify: concurrency, rollback, duplicate-decision, and lifecycle tests.

- [ ] **6. Implement embedding and policy-governed vector retrieval**
  Spec ref: `docs/architecture/04-data-and-storage.md` and ADR-004
  What to build: embedding adapter, CockroachDB vector columns/index, structured project/lifecycle filtering before semantic ranking, and retrieval trace persistence.
  Acceptance: related evidence is found; cross-project/rejected/revoked evidence is excluded; selected and excluded candidates are traceable.
  Verify: seeded two-project retrieval proof.

- [ ] **7. Implement deterministic continuity compiler and brief**
  Spec ref: `docs/architecture/03-critical-flows.md > Continuity compilation` and `Resume across sessions or models`
  What to build: compile governed evidence into a continuity snapshot/brief with decisions, constraints, corrections, open loops, rejected paths, risks, next actions, and exact provenance IDs.
  Acceptance: same governed facts survive a fresh session and provider switch without provider-local memory.
  Verify: deterministic compiler tests and provider-switch integration proof.

- [ ] **8. Build the minimum web experience**
  Spec ref: `docs/architecture/01-system-overview.md > Minimum product surface`
  What to build: one-project workspace, event entry, candidate review, approve/reject/revise, provider/session switch, continuity brief, provenance/retrieval inspector.
  Acceptance: target proof slice can be demonstrated without direct SQL or curl.
  Verify: browser happy-path test and manual demo rehearsal.

- [ ] **9. Configure read-only Managed MCP inspection**
  Spec ref: ADR-011 and `docs/architecture/05-security-and-trust-boundaries.md`
  What to build: read-only database role and demo-safe inspection views for events, assertions, decisions, snapshots, traces, and receipts.
  Acceptance: inspector reads the durable path and cannot mutate application truth.
  Verify: successful inspection plus rejected write proof.

- [ ] **10. Deploy the verified slice on AWS and capture proof**
  Spec ref: `docs/architecture/06-observability-and-proof.md` and `07-deployment-topology.md`
  What to build: one ECS Fargate application service, managed secrets/configuration, CockroachDB Cloud connectivity, public demo URL, synthetic fixture/reset lane, proof artifacts and submission notes.
  Acceptance: end-to-end flow survives application restart and provider change; database memory layer is visible in the demo.
  Verify: live proof script, restart proof, provider-switch proof, MCP read-only proof, final submission check.
