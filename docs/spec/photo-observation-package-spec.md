---
pdm_version: "0.1"
id: "rda-photo-observation-package"
name: "Photo Observation Package"
slug: "photo-observation-package"
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
    target: "rda-observation-model"
  - type: "depends_on"
    target: "rda-definition-registry"
---

# Photo Observation Package

## Purpose

This document defines the first portable serialization profile for RDA Observation data.

The working format name is **Photo Observation Package (POP)**.

POP exists to move, cache, inspect, archive, and present mechanically derived photographic observations to downstream reasoning systems without requiring those systems to open or decode the original RAW directly.

POP is not the RDA domain model. It is one serialization of domain objects defined elsewhere.

## Scope

POP v0.1 serializes references or records for:

- Source Artifacts;
- semantic Registry closure;
- Procedure Implementations;
- Observation Runs;
- Procedure Invocations;
- Signal States;
- Observation instances;
- Derived Representation assets;
- asset digests and locators.

POP v0.1 intentionally excludes:

- Development Context such as `_Fundamental`;
- AI prompts or model-specific request format;
- Interpretation;
- Development Decision;
- Lightroom/XMP settings;
- final rendered images unless they are explicitly included as separately typed downstream artifacts.

A higher-level request envelope MAY carry POP plus Development Context, but those typed objects remain separate.

## Requirements

### Package semantics

A POP consumer MUST derive meaning from the manifest and Registry references, not from filenames, directory names, image appearance, or undocumented conventions.

Every observation instance MUST resolve to an Observation Definition.

Every Measurement or quantitative Derived Representation whose interpretation depends on processing state MUST resolve to the applicable Signal State.

Every derived observation MUST resolve to the Procedure Invocation / Observation Run provenance that produced it.

### Source preservation

POP does not require embedding the original RAW.

A Source Artifact reference SHOULD contain at least one cryptographic content digest when source bytes are available.

Embedding a RAW in a package does not make the embedded copy a different Source Artifact when the bytes are identical.

Any byte-changing source conversion is represented as a distinct Source Artifact with explicit lineage outside or inside the package.

### Exact values

POP MUST preserve exact source values when the source semantics are exact.

In particular, a rational source value MUST NOT be irreversibly converted to binary floating point merely for JSON convenience.

The canonical v0.1 rational representation is conceptually:

```json
{
  "kind": "rational",
  "numerator": 1,
  "denominator": 125
}
```

The denominator MUST NOT be zero.

An AI input projection MAY additionally compute a floating-point approximation, but that approximation is a derived input view and does not replace the exact stored value.

### Local and persistent identity

Manifest object IDs are references, not human labels.

POP v0.1 uses one package-wide object-ID scope across Source Artifacts, Implementations, Runs, Procedure Invocations, Signal States, Observations, Assets, and Coordinate Spaces. Reusing the same object ID for two different manifest objects is invalid.

An implementation MAY use UUID URNs, content-addressed IDs, or package-local opaque identifiers.

The package MUST define reference scope unambiguously.

Cross-package durable references SHOULD use globally collision-resistant identifiers or content digests rather than package-local aliases.

### Package byte identity

The byte digest of a ZIP/TAR/directory serialization is not the semantic identity of an Observation Set.

Archive order, compression, timestamps, or container metadata may change while the represented Observation Set remains semantically equivalent.

POP v0.1 therefore does not define a canonical package-byte serialization or semantic digest.

Individual Source Artifacts and binary assets SHOULD be content-addressed independently.

## Logical manifest model

A POP manifest contains the following logical collections.

### Source Artifacts

Each source record identifies an immutable source content object.

Suggested fields include:

- `source_id`;
- content digests;
- media type;
- byte length;
- optional source lineage references;
- optional non-authoritative locator hints.

A source path is not source identity.

### Semantic Closure

The semantic closure carries or identifies the Definition Registry material required to interpret the package.

It SHOULD include:

- Registry identity;
- Registry release version;
- Registry namespace and status;
- Registry bundle digest when available;
- exact referenced Definition ID/version records.

The archival profile MUST NOT require a live network lookup to understand the meaning of persisted observation values.

Until Registry canonicalization is finalized, POP MAY embed the exact referenced definition objects directly.

### Procedure Implementations

Implementation records identify executable realizations of Analysis Procedure Definitions.

Suggested fields include:

- implementation ID;
- implementation name;
- release/version;
- immutable build/source revision when available;
- implementation digest when available;
- materially relevant decoder/library dependencies.

Implementation identity is not Analysis Procedure identity.

### Observation Runs

A Run records an execution event.

Suggested fields include:

- run ID;
- implementation reference;
- source inputs;
- start/end timestamps when known;
- environment details only when materially relevant;
- Run-level configuration.

A repeated execution is a new Run even when it produces identical results.

### Procedure Invocations

An Observation Run MAY invoke one or more registered procedures.

Each invocation records:

- invocation ID;
- Run reference;
- Analysis Procedure Definition reference;
- runtime parameters;
- declared input bindings;
- produced Observation IDs and/or Signal State IDs where convenient.

Input bindings SHOULD be role-qualified rather than represented only as an ordered list. This is required for durable multi-input semantics such as `query` versus `candidate`, `left` versus `right`, source versus reference, or other directional comparisons.

A role-qualified binding conceptually contains:

```json
{
  "role": "query",
  "ref": "source-or-derived-object-id"
}
```

If a procedure definition declares ordered/role-specific inputs, the invocation MUST preserve those roles.

The runtime parameters MUST preserve values that materially affect output.

### Signal States

A Signal State binds a Signal Domain Definition to concrete processing/source parameters.

