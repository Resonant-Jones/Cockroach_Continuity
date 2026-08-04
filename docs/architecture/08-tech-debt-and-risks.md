# Tech Debt and Risks

## Active risks

| Risk | Impact | Containment |
|---|---|---|
| Scope expands toward full Codexify | Missed deadline | Keep one project, one approval flow, one resume brief |
| Pre-existing work is mistaken for hackathon implementation | Eligibility risk | Maintain source adoption matrix and disclose conceptual reuse |
| Managed MCP is present but not meaningful | Judging risk | Use it for live read-only inspection and audit proof |
| Vector search becomes decorative | Judging risk | Make later-session resume depend on semantic retrieval |
| Model output is promoted without consent | Trust failure | Explicit approval transaction and lifecycle filters |
| CockroachDB schema over-normalizes too early | Delivery delay | Phase A envelope tables and JSON fields where justified |
| Embedding dimension changes | Migration churn | Select provider before vector DDL is finalized |
| Public demo leaks data or secrets | Security incident | Synthetic fixtures, scoped credentials, secret scanning |
| AWS topology becomes overbuilt | Operational fragility | Start with one ECS Fargate service |
| Retrieval crosses project boundaries | Privacy and correctness failure | Structured scope filter before vector ranking |
| Retry duplicates durable state | Corruption | Idempotency keys, unique constraints, durable receipts |
| Continuity brief appears authoritative without evidence | Trust failure | Source citations and proof classification |

## Explicitly deferred

- multi-user collaboration
- personal identity modeling
- automatic browser capture
- autonomous write tools
- graph database integration
- cross-region application failover
- federated continuity sync
- generalized plugin system
- production billing and tenant administration
- large-scale performance claims

## Architectural debt accepted for the hackathon

### Snapshot JSON

A continuity snapshot may store a structured JSON representation plus explicit provenance links rather than normalizing every decision, open loop, and rejected path into separate tables. Normalize later only when query patterns prove the need.

### Synchronous candidate extraction

The first vertical slice may run candidate extraction synchronously after event persistence. The canonical event must commit first, and extraction failure must remain retryable.

### Single application service

UI, API, and bounded background work may share one ECS service. Split workers only when reliability or latency evidence justifies it.

## Decision triggers

Create a new ADR before:

- enabling model-authored durable writes without a user approval step
- adding automatic capture from browsers or external services
- introducing a second canonical datastore
- enabling MCP write access
- adding multi-user or shared continuity
- changing the assertion lifecycle vocabulary
- moving continuity truth into a model, cache, graph, or object store
