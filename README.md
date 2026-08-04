# Cockroach Continuity

A continuity ledger for resilient AI systems. Tracks identity, memory provenance, approvals, and runtime state so intelligence can survive restarts, provider changes, and infrastructure failures using CockroachDB as a globally consistent foundation.

## Architecture

The architecture corpus lives in [`docs/architecture/`](docs/architecture/README.md).

Start with:

1. [`00-current-state.md`](docs/architecture/00-current-state.md) for what is actually implemented.
2. [`01-system-overview.md`](docs/architecture/01-system-overview.md) for the target shape.
3. [`Architecture-Decision-Hub.md`](docs/architecture/Architecture-Decision-Hub.md) for proposed decisions.
4. [`source-adoption-matrix.md`](docs/architecture/source-adoption-matrix.md) for concept provenance and hackathon disclosure.

The architecture documents are design contracts. They do not, by themselves, prove runtime implementation.
