---
pdm_version: "0.1"
id: "rda-base-observation-profile-plan"
name: "Base RAW Observation Profile Plan"
slug: "base-observation-profile"
type: "planning.plan"
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
  - type: "depends_on"
    target: "rda-photo-observation-package"
---

# Base RAW Observation Profile Plan

## Objective

Define the first useful RAW-development Observation Profile without guessing measurement semantics.

The profile should give a reasoning actor enough compact information to propose useful development adjustments while remaining reproducible, explainable, and independent of Lightroom/XMP.

The first profile is successful when it can be generated from representative RAW files, serialized as conforming POP, consumed by an AI Input View, and evaluated against human development decisions.

## Scope

In scope:

- representative RAW fixture selection;
- reference-decode experiments;
- candidate Signal Domain Definitions and Signal States;
- exact definitions for initial tone/exposure measurements;
- diagnostic Derived Representations;
- POP generation;
- Input View generation;
- comparison with baseline-relative human development decisions.

Out of scope until evidence requires them:

- face/subject semantic detection;
- aesthetic scoring;
- scene classification;
- photographer-style learning;
- local masking;
- Lightroom-specific parameter optimization beyond the evaluation adapter;
- stable noise/sharpness definitions without empirical validation.

## Steps

### 1. Build a representative RAW fixture corpus

Select a deliberately small but diverse fixture set covering:

- multiple camera makers / RAW containers available to the project;
- low/high ISO;
- deep shadows;
- near-clipped highlights;
- mixed color channels near clipping;
- backlit subject;
- low dynamic-range scene;
- high dynamic-range scene;
- daylight / tungsten or otherwise materially different white-balance conditions.

Fixture source files remain outside Git when licensing/privacy/size requires it. The repository stores immutable digests, metadata, expected source identity, and fixture roles.

### 2. Record decoder provenance before choosing a decoder contract

Evaluate at least one practical RAW decoder implementation.

The experiment records:

- decoder/library version/build;
- which source metadata and sensor values are exposed;
- black/white-level behavior;
- active-area behavior;
- CFA/channel access;
- scaling/normalization behavior;
- demosaic and white-balance defaults;
- whether "no auto adjustment" is actually achievable;
- camera-specific fallbacks.

The implementation used for experiments is not promoted into Core semantics.

### 3. Define the minimum sensor-side Signal Domains

Candidate domains are tested before Registry promotion.

Likely candidates include:

- source sensor code values before black subtraction;
- black-subtracted sensor-linear values;
- black/white-normalized sensor-linear values;
- optional demosaiced camera-linear RGB.

For each candidate, determine exactly which Signal State properties are required to reconstruct meaning.

No domain is stabilized under an ambiguous label such as `raw-linear`.

### 4. Define initial tone measurements

Start with measurements whose mathematical meaning can be made explicit and whose development utility can be tested.

Candidate families:

- channel distributions / percentiles;
- near-saturation / saturation fractions;
- highlight headroom;
- shadow-floor statistics.

For each candidate:

1. define sample population;
2. define Signal State;
3. define masking / active-area treatment;
4. define exact statistic;
5. define unit/range;
6. implement at least one procedure;
7. test reproducibility;
8. test whether the measurement materially improves a development decision.

"Luminance percentile" is not promoted until luminance itself is unambiguous in the chosen domain.

### 5. Define diagnostic Derived Representations

Generate compact visual or quantitative views intended for reasoning rather than presentation.

Candidate views:

- neutral diagnostic preview;
- highlight-inspection preview;
- shadow-inspection preview;
- clipping/headroom map;
- low-resolution tone map.

Every view records its procedure, Signal State, transform, color semantics, dimensions, encoding, and lossiness.

Do not use undocumented camera JPEG rendering as the neutral RAW view. An embedded camera JPEG may be carried separately as a source-provided contextual rendering.

### 6. Generate conforming POP fixtures

For each representative RAW:

- create Source Artifact reference/digest;
- create implementation/run/procedure provenance;
- create Signal States;
- create observations;
- create derived assets;
- embed semantic closure;
- validate through `rda validate-pop`.

### 7. Build an AI Input View

Define a small model-facing projection from POP.

The first Input View should prefer:

- the small set of scalar observations demonstrated to matter;
- selected diagnostic previews/maps;
- exact Development Context supplied separately;
- clear definition summaries where the model needs semantic help.

Record the exact Input View identity/content so evaluation knows what the model actually saw.

### 8. Evaluate against development decisions

Use the existing baseline-development concept such as `_Fundamental` as Development Context, not as Observation.

For test images collect:

- baseline settings;
- AI-proposed baseline-relative decision;
- human final decision;
- rendered comparisons when useful.

Evaluate per adjustment/decision dimension instead of collapsing quality into one score.

A human final result is an evaluation reference for this workflow, not universal photographic truth.

### 9. Promote only demonstrated definitions

A candidate Observation Definition, Signal Domain Definition, or Analysis Procedure becomes stable only when:

- its semantics are explicit;
- representative fixtures validate it;
- independent recomputation can meet defined tolerance/equivalence;
- it provides demonstrated downstream value or necessary auditability;
- unresolved camera/decoder behavior is not hidden inside the definition.

## Dependencies

- Core Domain specification
- Definition Registry specification and validator
- POP specification and validator
- representative RAW source access
- at least one practical RAW decoder for experimentation
- target-side evaluation adapter for the current baseline/XMP workflow

## Completion

This plan is complete when the repository contains:

- a documented representative fixture corpus manifest;
- at least one validated sensor-side Signal Domain Definition;
- a small initial set of mathematically exact RAW measurements;
- at least one standardized diagnostic Derived Representation;
- conforming POP examples generated from real RAW files;
- a recorded AI Input View contract;
- an evaluation report comparing proposed development decisions with human decisions;
- explicit evidence supporting which candidate definitions were promoted, retained as provisional, or rejected.

Completion does not require a full automatic Lightroom-development system. It establishes the observation layer on which that system can be built safely.
