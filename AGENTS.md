# Cockroach Continuity Agent Contract

## Mission

Build the hackathon vertical slice defined by `docs/architecture/` without reopening accepted boundaries unless implementation evidence proves a contradiction.

## Execution law

1. Work in checklist order from `docs/hackathon-build/checklist.md`.
2. Keep each change bounded to one checklist item or one prerequisite fix.
3. Run the item's verification before marking it complete.
4. Preserve `project_event_id` across retries; create a new execution-attempt identity for each attempt.
5. Never promote model output to durable continuity without an explicit user approval decision.
6. Retrieval selects evidence; it never grants truth or write authority.
7. CockroachDB is the canonical continuity store. Container files, caches, prompts, and provider memory are not canonical.
8. Keep application writes behind the governed API. Managed MCP remains read-only for the baseline demo.
9. Do not introduce Redis, Neo4j, browser capture, multi-user collaboration, or extra deployment services unless a failing proof requires an ADR change.
10. Any copied or adapted Codexify runtime code must be recorded in `docs/architecture/source-adoption-matrix.md` before merge.
11. `docs/architecture/00-current-state.md` may advance only with a governing commit and reproducible proof command.
12. On failure, record the blocker and preserve the last verified state. Do not paper over a failed proof with documentation language.

## Stable commands

```bash
make bootstrap
make lint
make typecheck
make test
make up
make smoke
make down
```

## Definition of done for the hackathon slice

A fresh session using a different model/provider can reconstruct a provenance-backed continuity brief from CockroachDB-approved project state, rejected candidates remain excluded, duplicate writes remain idempotent, and a read-only MCP inspector can show the durable path without bypassing application authority.