A Signal State record includes:

- signal-state ID;
- Signal Domain Definition reference;
- source/parent representation reference;
- concrete state properties;
- producing Procedure Invocation when derived.

The `properties` object is validated against the referenced Signal Domain Definition contract by semantic validation, not merely by the POP structural schema.

### Observations

An Observation instance includes:

- observation ID;
- Observation Definition reference;
- validity/status;
- Procedure Invocation reference;
- Signal State reference when required;
- exact value or asset reference when known;
- source locator for Source Assertions when applicable;
- spatial scope when applicable;
- uncertainty when applicable.

The status vocabulary is:

- `known`;
- `unknown`;
- `unsupported`;
- `unavailable`;
- `not_applicable`.

A non-`known` observation MUST NOT fabricate a zero, empty string, false, or placeholder value.

### Binary Assets

Derived Representations are stored as binary assets independently of their semantic role.

An asset record includes:

- asset ID;
- content digest(s);
- media type;
- byte length when known;
- encoding/compression metadata when material;
- dimensions/shape when material;
- lossiness declaration;
- package or external locator.

The Observation Definition tells the consumer what the asset means.

The asset filename does not.

## Asset storage profile

For a directory or archive representation, v0.1 SHOULD use a content-oriented layout such as:

```text
manifest.json
objects/
  sha256/
    <digest>
```

This layout is a transport convention, not domain semantics.

Implementations MAY expose human-friendly aliases such as:

```text
views/neutral.webp
views/highlight.webp
```

but aliases are non-authoritative and MUST resolve to manifest assets.

A package consumer MUST protect against path traversal and MUST NOT trust manifest paths as safe filesystem destinations without validation.

## Value representation

POP supports JSON-native scalar/structured values plus exact typed values.

### Rational

```json
{
  "kind": "rational",
  "numerator": -1,
  "denominator": 3
}
```

### Asset reference

```json
{
  "kind": "asset_ref",
  "asset_id": "asset-..."
}
```

Additional exact value kinds MAY be introduced by compatible schema evolution.

Consumers MUST NOT infer an Observation Definition solely from value shape.

## Spatial semantics

A POP MAY declare coordinate-space records and spatial-scope objects.

Whenever an observation or representation is spatial, it MUST identify enough information to relate its coordinates to the applicable source or derived representation.

A spatial map MUST NOT silently assume:

- orientation;
- active area;
- crop;
- resize;
- pixel-center convention;
- normalized-coordinate convention.

POP v0.1 permits extension fields for these details while the coordinate-space contract is still being stabilized.

## Color semantics

A visual Derived Representation MUST declare or resolve the color/signal state required to interpret it.

A display preview SHOULD identify:

- color space/profile;
- transfer function;
- white-balance state;
- tone transform;
- bit depth / encoding range where material.

A quantitative map encoded in an image container MUST additionally define how stored sample values map to the represented quantity.

Lossy encoding MUST NOT be used for a quantitative map unless the Observation Definition explicitly permits and bounds the loss.

## AI input projection

POP is not an AI prompt format.

An **Input View** MAY select and transform a subset of POP for a specific reasoning actor.

Examples include:

- selected scalar observations as JSON;
- a 512 px diagnostic preview;
- a compact luminance map;
- textual descriptions of Registry definitions.

The Input View SHOULD receive its own identity/digest so a future evaluator can determine exactly what the actor saw.

A machine Interpretation or Development Decision that consumed only an Input View MUST NOT claim that the actor directly inspected the complete POP.

## Privacy

A POP can contain sensitive information such as timestamps, GPS, serial numbers, identity metadata, faces, or location-bearing imagery.

A POP export profile MAY redact or omit such items.

Redaction is an export operation. It MUST be explicit and MUST NOT rewrite the semantic definition of a retained observation.

A redacted package SHOULD retain enough information to distinguish:

- observation not present because source lacked it;
- observation unsupported by the analyzer;
- observation intentionally omitted by export/privacy policy.

The exact privacy-redaction representation remains provisional in v0.1.

## Semantic validation

Structural JSON Schema validation is insufficient.

A conforming POP semantic validator MUST eventually verify at least:

1. all object IDs are unique within their declared scope;
2. all internal references resolve;
3. every Definition Reference resolves through the semantic closure/Registry;
4. multi-input procedure invocations preserve required input roles;
5. Observation value shape conforms to its Observation Definition;
6. non-`known` observations do not carry fabricated values;
7. Measurements requiring Signal State have one;
8. Signal State properties satisfy the referenced Signal Domain Definition;
9. Procedure Invocations conform to their Analysis Procedure Definitions;
10. derived observations resolve to a producing invocation/run;
11. asset references resolve and digest checks succeed when bytes are present;
12. quantitative Derived Representations declare sufficient numeric/color semantics;
13. source assertions retain a source locator when the procedure can provide one.

These checks will be promoted into stable finding codes and fixtures before POP v0.1 is declared stable.

## Initial profile

The first practical POP profile SHOULD contain:

- the initial Exif Source Assertions;
- Source Artifact digest/metadata;
- exact Run and procedure provenance;
- later, carefully defined RAW measurements;
- later, low-cost diagnostic Derived Representations.

The project MUST NOT make placeholder luminance/noise/headroom semantics stable merely to populate the package.

## Preservation rule

A preserved POP plus its Source Artifact should remain understandable even if:

- the original analyzer implementation is unavailable;
- current RDA code no longer exists;
- Lightroom/XMP no longer exist;
- current AI systems no longer exist;
- the project website has moved.

Long-term interpretation therefore depends on embedded/resolvable semantic definitions and provenance, not on contemporary software behavior.
