---
pdm_version: "0.1"
id: "rda-proxy-edit-transfer"
name: "Proxy Edit and RAW Parameter Transfer"
slug: "proxy-edit-transfer"
type: "specification.application"
status: "draft"
created_at: "2026-10-05"
updated_at: "2026-10-05"
owners:
  - "Period-Inc"
relations:
  - type: "depends_on"
    target: "rda-core-domain"
---

# Proxy Edit and RAW Parameter Transfer

## Purpose

This specification defines a proxy-first photographic editing workflow.

The minimum useful product is:

> Edit a lightweight JPEG now; preserve the edit decisions as parameters; resolve the matching RAW later; apply the transferable decisions to RAW development.

The RAW does not need to be locally available during the proxy edit session.

Automatic analysis is optional. The transfer workflow is independently useful.

## Product boundary

The system is not a replacement for Lightroom or Photoshop.

It is a pre-development and offline-editing layer that allows lightweight proxy work before the original RAW is available.

The system owns the durable edit-decision model.

Adobe XMP, Lightroom catalog state, and Adobe ACR sidecars are target encodings or target-side storage, not the canonical model.

## Primary workflow

```text
Proxy JPEG
   ↓
Proxy Edit Session
   ↓
Edit Manifest
   ↓
Human-confirmed Edit Decision
   ↓
[RAW may become available later]
   ↓
JPEG ↔ RAW Resolution
   ↓
Transferability Validation
   ↓
Target Translation
   ↓
Adobe sidecars / Lightroom import state
```

JPEG-to-RAW resolution occurs late by design.

## MVP capabilities

The first implementation SHALL support:

- proxy JPEG registration;
- rating / reject;
- rotation / straighten;
- crop;
- normalized annotations;
- exposure delta;
- white-balance delta;
- structured manifest persistence;
- late JPEG-to-RAW resolution;
- target transfer report;
- Adobe basic-settings sidecar generation for fields whose mapping has been verified.

The system SHOULD be designed from the beginning to support masks and spotting/removal primitives without changing the manifest identity model.

## Proxy

A Proxy is a lossy Derived Representation used for low-cost editing.

Typical dimensions are approximately 720 × 480, preserving source aspect ratio unless explicitly cropped.

A Proxy MUST record:

- digest;
- dimensions;
- orientation;
- source locator hint when known;
- lineage status;
- generation procedure when known.

### Known-lineage proxy

The source RAW and proxy-generation baseline are known.

This permits stronger photometric transfer.

### Unknown-lineage proxy

The JPEG is believed to represent a RAW, but the exact rendering pipeline is not known.

Geometry, rating, annotations, and many mask shapes remain useful.

Photometric parameter transfer MAY be restricted to advisory mode unless a compatible baseline is established.

## Edit Manifest

The Edit Manifest is the canonical record of proxy editing.

The rendered proxy pixels are not the authority.

A manifest MUST preserve:

- proxy identity;
- coordinate space;
- baseline context when known;
- proposals separately from accepted decisions;
- human-confirmed decisions;
- annotations;
- masks;
- spot/removal edits;
- transfer status;
- provenance.

## Decision provenance

Every editable field SHOULD distinguish:

```text
observed / proposed / human-confirmed / target-translated / applied
```

A machine proposal MUST NOT silently replace a human-confirmed value.

## Coordinate spaces

All spatial edit data MUST be expressible in normalized oriented-image coordinates.

### Normalized oriented-image space

- origin: top-left;
- x: 0.0 .. 1.0;
- y: 0.0 .. 1.0;
- coordinate orientation: explicitly recorded;
- source dimensions: recorded separately.

UI pixel coordinates are disposable projections.

Normalized coordinates are the durable transfer representation.

## Transfer classes

### Class A — directly transferable

Independent of JPEG tone rendering:

- rating;
- reject / pick;
- workflow label;
- crop geometry;
- rotation / straighten;
- normalized point / region annotations;
- vector mask geometry;
- raster mask geometry when coordinate mapping is known.

### Class B — baseline-relative transferable

Requires a known or compatible target baseline/process model:

