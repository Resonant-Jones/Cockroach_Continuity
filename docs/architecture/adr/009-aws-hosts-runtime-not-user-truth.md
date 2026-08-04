# ADR-009: AWS Hosts the Runtime, Not User Truth

## Status

Proposed

## Date

2026-08-02

## Context

The hackathon requires meaningful AWS use. Treating a provider cache, container filesystem, or deployment platform as continuity ownership would weaken portability and create ambiguous failure semantics.

## Decision

AWS will host the application runtime, initially as an ECS Fargate service. Optional S3 storage may hold artifact bytes. Durable continuity remains in CockroachDB.

Runtime restarts must rehydrate project state from the canonical database.

## Invariants

- container-local files are not durable truth
- AWS service health is distinct from CockroachDB data health
- secrets are environment-managed
- a restart does not require provider-local memory
- AWS integration is meaningful but bounded

## Consequences

The deployment story is simple and honest. Cross-region application resilience remains outside the hackathon claim.

## Source lineage

Project-specific decision informed by Codexify's runtime and canonical-truth boundaries.
