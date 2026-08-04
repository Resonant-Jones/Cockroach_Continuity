# Security and Trust Boundaries

## Authority model

| Boundary | May do | Must not do by default |
|---|---|---|
| Project owner | Govern memory, inspect provenance, reset continuity | Be bypassed by model confidence |
| Agent runtime | Propose, retrieve, compile, explain | Self-approve durable assertions |
| Application API | Enforce policy and transactional writes | Accept unscoped or unauthenticated writes |
| Managed MCP Server | Read-only inspection and database operations allowed by configured role | Become the ordinary end-user write path |
| Infrastructure operator | Maintain services and inspect operational health | Impersonate product users or mutate user continuity casually |
| Model provider | Process bounded prompts | Receive unneeded secrets or become durable storage |

## Consent boundary

Durable memory promotion requires an explicit user decision. The following are not consent:

- a model confidence score
- repeated mention
- a semantic match
- silence
- continued conversation
- a provider-generated summary

Project facts and personal identity claims are separate categories. The hackathon slice should remain project-scoped and avoid durable personal trait inference.

## Least privilege

Recommended database roles:

- `app_runtime`: scoped read/write on application tables
- `mcp_inspector`: read-only access to demo-safe schemas and views
- `migration_admin`: schema changes only during controlled deployment
- `proof_runner`: read access to proof views and trace records

Credentials must not be committed to the repository or exposed in the demo video.

## Public demo posture

- use seeded synthetic project data
- provide bounded test credentials if authentication exists
- prevent arbitrary SQL and unrestricted tenant enumeration
- rate limit public mutation routes
- avoid personal or Codexify production data
- keep MCP inspection read-only
- rotate demo credentials after judging

## Data classification

| Class | Examples | Default handling |
|---|---|---|
| Public demo | Synthetic project events and briefs | May be shown publicly |
| Project-private | Decisions, constraints, artifacts | Project-scoped access |
| Restricted | Secrets, credentials, sensitive personal data | Reject or isolate; never include in model context by default |
| Operational | traces, receipts, provider errors | Operator-scoped; redact secrets |

## Threats and controls

| Threat | Control |
|---|---|
| Prompt injection asks agent to rewrite memory | API-only governed writes and approval gate |
| Cross-project retrieval leakage | project-scoped filters before vector ranking |
| Duplicate retries create inconsistent truth | durable idempotency keys and receipts |
| Operator access becomes user authority | separate roles and audit logs |
| Model output is mistaken for proof | evidence classification and provenance links |
| Public demo exposes secrets | synthetic data, secret scanning, environment-managed credentials |
| Revoked memory remains active | lifecycle filters and snapshot freshness checks |
| Imported history appears native | explicit import lineage and UI labels |

## Audit requirements

Security-relevant actions should record:

- actor and authority role
- project scope
- operation kind
- target entity
- before and after lifecycle state
- idempotency key and receipt
- timestamp
- request and attempt identifiers
- result and failure class

Audit logging must not record raw secrets, hidden chain-of-thought, or unnecessary source content.