- exposure;
- temperature / tint;
- highlights / shadows / whites / blacks;
- contrast;
- vibrance / saturation;
- local adjustment values attached to masks.

### Class C — transferable intent requiring target execution

The edit intent and geometry are portable, but the exact resulting pixels depend on a target algorithm:

- heal;
- clone;
- content-aware remove;
- generative remove;
- AI subject/sky/person masks when only semantic intent is preserved.

Class C records MUST preserve enough geometry and intent for a target adapter to execute or request confirmation.

## Rating

Rating is a workflow Decision.

It MAY be entered by a human or proposed by policy/algorithm.

Final rating MUST preserve its source.

Suggested initial fields:

- rating: 0..5;
- reject: boolean;
- pick: boolean;
- reasons: optional machine/human rationale identifiers.

## Geometry edits

Geometry SHALL be represented independently of Adobe fields.

### Rotation

```yaml
rotation:
  delta_deg: -1.8
  source: human
```

### Crop

```yaml
crop:
  coordinate_space: oriented-normalized
  left: 0.04
  top: 0.07
  right: 0.96
  bottom: 0.93
```

Crop transfer MUST validate source orientation and aspect assumptions.

## Global development edits

Initial portable decision fields:

- exposure_delta_ev;
- temperature_delta;
- tint_delta;
- highlights_delta;
- shadows_delta;
- whites_delta;
- blacks_delta;
- contrast_delta;
- vibrance_delta;
- saturation_delta.

These are semantic decisions relative to a declared baseline.

They are not Adobe fields.

## Spot / removal edits

Spotting is a first-class edit primitive.

A Spot Edit SHALL describe a target region and MAY describe a source/sample region.

Initial modes:

- candidate;
- heal;
- clone;
- remove;
- generative_remove.

Example:

```yaml
spot_edits:
  - id: spot-001
    mode: heal
    target:
      type: circle
      center: [0.731, 0.218]
      radius: 0.012
    source:
      mode: explicit
      center: [0.694, 0.221]
    feather: 0.5
    opacity: 1.0
    source_of_decision: human
```

A candidate MAY exist without a chosen correction mode.

Sensor-dust detection or foreign-object detection SHOULD emit candidates rather than silently create destructive edits.

## Masks

Masks are first-class spatial edit objects.

A Mask SHALL have:

- stable mask ID;
- coordinate space;
- one or more components;
- composition operation;
- optional raster snapshot;
- optional semantic intent;
- local adjustments applied through the mask.

### Mask component types

Initial portable types:

- brush stroke;
- linear gradient;
- radial gradient;
- ellipse;
- polygon;
- raster alpha mask;
- semantic selector snapshot.

### Brush stroke

A brush stroke SHOULD preserve:

- normalized path points;
- radius or pressure-varying radius;
- feather;
- flow;
- density/opacity where relevant.

### Linear gradient

Preserve normalized geometry rather than screen pixels.

### Radial gradient

Preserve center, radii, rotation, feather, and inversion.

### Raster alpha mask

A raster mask asset MUST record:

- asset digest;
- dimensions;
- bit depth;
- transfer/range semantics;
- coordinate mapping to normalized oriented-image space;
- lossy/lossless status.

A low-resolution proxy mask MAY be upscaled for target execution, but that fact MUST be recorded as a lossy spatial transfer.

### Semantic masks

For AI-derived masks such as subject, sky, person, or object:

- preserve semantic intent when useful;
- preserve the resolved raster mask when available.

The semantic selector alone is not sufficient for reproducible transfer because another model/version may select different pixels.

### Mask composition

Masks MUST support explicit operations:

- add;
- subtract;
- intersect.

Target adapters MAY reject compositions they cannot encode.

## Local adjustments

A Mask MAY own local adjustment decisions.

Example:

```yaml
mask:
  id: mask-face-001
  adjustments:
    exposure_delta_ev: 0.35
    shadows_delta: 12
    temperature_delta: 150
```

Local adjustment semantics follow the same baseline-relative rule as global adjustments.

## Mechanical snippets

