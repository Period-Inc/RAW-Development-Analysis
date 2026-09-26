---
pdm_version: "0.1"
id: "rda-evolution-policy"
name: "Core Evolution and Compatibility Policy"
slug: "evolution-policy"
type: "specification.core"
status: "active"
created_at: "2026-09-26"
updated_at: "2026-09-26"
owners:
  - "Period-Inc"
relations:
  - type: "depends_on"
    target: "rda-core-domain"
---

# Core Evolution and Compatibility Policy

## Purpose

This document defines how RAW Development Analysis can evolve for decades without requiring old observations, decisions, or artifacts to be reinterpreted under new semantics.

## Principle

Semantic meaning is more durable than field names, file layouts, libraries, or model APIs.

The project therefore versions definitions, procedures, schemas, and adapters independently.

## Compatibility layers

The system distinguishes five versioned layers:

1. **Core semantic model** — Source, Observation, Context, Interpretation, Decision, Target Model, Target Encoding, Evaluation.
2. **Definition registry** — stable identities for measurements, domains, procedures, intent types, and target semantics.
3. **Serialization schemas** — JSON/package/wire representations.
4. **Implementations** — analyzers, decoders, AI actors, renderers, adapters.
5. **Experimental profiles** — temporary combinations used for evaluation.

A change in one layer MUST NOT imply a version change in all other layers.

## Stable identity

Definitions that may be referenced historically MUST have stable identifiers independent of:

- display names;
- filesystem paths;
- source-code symbols;
- package filenames;
- current implementation language.

A definition ID MUST NOT be reused for materially different semantics.

Renaming a label does not require a new definition identity. Changing the meaning does.

## Semantic versioning

Schemas and registries SHOULD use semantic versioning.

- **Patch** — clarification or correction that does not change valid interpretation.
- **Minor** — additive, backward-compatible capability.
- **Major** — a breaking change to interpretation or required structure.

Implementation versions MAY follow their own release policy, but provenance MUST retain the exact version or immutable build identity used to produce stored derived data.

## Observation compatibility

Historical observations MUST be interpreted according to the definition and procedure versions recorded when they were created.

A newer analyzer MUST NOT silently rewrite the meaning of an older measurement ID.

If an improved algorithm produces a materially different measurement, it MUST do one of the following:

- publish a new procedure version under the same measurement definition when the measurement semantics remain identical;
- publish a new measurement definition when the semantics changed;
- explicitly publish a migration/equivalence rule when equivalence has been demonstrated.

"Better result" alone does not justify overwriting historical evidence.

## Recalculation

Observation data is normally regenerable from the Source Asset, but regeneration is not assumed to be bit-identical across time.

A regenerated Observation Set MUST carry a new provenance identity when any material procedure, dependency, parameter, or source representation changed.

Old and new Observation Sets MAY coexist.

## Serialization compatibility

A serialization format is a representation of domain data, not the domain authority.

Readers SHOULD:

- accept compatible minor versions;
- ignore unknown optional extension fields they do not understand;
- preserve unknown extension payloads when performing lossless read-modify-write operations;
- reject data when required semantics cannot be determined safely;
- never reinterpret an unknown field based solely on its name.

Writers SHOULD include enough schema and definition references to make the payload self-describing.

## Namespaced extensions

Experimental or vendor-specific data MUST use a namespace or extension identity that prevents collision with Core definitions.

Examples of extension ownership include:

- an analyzer family;
- a camera-maker decoder;
- an Adobe target adapter;
- an experiment;
- a future subject-detection module.

Promotion of an extension into Core requires a semantic review. Existing extension data remains valid under its original identity.

## Source identity and content addressing

When source bytes are available, Source Assets SHOULD use a cryptographic digest as a content identity component.

Derived binary assets such as maps and previews SHOULD also carry a digest.

Algorithms MUST be recorded by name (for example SHA-256) and not inferred from digest length.

A future hash migration MUST allow multiple digests to coexist.

## Time

Creation time, capture time, modification time, and analysis time are different concepts and MUST NOT share an ambiguous field.

Timestamps SHOULD carry timezone/offset when the source semantics provide one. Unknown timezone MUST remain unknown rather than being guessed.

## Units

Units MUST be explicit for values whose scale is not inherent.

The project SHOULD prefer established units where meaningful:

- seconds;
- millimetres;
- kelvin when a temperature model is actually being used;
- EV for logarithmic exposure differences;
- fractions/ratios for normalized proportions.

Unitless normalized numbers MUST define their domain and endpoints.

## Floating-point durability

Serialized floating-point measurements SHOULD preserve sufficient precision to reproduce the meaning of the measurement.

No Core contract may depend on exact binary equality of independently recomputed floating-point values unless the procedure explicitly guarantees it.

Evaluation procedures SHOULD define tolerances.

## Coordinate durability

Spatial definitions MUST not depend on a current UI convention.

Every spatial datum MUST reference a declared coordinate space and orientation/crop transform.

Future representations MAY add coordinate spaces without changing historical ones.

## Color durability

Color-space names MUST resolve to an explicit definition or recognized standard/profile.

A bare label such as `RGB`, `linear`, or `RAW color` is not a durable color definition.

If an ICC/DCP/profile or matrix is material to the computation, its identity or digest SHOULD be retained.

## AI evolution

AI model identities are implementation provenance.

No Core schema SHOULD contain fields whose meaning depends on the behavior of a named current model.

AI-generated Interpretations and Decisions SHOULD retain:

- model/provider or actor identity when known;
- model/version or immutable deployment identity when available;
- prompt/policy identity or decision-procedure identity when material;
- input Observation Set identity;
- Development Context identity.

A future non-AI actor MUST be able to occupy the same role.

## Vendor evolution

A Target Model definition MUST identify the process/version semantics required to interpret target-specific controls.

For example, an Adobe slider named `Highlights` is not assumed to mean the same function forever.

A target-specific value is only meaningful with the target/process definition that gives it semantics.

## Baseline profiles

A baseline profile such as `_Fundamental` is versioned Context.

Changing a baseline creates a new baseline identity or revision.

A baseline-relative delta MUST identify the exact baseline revision against which the delta is expressed.

## Deprecation

Core definitions SHOULD be deprecated before removal.

Deprecated data remains interpretable indefinitely when practical.

A deprecated definition MUST NOT be reassigned a new meaning.

Migration guidance SHOULD state whether migration is:

- lossless;
- approximate;
- impossible.

## Preservation principle

For long-term archival value, it is preferable to preserve an old, fully described result than to replace it with a newer result whose provenance is incomplete.

The system optimizes for explainability across time, not perpetual normalization to the newest implementation.
