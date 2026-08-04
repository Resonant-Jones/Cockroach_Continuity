# ADR-008: CockroachDB Is the Canonical Continuity Store

## Status

Proposed

## Date

2026-08-02

## Context

Splitting transactional approval state and semantic retrieval across unrelated stores creates consistency gaps, duplicate lifecycle rules, and harder provenance reconstruction.

## Decision

CockroachDB Cloud will be the canonical durable store for project events, attempts, candidates, approvals, assertions, provenance, snapshots, traces, receipts, and vector-searchable embeddings.

Optional object storage holds artifact bytes only. No graph store is required for baseline continuity.

## Invariants

- approval and assertion writes are transactional
- vector retrieval respects structured lifecycle and scope filters
- object storage references preserve hashes and provenance
- caches and queues are not canonical truth
- the application works without an optional graph system

## Consequences

Schema and vector index design become central to the project, which directly supports the hackathon's agentic memory criteria.

## Source lineage

Adapted from Codexify's Postgres system-of-record posture, continuity storage proposal, ADR-030, and ADR-031. The CockroachDB selection is project-specific.
