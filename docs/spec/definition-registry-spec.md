---
pdm_version: "0.1"
id: "rda-definition-registry"
name: "Definition Registry"
slug: "definition-registry"
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
    target: "rda-evolution-policy"
  - type: "depends_on"
    target: "rda-observation-model"
---

# Definition Registry

## Purpose

The Definition Registry gives durable machine-resolvable identity to the semantic definitions used by RAW Development Analysis.

Its primary job is to ensure that a value recorded decades later can still answer:

- what the observation meant;
- in what signal domain it was meaningful;
- what procedure semantics produced it;
- which version of each semantic definition was intended.

The Registry is a semantic vocabulary. It is not a catalog of software releases, execution runs, files, AI providers, camera models, or current implementation preferences.

## Scope

The initial Registry governs three definition classes:

1. **Observation Definition** — what an observed value or derived representation means.
2. **Signal Domain Definition** — what class of signal/image state gives numeric values their meaning.
3. **Analysis Procedure Definition** — what computation/extraction/transformation method means independently of a concrete executable.

Future definition classes MAY be added when the Core introduces a durable semantic type that needs shared identity.

The Registry does not store:

- Procedure Implementations;
- Observation Runs;
- concrete Signal States;
- Source Artifacts;
- Development Context instances;
- AI model deployments;
- Target Encodings;
- current filesystem locations.

Those are runtime, artifact, context, or adapter records that reference Registry definitions where appropriate.

## Requirements

### Definition identity

Every durable definition MUST have:

- a stable `id`;
- an explicit `version`;
- a `kind`;
- a lifecycle/stability state;
- a normative semantic description;
- enough structured contract data to detect incompatible reuse.

The pair `(id, version)` identifies one immutable semantic definition.

A definition ID MUST NOT be reused for materially different meaning.

A released definition version MUST NOT be edited in place. Corrections or semantic changes create a new version.

### ID syntax

RDA-owned definition IDs use lower-case ASCII dotted identifiers:

```text
rda.<kind>.<semantic-path>
```

Initial kinds are:

- `rda.observation.*`
- `rda.signal-domain.*`
- `rda.procedure.*`

Path components MAY contain lowercase letters, digits, and hyphens.

Examples:

```text
rda.observation.capture.photographic-sensitivity-reported
rda.observation.tone.luminance-percentile
rda.signal-domain.sensor-mosaic-normalized
rda.procedure.metadata.exif-photographic-sensitivity
```

The ID is project-scoped semantic identity, not a URL.

A wire format MUST NOT require concatenating the version into the ID string. References SHOULD use an object equivalent to:

```json
{
  "id": "rda.observation.tone.luminance-percentile",
  "version": "1.0.0"
}
```

Human-facing notation such as `id@1.0.0` MAY be used for display only.

### Definition versioning

Definition versions use semantic versioning notation.

For Registry semantics:

- **PATCH** — editorial clarification that does not change how any valid value is interpreted.
- **MINOR** — backward-compatible semantic extension, such as adding optional metadata or a newly permitted representation that leaves existing interpretation unchanged.
- **MAJOR** — any change that can alter the interpretation, accepted value domain, required inputs, computation semantics, unit meaning, spatial semantics, or compatibility of existing data.

When unsure whether a change is semantic, the project SHOULD create a new MAJOR version.

A new Analysis Procedure version MAY still implement the same Observation Definition version when the observable semantic contract remains unchanged.

### Registry releases

Registry release version and definition version are independent.

A Registry release is an immutable bundle/snapshot of definitions. Updating the Registry bundle because a new definition was added does not change existing definition identities.

A persisted artifact that depends on Registry meaning SHOULD retain:

- Registry namespace;
- Registry release version or immutable bundle digest;
- every referenced definition ID/version;
- enough definition content or a content-addressed semantic closure to remain interpretable without a live network service.

### Semantic closure

A **semantic closure** is the minimal set of Registry definitions required to interpret a persisted object.

For an Observation Set this commonly includes:

- referenced Observation Definitions;
- referenced Signal Domain Definitions;
- referenced Analysis Procedure Definitions;
- transitively referenced definitions required by those definitions.

Portable archival representations SHOULD embed the semantic closure or provide a content-addressed bundle that can be preserved with the artifact.

A package MUST NOT rely solely on "latest Registry" resolution.

### External standards

RDA SHOULD reuse established standards instead of creating local meanings where a precise external definition already exists.

A Registry definition MAY contain external references including:

- standards organization;
- standard/document identifier;
- edition/version/date;
- clause/tag/property identifier when applicable;
- public URI when available.

External references are descriptive dependencies, not mutable web locators.

A definition MUST retain enough local semantic description to determine why the external reference is relevant, while avoiding unauthorized reproduction of copyrighted standards text.

### Provenance interoperability

Definition identity is independent of provenance serialization.

A future W3C PROV, C2PA, JSON-LD, RDF, database, or other interoperability profile MAY map Registry references into its own identifier system.

