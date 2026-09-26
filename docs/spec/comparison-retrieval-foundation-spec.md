---
pdm_version: "0.1"
id: "rda-comparison-retrieval-foundation"
name: "Comparison, Fingerprint, Index and Retrieval Foundation"
slug: "comparison-retrieval-foundation"
type: "specification.core"
status: "active"
created_at: "2026-09-26"
updated_at: "2026-09-26"
owners:
  - "Period-Inc"
relations:
  - type: "depends_on"
    target: "rda-core-domain"
  - type: "depends_on"
    target: "rda-definition-registry"
---

# Comparison, Fingerprint, Index and Retrieval Foundation

## Purpose

This document defines the durable semantic boundary between image observation, compact fingerprints, similarity evaluation, indexes, and retrieval.

The goal is to let RDA support image-search and archive use cases without turning any current embedding model, vector database, perceptual hash, ANN algorithm, or commercial search product into Core semantics.

## Scope

This specification covers:

- single-asset fingerprints;
- exact/near-duplicate identity evidence;
- pairwise and multi-input comparison;
- similarity dimensions;
- candidate retrieval;
- indexes as rebuildable projections;
- query intent and filters;
- ranked retrieval results;
- provenance and explainability requirements.

It does not define a user-facing search service, UI, deployment product, commercial API, or one universal similarity metric.

## Requirements

RDA MUST distinguish:

1. **Observation** — information about one or more declared inputs.
2. **Fingerprint** — a compact Derived Representation designed for efficient comparison/retrieval.
3. **Comparison** — an explicit relation measured between declared inputs.
4. **Index** — a rebuildable acceleration structure derived from observations/fingerprints.
5. **Retrieval** — a procedure that uses query constraints and one or more indexes to produce candidates.
6. **Ranking / Similarity Evaluation** — a separate evaluation that may reorder or filter candidates.

A retrieval result MUST NOT be interpreted as proof of identity or semantic equivalence merely because it was highly ranked.

## Fingerprint

A Fingerprint is a Derived Representation optimized for matching, retrieval, or comparison.

A Fingerprint MUST identify:

- its Observation Definition;
- the Source Artifact or Derived Representation from which it was produced;
- the Analysis Procedure Definition;
- Procedure Implementation and Run provenance;
- parameters that materially affect matching behavior;
- representation format and dimensionality/shape where applicable.

Examples MAY include:

- cryptographic digest;
- perceptual hash;
- local-feature signature;
- color/tone signature;
- spatial-layout signature;
- frequency signature;
- learned embedding;
- compound fingerprint containing several typed components.

A Fingerprint is not automatically human-interpretable. Its semantics are defined by its Observation Definition and procedure contract.

## Identity Fingerprints and Similarity Fingerprints

RDA distinguishes two goals that are often conflated.

### Identity / derivation matching

The question is:

> Is this the same source content, or is it likely derived from the same underlying image?

Relevant techniques may include:

- cryptographic digest for byte identity;
- perceptual hashes resilient to resizing/compression;
- local-feature matching;
- geometric consistency;
- crop/transform matching;
- lineage metadata.

A result can support evidence for:

- byte-identical copy;
- likely same-image derivative;
- transformed/cropped derivative;
- unresolved relationship.

It MUST NOT silently equate "very visually similar" with "same origin".

### Similarity matching

The question is:

> In what defined sense are these distinct images similar?

Possible dimensions include:

- tone;
- color;
- spatial composition;
- texture;
- local feature arrangement;
- capture conditions;
- semantic subject/content;
- development/rendering appearance.

Each dimension requires an explicit definition/procedure.

RDA MUST NOT require all similarity dimensions to collapse into one scalar.

## Comparison

A Comparison is a relational observation whose inputs are explicit.

Pairwise form:

```text
Input A
Input B
   ↓
Comparison Procedure
   ↓
Comparison Observation Set
```

A Comparison result MUST identify input roles and order semantics.

If a metric is symmetric, its definition SHOULD say so.

If a metric is directional, the roles MUST remain distinct.

Example result structure may conceptually include:

```text
tone_similarity        0.91
color_similarity       0.34
spatial_similarity     0.82
semantic_similarity    0.20
identity_confidence    0.03
```

These values are illustrative. Their meanings depend entirely on registered definitions.

## Composite similarity

A consumer MAY combine multiple similarity dimensions.

A composite score MUST identify:

- component definitions;
- normalization;
- weights;
- missing-component behavior;
- combination procedure/version.

The composite score is itself a derived comparison observation.

A product MAY choose its own weighting policy without changing lower-level observations.

