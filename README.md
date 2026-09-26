# RAW Development Analysis

RAW Development Analysis is a long-lived domain and reference implementation for turning photographic source data into reproducible observations, interpretations, development decisions, and target-specific development artifacts.

The project deliberately separates four concerns that are often conflated:

1. **Source** — immutable captured data and source metadata.
2. **Observation** — reproducible, method-described measurements and derived evidence.
3. **Interpretation / Decision** — contextual reasoning about what the observations mean and what development action is desired.
4. **Target Encoding** — translation of a decision into a tool-specific representation such as Adobe XMP.

AI, Lightroom, XMP, a particular RAW decoder, and any specific camera format are replaceable participants. They are not the domain model.

## Foundation hierarchy

RDA separates the deepest principles from the evolving domain model:

```text
Foundational Axioms
        ↓
Core Domain
        ↓
Specifications / Profiles
        ↓
Serialization / Procedures / Implementations
        ↓
Applications / Services
```

The Foundational Axioms are the "core of the core": changing them is an identity-level change, not normal feature evolution.

The deepest preservation rule is:

> Preserve the distinction between the world, its records, our interpretations, and our decisions.

See `docs/spec/foundational-axioms-spec.md`.

## Core dependency model

A common execution path is:

```text
Source Artifact
  -> Observation
  -> Interpretation
  -> Development Decision
  -> Target Encoding
```

This is a dependency model, not a mandatory linear pipeline. Interpretation may request additional observations, decisions may be revised after rendering/evaluation, and multiple actors may operate on the same immutable observations.

A development context (for example a baseline preset) may inform interpretation and decision, but it never changes what was observed from the source.

## Longevity objective

The preservation horizon is intentionally extreme: **1,000 years**.

RDA does not assume that today's software, vendors, file formats, programming languages, storage systems, organizations, or even current project infrastructure will survive that horizon.

The design therefore optimizes for semantic recoverability across generations of implementations. It prefers explicit meaning, provenance, stable identities, open and inspectable representations, versioned definitions, reconstructable transformations, and preservation of ambiguity over dependence on contemporary tools.

The objective is not to keep one implementation running for 1,000 years. The objective is that a future system can still determine **what was observed, how it was produced, what was inferred, what was decided, and what remained unknown**.

## Documentation

Normative project documentation follows the Period Project Documentation Model (PDM). Canonical documentation is English unless explicitly stated otherwise.

Initial domain work is being developed under `docs/`.

## Current conformance surface

The repository now contains executable contracts for:

- the semantic Definition Registry;
- Photo Observation Package (POP) manifests;
- valid/invalid conformance fixtures for both layers.

Local validation commands:

```text
python -m pip install -e ".[dev]"
pytest
rda validate-registry
rda test-registry-fixtures
rda test-pop-fixtures
```

RAW measurements such as luminance percentiles, clipping/headroom, noise, and diagnostic transforms remain deliberately provisional until the base observation profile experiments define and verify their semantics.

See `docs/base-observation-profile-plan.md` for the next phase.

## Comparison and retrieval foundation

RDA is being kept as a technical foundation rather than a service definition.

The reusable foundation now distinguishes:

```text
Observation
  -> Fingerprint
  -> Comparison
  -> Index
  -> Candidate Retrieval
  -> Ranking / Verification
```

These are not collapsed into one opaque "similarity" concept.

Key rules:

- byte identity is different from likely same-image derivation;
- derivation is different from visual similarity;
- visual similarity is different from semantic similarity;
- candidate retrieval is different from expensive pairwise verification;
- component similarity dimensions should be preserved instead of only one composite score;
- indexes are rebuildable projections/caches, not archival authority;
- hosted AI/vector/search providers are adapters, not Core dependencies;
- multi-input comparisons preserve explicit roles such as `query` and `candidate`.

See:

- `docs/spec/comparison-retrieval-foundation-spec.md`
- `docs/image-comparison-retrieval-foundation-plan.md`

## Experimental RAW decoder probe

Before stabilizing sensor-side measurement semantics, RDA can inspect the unpacked RAW state exposed by the current rawpy/LibRaw implementation without calling `postprocess()`.

Install the optional experiment dependency and run:

`pip install -e ".[raw]"`

`rda probe-raw /path/to/file.raw`

The resulting JSON records source digest, decoder version, visible sensor array shape/type, CFA/color-index metadata, black levels, white/saturation levels, and decoder-exposed dimensions.

This output is experimental instrumentation. It is not yet a stable Observation Profile.

See `docs/raw-decoder-characterization-plan.md`.
