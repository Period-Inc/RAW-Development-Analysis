---
pdm_version: "0.1"
id: "rda-search-foundation-plan"
name: "Image Comparison and Retrieval Foundation Plan"
slug: "image-comparison-retrieval-foundation"
type: "planning.plan"
status: "active"
created_at: "2026-09-26"
updated_at: "2026-09-26"
owners:
  - "Period-Inc"
relations:
  - type: "depends_on"
    target: "rda-comparison-retrieval-foundation"
  - type: "depends_on"
    target: "rda-photo-observation-package"
---

# Image Comparison and Retrieval Foundation Plan

## Objective

Establish the minimum reusable technical foundation for image identity, similarity, candidate retrieval, and explainable search without committing to a commercial service or UI.

The first goal is not "build a Google Images competitor." It is to prove that RDA observations and fingerprints can support efficient multi-stage retrieval over a local archive with traceable semantics.

## Scope

In scope:

- exact-content identity;
- near-duplicate / derivative matching;
- typed fingerprints;
- structured parameter filtering;
- pairwise comparison records;
- index abstraction;
- candidate retrieval;
- explainable multi-stage ranking;
- local/on-premise execution;
- benchmark/evaluation fixtures.

Out of scope:

- consumer-facing search UI;
- SaaS architecture;
- billing/auth/customer model;
- web crawling;
- internet-scale image ingestion;
- proprietary service integrations.

## Steps

### 1. Establish benchmark image relationships

Create a controlled fixture family containing:

- byte-identical copy;
- metadata-only rewrite;
- JPEG recompression;
- resize;
- crop;
- rotation/orientation normalization;
- color/tone adjustment;
- monochrome conversion;
- unrelated visually similar image;
- unrelated semantically similar image;
- clearly unrelated image.

The benchmark must distinguish known lineage from merely visual similarity.

### 2. Define byte identity

Use cryptographic content digests as the exact-identity baseline.

This is not a learned fingerprint and should remain the strongest answer to "are these bytes identical?"

### 3. Evaluate derivative fingerprints

Test provisional fingerprints for resilience to common asset transformations.

Candidates may include:

- perceptual hash families;
- local-feature descriptors;
- geometric feature matching;
- compact global tone/color/spatial signatures.

Do not stabilize one fingerprint simply because a library exposes it.

Measure which transformations each fingerprint is intentionally invariant or sensitive to.

### 4. Separate fingerprint retrieval from comparison

For each candidate method document whether it is intended for:

- bucket/candidate lookup;
- approximate nearest-neighbor retrieval;
- pairwise similarity scoring;
- geometric verification;
- identity/derivation evidence.

A candidate-retrieval fingerprint must not automatically be treated as a calibrated similarity score.

### 5. Define multi-dimensional comparison

Create provisional comparison definitions for distinct axes such as:

- tone;
- color;
- spatial layout;
- texture;
- local-feature/geometric correspondence;
- semantic embedding similarity where used.

Keep component scores separate.

Composite ranking experiments come later and must record weights/policy.

### 6. Build rebuildable indexes

Implement at least:

- structured parameter index;
- one fingerprint lookup index;
- one vector/ANN index if an embedding experiment is included.

Index records reference authoritative Observation/Fingerprint identities.

Delete/rebuild testing is required: loss of an index must not lose semantic source data.

### 7. Implement multi-stage candidate retrieval

Demonstrate a pipeline such as:

```text
archive
 -> structured predicates
 -> fingerprint/vector candidate retrieval
 -> expensive comparison/verification
 -> ranked result
```

Every stage records configuration/procedure identity.

### 8. Evaluate retrieval quality

Measure separately for each task:

- byte duplicate;
- derivative identification;
- crop/resize/recompression robustness;
- visual similarity;
- semantic similarity;
- structured-parameter retrieval.

Use task-specific precision/recall or ranked-retrieval metrics rather than one universal "image search accuracy" score.

### 9. Test local/on-premise operation

The baseline experiment must run without sending source images to an external hosted service.

Optional hosted/AI comparisons may be benchmark adapters, not dependencies.

### 10. Promote only demonstrated primitives

Promote a fingerprint/comparison procedure into the durable Registry only when:

- invariances and sensitivities are explicitly defined;
- fixture behavior is reproducible;
- its role (identity, candidate retrieval, similarity, verification) is unambiguous;
- evaluation demonstrates value;
- implementation replacement remains possible.

## Dependencies

- Core Domain
- Definition Registry
- POP
- Comparison / Retrieval Foundation specification
- controlled image fixture corpus
- local storage and indexing environment

## Completion

This plan is complete when the repository contains:

- a relationship-aware benchmark fixture manifest;
- exact identity baseline;
- at least one validated derivative fingerprint;
- at least two distinct comparison dimensions;
- rebuildable structured/fingerprint index implementation;
- multi-stage local retrieval demo;
- retrieval evaluation report;
- explicit promotion/rejection decisions for tested fingerprint/comparison definitions.
