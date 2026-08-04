# ADR-007: Models Are Replaceable Compute

## Status

Proposed

## Date

2026-08-02

## Context

Continuity tied to one model, provider session, prompt cache, or hidden chat transcript does not survive provider changes and cannot be inspected independently.

## Decision

Models and embedding providers are adapters behind explicit interfaces. They may propose candidates and compile briefs, but they own no durable continuity state.

Provider changes must not require rewriting project events, assertions, or approvals.

## Invariants

- provider-local memory is never canonical
- prompt and KV caches are runtime optimization only
- provider metadata is recorded on attempts and derived outputs
- durable state is rehydrated from CockroachDB
- a provider switch must preserve source provenance

## Consequences

Adapter contracts add work, but the central demo becomes possible: the project resumes coherently after a model switch.

## Source lineage

Derived from the Codexify continuity thesis and provider-boundary doctrine.