Core SHOULD prefer preserving component measurements over storing only the composite.

## Index

An Index is a materialized, rebuildable projection over Source Artifacts, Observations, Fingerprints, or other derived records.

Examples:

- B-tree / relational structured index;
- inverted index;
- locality-sensitive hash table;
- vector index;
- ANN graph;
- fingerprint posting list;
- geospatial/time index.

An Index MUST NOT be treated as the authority for the underlying observation meaning.

The authoritative chain remains:

```text
Source / Observation / Fingerprint definitions + provenance
                ↓
              Index
```

If an Index is lost, the system SHOULD be able to rebuild it from preserved authoritative records.

An Index definition/configuration SHOULD identify:

- indexed definition IDs/versions;
- index implementation and version;
- preprocessing/projection rules;
- parameters affecting recall/order;
- source snapshot/revision;
- build time and build provenance.

## Candidate Retrieval

Candidate Retrieval exists to reduce the search space.

It MAY combine cheap mechanisms such as:

- structured parameter filtering;
- time/camera/focal-length predicates;
- bucketed tone/color statistics;
- fingerprint lookup;
- inverted/local-feature matching;
- approximate nearest-neighbor vector search.

Candidate Retrieval is allowed to be approximate.

Therefore a candidate set means:

> These items passed this retrieval procedure under this configuration.

It does not mean:

> These are the only truly similar items.

Recall/precision characteristics belong to evaluation, not to the semantic meaning of the source observations.

## Multi-stage retrieval

RDA explicitly supports staged retrieval.

For example:

```text
1,000,000 assets
   ↓ structured / cheap parameter filters
20,000 candidates
   ↓ fingerprint / ANN retrieval
500 candidates
   ↓ expensive comparison / multimodal reasoning
50 ranked results
```

Each stage SHOULD preserve its procedure/configuration identity.

This allows a local/on-premise system to minimize expensive AI or GPU inference while retaining traceable search behavior.

## Query

A Query is typed search intent plus constraints.

Core recognizes that a query may contain different kinds of conditions:

- exact structured predicates;
- numeric ranges;
- similarity-to-example constraints;
- identity/derivation constraints;
- semantic text interpreted into structured constraints;
- ranking preferences.

A natural-language query is not itself a canonical observation.

If AI translates natural language into query constraints, the translation is an Interpretation/Query Projection with its own provenance.

The executed retrieval query SHOULD preserve the resolved machine constraints so that the result can be reproduced independently of the language model.

## Retrieval Result

A Retrieval Result records:

- query identity/resolved constraints;
- index snapshot(s);
- retrieval procedure/version;
- candidate identities;
- candidate scores/distances when meaningful;
- ranking procedure/version when applied;
- truncation/top-k behavior;
- execution provenance.

A result rank is contextual to that query and procedure.

It MUST NOT be stored as an intrinsic property of a Source Artifact.

## Search by parameter before expensive similarity

RDA SHOULD support structured observations as first-class search predicates.

This enables inexpensive coarse filtering before more costly comparison.

For example, a consumer may filter by:

- capture date range;
- focal-length range;
- aspect/orientation;
- tone distribution;
- color distribution;
- source/reporting metadata;
- spatial statistics;
- semantic assertions from a separate Interpretation layer.

This staged design is especially suitable for large archives and on-premise operation.

## Explainability

A search system SHOULD be able to explain a result at the level supported by its procedures.

Examples:

- "same perceptual fingerprint family";
- "high tone similarity, low color similarity";
- "candidate selected by focal-length/tone filter, then ranked by embedding";
- "likely derivative: strong local-feature correspondence after crop/resize normalization".

A black-box embedding MAY still be used, but the system MUST NOT fabricate semantic explanations that the embedding procedure does not actually provide.

## On-premise compatibility

No Core retrieval capability requires a hosted service.

The following can all be implemented locally:

- Observation generation;
- Fingerprint generation;
- structured indexes;
- vector indexes;
- candidate retrieval;
- similarity evaluation;
- optional local AI interpretation.

Hosted AI/search providers MAY be adapters, never Core dependencies.

## Preservation rule

Long-term preservation SHOULD prioritize:

1. Source Artifacts;
2. durable Observation / Fingerprint definitions;
3. Observation and Fingerprint records with provenance;
4. enough procedure/build metadata for interpretation/reproduction;
5. index configuration when operationally useful.

Indexes themselves are caches/projections and MAY be discarded/rebuilt.

A 50-year archive should not become unreadable because a particular vector database or embedding vendor ceased to exist.
