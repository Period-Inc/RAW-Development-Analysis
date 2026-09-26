---
pdm_version: "0.1"
id: "rda-observation-model"
name: "Observation Set and Portable Observation Package"
slug: "observation-model"
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
---

# Observation Set and Portable Observation Package

## Purpose

This document defines the durable information model for mechanically observing a photographic source and the requirements for a portable package that carries those observations to downstream actors such as AI systems.

The semantic object is the **Observation Set**.

The current portable serialization profile is provisionally called **Photo Observation Package (POP)**.

POP is not the domain authority. A future database, object store, stream protocol, or different package format may represent the same Observation Set.

## Scope

This specification defines Observation Set identity, observation profiles, extracted facts, measurements, derived representations, provenance requirements, semantic-definition references, package-manifest responsibilities, binary evidence handling, AI-consumption boundaries, and stabilization rules.

It does not yet freeze the exact POP JSON Schema, directory layout, preview transform, or base observation profile.

## Requirements

A portable observation representation MUST preserve the semantic class, provenance, measurement domain, validity, and source relationship required to interpret every included observation.

Consumers MUST resolve semantics from explicit definitions and manifest references rather than filenames or undocumented field conventions.

Development preferences and target-specific adjustment policy MUST remain outside the Observation namespace.

## Observation Set identity

An Observation Run represents one execution over a Source Artifact under one declared analysis configuration.

An Observation Set is the immutable result produced by that run.

Run identity MUST distinguish at least:

- source content identity;
- observation profile identity/version;
- analysis-procedure definitions/versions;
- analyzer implementation/build identity;
- materially relevant decoder/dependency identities and versions;
- materially relevant runtime parameters.

Observation Set identity MAY be content-addressed independently of Run identity.

Two runs MAY produce byte-identical Observation Sets while remaining distinct execution events. Conversely, a materially changed implementation or dependency MUST NOT be hidden merely because output happens to compare equal in one case.

## Observation profile

An Observation Profile defines which observations and derived representations are requested together.

Examples:

- `raw-development/base-v1`;
- a minimal metadata-only profile;
- a future high-fidelity scientific profile.

The profile is a request/contract, not proof of successful extraction. Individual outputs retain explicit validity states.

Adding an optional observation does not change the meaning of existing observation definitions.

## Information classes

A package MUST keep the following classes distinguishable:

### Source reference

Identifies the Source Artifact without requiring the source bytes to be embedded.

Required semantic information:

- one or more source digests when available;
- digest algorithms;
- media/container type when known;
- source byte size when known;
- optional external locator hints that are explicitly non-authoritative.

A POP SHOULD NOT embed the original RAW by default.

### Source assertions

Values declared or encoded by source metadata or source structures and decoded without adding a photographic-development judgment.

A Source Assertion is not automatically an independently verified physical fact. For example, camera-reported ISO, focal length, or white-balance coefficients are assertions attributable to the source and extraction procedure.

Every assertion SHOULD identify the extraction source/path or procedure if different decoders may disagree. Conflicting assertions MAY coexist when their provenance differs.

### Measurements

Measurements are typed records, not anonymous JSON numbers.

A measurement record conceptually contains:

- definition ID;
- value;
- unit/dimension;
- validity;
- signal-domain reference;
- procedure-definition reference;
- observation-run reference;
- input representation reference;
- spatial-scope reference;
- optional measurement uncertainty;
- optional auxiliary parameters required for interpretation.

Wire formats MAY compact repeated references through tables or IDs.

### Derived representations

Binary or structured derived evidence such as previews, maps, masks, distributions, or tensors.

Each derived representation conceptually contains:

- stable role/definition ID;
- media type;
- byte digest;
- dimensions/shape;
- numeric/color domain;
- encoding/compression;
- lossiness declaration;
- procedure reference;
- spatial reference;
- transform relationship to source/decoded coordinates.

A consumer MUST be able to distinguish a display preview from a measurement map even if both are encoded as an image file.

### Provenance

The package MUST be able to resolve every derived item through both semantic method and execution provenance.

At minimum, the package MUST distinguish:

- observation definition — what the value means;
- analysis procedure — what method defines the computation;
- procedure implementation — which executable realization was used;
- observation run — which execution produced this result.

Provenance SHOULD avoid repeating full software metadata on every measurement. A manifest MAY define definitions, procedures, implementations, and run records once and reference them by local IDs.

An interoperability profile MAY map these concepts to established provenance models. The POP wire format MUST NOT require consumers to treat local identifiers as globally meaningful when they are only package-scoped.

## Definitions over field names

Durable meaning MUST be attached to a definition identity, not merely to a JSON key.

For example, the durable concept is not the string:

`luminance_p99`

but a versioned definition stating:

- which input domain is used;
- how luminance is computed;
- what sample population is included;
- how black/white normalization occurs;
- how percentile interpolation occurs;
- how masked/invalid pixels are treated.

A convenient field name MAY exist in a serialization, but consumers MUST be able to resolve its semantic definition.

## Candidate base observation profile

The initial RAW-development profile SHOULD stay intentionally small until experiments show additional evidence is required.

### Source/exposure facts

Candidate facts:

- camera make/model;
- lens identity when available;
- ISO;
- shutter duration;
- aperture;
- focal length;
- image dimensions;
- source orientation;
- recorded exposure compensation;
- as-shot white-balance coefficients;
- sensor black/white levels when reliably available.

### Tone measurements

Candidate measurements:

- histogram or compact histogram summary;
- p01, p05, p25, p50, p75, p95, p99 under an explicitly defined linear domain;
- per-channel near-clipping/clipping fractions;
- shadow-floor estimate;
- highlight-headroom estimate in EV when a valid procedure is defined.

### Color measurements

Candidate measurements:

- channel statistics in a defined linear domain;
- chromaticity or neutral-candidate statistics only after the exact procedure is specified;
- saturation statistics only under a defined color space.

The project MUST NOT introduce an ambiguous universal `temperature` or `tint` measurement until its estimation procedure and reference model are defined.

### Detail/noise measurements

Candidate measurements:

- noise estimate under an explicit estimator and spatial-selection method;
- high-frequency/detail statistic under an explicit procedure.

These are not named `image_quality` because quality is interpretive.

### Spatial evidence

Candidate evidence:

- low-resolution luminance map;
- per-channel clipping or headroom map;
- optional linear-RGB diagnostic map.

Maps SHOULD be sufficiently low resolution to reduce cost while preserving the spatial relationships needed by downstream reasoning.

### Diagnostic previews

The base profile SHOULD provide a small set of standardized diagnostic views rather than a single attractive preview.

Initial candidates:

- neutral diagnostic view;
- highlight-inspection view;
- shadow-inspection view.

Their exact transforms are not yet Core. Before stabilization, each transform MUST be fully specified and validated across representative RAW formats.

Diagnostic previews MUST NOT inherit an undocumented camera-maker look.

An embedded camera JPEG MAY be included as a separate representation role because it can provide useful contextual information, but it MUST be identified as an in-camera rendering rather than RAW-neutral evidence.

## Package manifest

A portable package SHOULD contain a manifest that resolves semantic objects to package assets.

The following example is illustrative, not yet a stable schema:

```json
{
  "format": "photo-observation-package",
  "format_version": "0.1.0",
  "observation_profile": "raw-development/base-v1",
  "source": {
    "digests": [
      {"algorithm": "sha256", "value": "..."}
    ],
    "media_type": "image/x-sony-arw"
  },
  "run": {
    "id": "run-...",
    "implementation": "impl-rda-analyzer-...",
    "procedures": ["proc-..."]
  },
  "definitions": {},
  "procedures": {},
  "implementations": {},
  "facts": [],
  "measurements": [],
  "representations": []
}
```

The final schema MAY use a different physical shape if it preserves the semantics defined here.

## Package layout

Directory names are not Core.

A convenient v0 implementation MAY use:

```text
<source>.pop/
  manifest.json
  representations/
    preview-neutral.webp
    preview-highlight.webp
    preview-shadow.webp
    luminance-map.*
    clipping-map.*
```

This layout is replaceable.

Consumers MUST use manifest references rather than infer semantics from filenames.

## Binary encodings

A map does not become semantically an "image" merely because PNG, WebP, TIFF, EXR, or another image container is used.

For quantitative maps, the manifest MUST define how encoded sample values map back to the measurement domain.

Lossy encoding MUST NOT be used for a quantitative map unless the definition explicitly allows and bounds the resulting loss.

Diagnostic visual previews MAY use lossy encoding.

## AI consumption

An AI input builder MAY transform an Observation Set into the most economical model input available at the time.

Examples:

- structured JSON;
- selected scalar measurements;
- compact tables;
- selected diagnostic images;
- textual explanations of definition semantics;
- future multimodal tensors.

This transformation is an adapter concern.

The Observation Set MUST NOT be redesigned around a current model token format or image-size limit.

## Context exclusion

A POP that serializes an Observation Set MUST NOT place development preferences inside the observation namespace.

The following belong outside Observation:

- `_Fundamental` preset values;
- desired look;
- photographer preferences;
- target application;
- requested output medium;
- AI prompt policy;
- final human corrections.

A transport envelope MAY carry Observation and Development Context together for one request, but they remain separate typed sections.

## Security and privacy

A source may contain location, device serials, creator identity, timestamps, or other sensitive metadata.

Observation profiles SHOULD define whether such fields are:

- included;
- excluded;
- redacted;
- hashed/pseudonymized;
- passed only under an explicit privacy policy.

Privacy filtering is a packaging/export policy. It MUST NOT silently rewrite the underlying semantic definition of an extracted fact.

## Verification requirements

Before a base observation profile is declared stable, the project SHOULD verify:

1. repeated runs with the same pinned implementation are reproducible within defined tolerances;
2. multiple representative camera RAW formats are handled;
3. orientation and crop transformations are correct;
4. quantitative map values can be decoded back to their declared domain;
5. diagnostic views expose highlight/shadow information without undocumented auto-adjustment;
6. unsupported source metadata is represented as unsupported/unavailable rather than guessed;
7. old package fixtures remain readable after compatible schema evolution.

## Stabilization rule

A candidate measurement or representation role SHOULD enter the stable base profile only when at least one downstream decision has demonstrated that the information materially improves a useful task or provides necessary diagnostic traceability.

The default response to an uncertain future requirement is an extension, not expansion of Core.