Such mappings MUST NOT silently change RDA definition semantics.

## Observation Definition contract

An Observation Definition defines what one observation means independently of the implementation that obtains it.

Required fields:

- `id`;
- `version`;
- `kind: observation`;
- `observation_kind`: `source_assertion`, `measurement`, or `derived_representation`;
- `stability`;
- `title`;
- `description`;
- `value_contract`.

Depending on the observation, it SHOULD also define:

- unit/dimension;
- valid numeric range;
- shape/cardinality;
- required Signal Domain Definition classes;
- required Signal State properties;
- spatial-scope semantics;
- unknown/unsupported/not-applicable behavior;
- uncertainty semantics;
- external standard references;
- compatible Analysis Procedure Definition references.

### Source assertions

For a Source Assertion, the definition MUST state whose assertion is being represented when that distinction matters.

For example, a recorded sensitivity field is not automatically defined as "the true ISO of the physical capture." It is a decoded source assertion with provenance to the field and extraction procedure.

### Measurements

For a Measurement, the definition MUST make explicit the mathematical quantity being represented.

A field name alone is insufficient.

A percentile definition, for example, must eventually fix:

- sample population;
- Signal State requirements;
- scalar quantity being ranked;
- masking rules;
- percentile convention/interpolation;
- output unit/range.

### Derived representations

For a Derived Representation, the definition MUST distinguish:

- visual diagnostic purpose;
- quantitative data representation;
- categorical/label map;
- another structured representation.

A visual preview MUST NOT be interpreted as a quantitative map solely because both use an image container.

## Signal Domain Definition contract

A Signal Domain Definition defines a class of signal/image states.

Required fields:

- `id`;
- `version`;
- `kind: signal_domain`;
- `stability`;
- `title`;
- `description`;
- `state_contract`.

The state contract SHOULD identify which concrete Signal State properties are required to interpret values, such as:

- source plane / channel semantics;
- CFA/demosaic state;
- active area;
- black/white normalization;
- white-balance state;
- color transform/profile;
- image-state semantics;
- transfer function;
- numeric range / quantization;
- spatial transforms.

A Signal Domain Definition is not sufficient by itself when source-specific parameters matter. Actual Measurements reference a concrete Signal State that instantiates the definition.

## Analysis Procedure Definition contract

An Analysis Procedure Definition describes method semantics independently of a concrete executable.

Required fields:

- `id`;
- `version`;
- `kind: procedure`;
- `stability`;
- `title`;
- `description`;
- required input contracts;
- produced observation contracts;
- parameter semantics.

A procedure definition SHOULD specify:

- deterministic / stochastic behavior where relevant;
- parameter defaults when defaults are semantically meaningful;
- required Signal Domain Definition or Signal State properties;
- ordering of transformations when order affects meaning;
- tolerance or equivalence expectations when multiple implementations may conform;
- external algorithm/standard references where appropriate.

A Procedure Implementation claims conformance to an Analysis Procedure Definition; it is not stored as the procedure definition itself.

## Stability

Definitions use:

- `provisional` — semantics are being tested and MAY be replaced; persisted experimental data must still retain the exact referenced version.
- `stable` — semantics are intended for durable interchange and compatibility.
- `deprecated` — retained for historical interpretation but SHOULD NOT be selected for new data unless required for compatibility.

Deprecation MUST preserve the old definition. It never reassigns the ID.

A provisional definition MAY become stable under the same ID/version only if the published semantic content does not change. Otherwise a new version is required.

## Registry cross-validation

JSON Schema is necessary but insufficient.

A conforming Registry Validator MUST additionally verify:

1. every `(id, version)` pair is unique;
2. every ID matches the namespace/kind syntax for its definition class;
3. every internal Definition Reference resolves;
4. no definition version is reused with different canonical content;
5. deprecated definitions remain resolvable;
6. supersession/replacement references do not form cycles;
7. Observation Definitions reference compatible Signal Domain / Procedure kinds;
8. Procedure produced-observation references resolve to Observation Definitions;
9. procedure input-domain references resolve to Signal Domain Definitions;
10. stable definitions do not depend on missing provisional definitions unless explicitly allowed by policy;
11. Registry release version/digest identifies one exact resolved bundle.

Stable finding codes are defined by the Conformance specification.

## Initial registry policy

The project MUST NOT populate the stable Registry with guessed RAW-development measurements simply to make the Registry look complete.

Initial measurement definitions such as luminance percentiles, clipping fraction, highlight headroom, noise level, and diagnostic preview transforms remain provisional until their exact mathematical and signal-processing contracts are fixed and validated against representative RAW sources.

Source-assertion definitions MAY be introduced earlier when their external field semantics and extraction provenance are sufficiently clear.

## Preservation rule

The Registry is optimized for future interpretation, not contemporary convenience.

If a future reader has:

- the Source Artifact;
- the Observation Set;
- its semantic closure;
- its Run provenance;

they should be able to determine what the stored values meant without depending on the current RDA source tree, current website, current AI provider, or current Adobe software.