Algorithmic processing SHOULD be implemented as independent snippets.

A snippet emits Observation and/or Proposal.

It MUST NOT silently become the final Decision.

Initial candidates:

- detect_rotation;
- detect_faces;
- detect_eyes;
- measure_subject_sharpness;
- measure_global_sharpness;
- estimate_white_balance;
- detect_sensor_spot_candidates;
- detect_foreign_object_candidates.

A snippet SHOULD declare:

- required proxy representation;
- output coordinate space;
- procedure version;
- confidence;
- optional overlay geometry.

## Web UI

The Web UI is an edit-decision console.

### Collection view

Minimum functions:

- next/previous;
- rating 1..5;
- reject/pick;
- filter;
- batch acceptance of proposals.

### Single image view

Minimum functions:

- proxy display;
- zoom/pan;
- crop;
- straighten;
- global exposure/WB;
- overlay toggles;
- spot candidate display/edit;
- mask create/edit;
- local adjustments attached to a mask;
- indication of transfer class and transfer warnings.

The UI SHALL edit manifest data, not destructively rewrite the proxy.

## JPEG-to-RAW resolution

Resolution occurs after proxy editing.

Candidate evidence MAY include:

- explicit generated lineage;
- embedded identity metadata;
- basename;
- capture timestamp;
- camera model / serial;
- dimensions / orientation;
- source metadata;
- visual fingerprint candidate retrieval;
- stronger visual verification.

Filename equality alone is insufficient.

Resolver output MUST preserve:

- selected RAW;
- relation type;
- confidence/status;
- evidence;
- alternatives when ambiguous.

## Transfer

Transfer is two separate operations.

### Semantic transfer

Project the accepted proxy Decision onto the resolved RAW Source Artifact.

### Target translation

Translate the portable Decision into the destination application's parameter/storage model.

These operations MUST remain distinguishable.

## Adobe target adapter

The initial target is current Lightroom Classic / Camera Raw.

The adapter SHALL be versioned.

It SHALL record:

- Lightroom/Camera Raw target version where known;
- Adobe Process Version;
- baseline profile/context;
- portable decision field;
- Adobe field/storage mechanism;
- translated value;
- warnings;
- transfer result.

Basic scalar development values MAY be emitted through verified XMP mappings.

For current Lightroom Classic generations, masks, large edits, removal edits, and other large edit data MAY use an additional Adobe ACR sidecar. The adapter MUST treat XMP and ACR as implementation-specific target artifacts and MUST NOT make their undocumented representation part of the RDA semantic model.

Mask/spot Adobe encoding SHALL be introduced only after round-trip fixture characterization proves that the produced artifacts are accepted by the target version.

## Target characterization protocol

For any target field not publicly and stably specified:

1. create a controlled RAW fixture;
2. save baseline target metadata/sidecars;
3. make exactly one edit in Lightroom;
4. save metadata/sidecars again;
5. diff catalog/XMP/ACR artifacts;
6. reload into Lightroom/Camera Raw;
7. verify the edit round-trips;
8. record target version and observed encoding;
9. add a conformance fixture before enabling writes.

The adapter MUST prefer verified target behavior over guessed undocumented fields.

## Transfer safety

Before target write, each field is classified:

- transferable;
- transferable_with_baseline;
- transferable_as_geometry_or_intent;
- unsupported;
- ambiguous.

Default behavior MUST refuse silent application of ambiguous values.

## Persistence

SQLite is sufficient for MVP.

Suggested logical records:

- proxy_artifact;
- edit_session;
- edit_decision;
- proposal;
- annotation;
- mask;
- mask_component;
- local_adjustment;
- spot_edit;
- raw_candidate;
- source_resolution;
- transfer_run;
- target_artifact.

Binary mask assets live outside the relational store and are referenced by digest.

## Implementation boundary

The first implementation SHOULD NOT require:

- RAW decoding during proxy editing;
- Lightroom catalog access during proxy editing;
- AI;
- cloud services;
- a RAW being present.

Those are later inputs/adapters.

This preserves the principal feature: lightweight JPEG editing can happen independently and be transferred later.
