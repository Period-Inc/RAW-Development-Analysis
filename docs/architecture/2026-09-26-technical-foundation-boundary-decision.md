---
pdm_version: "0.1"
id: "rda-adr-technical-foundation-boundary"
name: "Keep RDA as a Technical Foundation Independent of Services"
slug: "technical-foundation-boundary"
type: "architecture.decision"
status: "active"
created_at: "2026-09-26"
updated_at: "2026-09-26"
owners:
  - "Period-Inc"
relations:
  - type: "depends_on"
    target: "rda-core-domain"
---

# ADR: Keep RDA as a Technical Foundation Independent of Services

## Context

The Observation model developed for RAW development also supports broader image capabilities such as:

- parameter-based filtering;
- duplicate and derivative detection;
- image fingerprinting;
- similarity search;
- archival indexing;
- asset discovery;
- local/on-premise analysis and retrieval.

These capabilities suggest many possible services and products. Prematurely designing the Core around one service would couple long-lived image semantics to a short-lived product concept.

## Decision

RDA SHALL remain a **technical foundation**.

Its responsibility is to make image/source assets:

- observable;
- describable;
- comparable;
- indexable;
- traceable;
- reproducible;
- portable across implementations.

RDA MAY provide reusable primitives for:

- observations and derived representations;
- fingerprints;
- similarity measurements;
- candidate retrieval;
- structured parameter indexes;
- vector/feature indexes;
- lineage and duplicate detection;
- search/query adapters.

RDA SHALL NOT define a particular commercial service, UI, deployment model, customer segment, pricing model, or product workflow as Core semantics.

Possible downstream services include RAW development support, archive search, similarity search, enterprise asset discovery, on-premise image search, duplicate/derivative detection, and other applications not yet defined.

These are consumers of the technical foundation.

## Consequences

A future architecture can take the form:

```text
Source Assets
    ↓
RDA Observation / Fingerprint / Similarity Foundation
    ↓
Indexes and Retrieval
    ↓
Application / Service Layer
```

The same Observation Store can support multiple applications without each application redefining image analysis.

Service-specific requirements may introduce adapters, profiles, indexes, or projections, but they MUST NOT silently redefine Core Observation semantics.

Product discovery can therefore happen later, using evidence from actual technical capability rather than forcing the foundation to fit a speculative service.

This decision also preserves the option for fully local/on-premise deployments because Core analysis and indexing do not depend on a hosted AI or external search provider.
