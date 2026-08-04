# ADR-011: Managed MCP Is an Inspection Boundary

## Status

Proposed

## Date

2026-08-02

## Context

The CockroachDB Managed MCP Server is a required technology candidate and a powerful operator interface. Using it as an unrestricted end-user write path would bypass application policy, approval transactions, and domain validation.

## Decision

The Managed MCP Server will be used as a read-only inspection and operations boundary for the hackathon baseline.

Application mutations will pass through the governed API. MCP access will demonstrate schema, events, assertions, snapshots, traces, indexes, and auditability to operators and judges.

## Invariants

- baseline MCP credentials are read-only
- MCP does not bypass project scope or tenant boundaries
- MCP queries are auditable
- application functionality does not depend on operator MCP access
- future write access requires a separate ADR and proof plan

## Consequences

The MCP integration is meaningful and visible without creating a second policy-evading write surface.

## Source lineage

Project-specific decision informed by Codexify's operator/user boundary and inspection-surface doctrine.
