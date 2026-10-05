---
pdm_version: "0.1"
id: "rda-adr-observation-boundary"
name: "Separate Observation from Interpretation and Development"
slug: "separate-observation-from-interpretation"
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

# ADR: Separate Observation from Interpretation and Development

## Context

The initial use case is practical: inspect a camera RAW file with low-cost mechanical tooling, provide compact evidence to an AI, have the AI propose development adjustments relative to a baseline such as `_Fundamental`, and encode the result as Adobe XMP so that Lightroom development starts closer to the photographer's preferred state.

A direct implementation could combine all of these concerns into one analyzer output. That would be fast to prototype but would bind long-lived data to current AI behavior, current Adobe controls, and current interpretation heuristics.

The project intends to remain useful across major changes in software and photographic technology.

## Decision

The architecture SHALL separate these semantic dependencies:

```text
Source Artifact
  -> Observation Run
  -> Observation Set
  -> Interpretation
  -> Development Decision
  -> Target Encoding
  -> optional Rendered Result
```

This is not a mandatory linear workflow. The system SHALL model provenance as a dependency graph so that interpretations can request further observation, repeated runs can coexist, and decisions can be revised after rendering or evaluation.

Development Context is supplied to Interpretation and/or Development Decision, not to Observation.

The mechanical analyzer SHALL execute declared Analysis Procedures and produce Observation Sets through explicit Observation Runs. It SHALL NOT silently emit development judgments as measurements.

AI SHALL consume observations and context as an Interpretation/Decision actor. It SHALL NOT be treated as the producer of source facts merely because it can inspect images.

Adobe XMP SHALL be treated as a Target Encoding, not as the canonical development model.

A Photo Observation Package (POP) MAY be defined as a portable serialization of an Observation Set plus its Derived Representations and execution provenance. POP SHALL NOT itself become the Core domain model.

## Why

This separation allows each layer to evolve independently:

- RAW decoding can improve without changing development policy, while old and new Observation Runs remain distinguishable.
- AI can change without regenerating the meaning of source measurements.
- Lightroom can disappear without invalidating stored observations and decisions.
- a photographer's baseline profile can evolve without contaminating source analysis.
- human decisions and AI decisions can be compared under a common evaluation model.
- historical results remain explainable because provenance crosses explicit boundaries.

## Consequences

### Positive

- lower coupling between photographic evidence and current development tools;
- reproducible analyzer testing;
- explicit evaluation of AI reasoning versus mechanical extraction;
- reusable observations for search, archival inspection, culling, or future tasks;
- safer schema evolution;
- clear location for vendor-specific behavior.

### Cost

- more explicit data structures and provenance;
- some values must be duplicated as references across stage boundaries;
- MVP code may appear more complex than a single script;
- target-neutral intent abstractions cannot pretend that all vendor controls have equivalent semantics.

These costs are accepted because long-term interpretability is a primary project requirement.

## Rejected alternatives

### AI directly reads RAW and emits XMP

Rejected as the architectural Core because it collapses source decoding, visual evidence, interpretation, and target encoding into one opaque actor.

It remains valid as an experiment or benchmark.

### Mechanical analyzer emits "underexposed", "backlit", or "too warm"

Rejected from Core Observation because these labels already contain interpretation.

An analyzer extension MAY emit such assertions, but they are classified as Interpretation and carry separate provenance.

### Put `_Fundamental` inside the observation package as if it were part of source analysis

Rejected because changing a preferred baseline must not change what was observed from the RAW.

The exact baseline revision belongs to Development Context.

### Make Lightroom slider values the canonical development model

Rejected because slider semantics are vendor/process-version specific and may not map cleanly to another renderer.

## Review trigger

Revisit this decision only if evidence shows that the separation itself prevents a required use case. A new AI capability, decoder, camera format, or application is not by itself a reason to collapse the boundary.
