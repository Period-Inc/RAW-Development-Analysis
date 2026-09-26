# RAW Development Analysis

RAW Development Analysis is a long-lived domain and reference implementation for turning photographic source data into reproducible observations, interpretations, development decisions, and target-specific development artifacts.

The project deliberately separates four concerns that are often conflated:

1. **Source** — immutable captured data and source metadata.
2. **Observation** — reproducible, method-described measurements and derived evidence.
3. **Interpretation / Decision** — contextual reasoning about what the observations mean and what development action is desired.
4. **Target Encoding** — translation of a decision into a tool-specific representation such as Adobe XMP.

AI, Lightroom, XMP, a particular RAW decoder, and any specific camera format are replaceable participants. They are not the domain model.

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

The design target is measured in decades. The core therefore prefers semantic invariants, provenance, explicit measurement domains, stable identities, and versioned adapters over vendor controls or current AI APIs.

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
