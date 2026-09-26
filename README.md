# RAW Development Analysis

RAW Development Analysis is a long-lived domain and reference implementation for turning photographic source data into reproducible observations, interpretations, development decisions, and target-specific development artifacts.

The project deliberately separates four concerns that are often conflated:

1. **Source** — immutable captured data and source metadata.
2. **Observation** — reproducible, method-described measurements and derived evidence.
3. **Interpretation / Decision** — contextual reasoning about what the observations mean and what development action is desired.
4. **Target Encoding** — translation of a decision into a tool-specific representation such as Adobe XMP.

AI, Lightroom, XMP, a particular RAW decoder, and any specific camera format are replaceable participants. They are not the domain model.

## Core flow

```text
Source Asset
  -> Observation
  -> Interpretation
  -> Development Decision
  -> Target Encoding
```

A development context (for example a baseline preset) may inform interpretation and decision, but it never changes what was observed from the source.

## Longevity objective

The design target is measured in decades. The core therefore prefers semantic invariants, provenance, explicit measurement domains, stable identities, and versioned adapters over vendor controls or current AI APIs.

## Documentation

Normative project documentation follows the Period Project Documentation Model (PDM). Canonical documentation is English unless explicitly stated otherwise.

Initial domain work is being developed under `docs/`.
