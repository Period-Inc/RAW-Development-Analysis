---
pdm_version: "0.1"
id: "rda-proxy-edit-transfer-implementation-plan"
name: "Proxy Edit and RAW Parameter Transfer Implementation Plan"
slug: "proxy-edit-transfer-implementation"
type: "planning.plan"
status: "draft"
created_at: "2026-10-05"
updated_at: "2026-10-05"
owners:
  - "Period-Inc"
relations:
  - type: "implements"
    target: "rda-proxy-edit-transfer"
---

# Proxy Edit and RAW Parameter Transfer Implementation Plan

## Goal

Reach an implementation-ready MVP whose smallest valuable path is:

```text
JPEG proxy edit
  -> manifest
  -> later RAW match
  -> verified parameter translation
  -> Adobe sidecar
```

Automatic analysis is additive, not required.

## Module layout

Suggested package boundary:

```text
rda_toolchain/
  proxy/
    model.py
    manifest.py
    coordinates.py
  resolver/
    candidates.py
    verify.py
  transfer/
    planner.py
    report.py
  targets/
    adobe/
      baseline.py
      xmp.py
      acr.py
      capability.py
  snippets/
    rotation.py
    sharpness.py
    white_balance.py
    spots.py
web/
  api/
  ui/
```

The final directory names MAY change; responsibility boundaries SHOULD remain.

## Phase 1 — parameter-transfer script

This is the first deliverable and already has standalone value.

Implement:

- load proxy manifest;
- load/source-register RAW;
- resolve explicit or verified proxy↔RAW pair;
- validate coordinate/orientation assumptions;
- classify every decision by transfer class;
- translate verified scalar/geometry fields;
- emit target sidecar to a staging path;
- emit machine-readable transfer report;
- never overwrite an existing target artifact by default.

Initial CLI:

```text
rda transfer-proxy-edit MANIFEST RAW --target adobe --out OUTDIR
```

Required output:

- transfer-report.json;
- generated target sidecar(s);
- warnings;
- unapplied fields.

## Phase 2 — manifest authoring API

Implement CRUD for:

- rating;
- reject;
- rotation;
- crop;
- global adjustment;
- annotations;
- spot edits;
- masks;
- mask-local adjustments.

API operations MUST write portable decisions, never direct Adobe fields.

## Phase 3 — minimal Web UI

Implement:

### Collection

- proxy thumbnail/grid;
- keyboard next/previous;
- rating;
- reject;
- edited/unreviewed state.

### Editor

- image viewport;
- rotation;
- crop;
- exposure;
- WB;
- spot points/regions;
- mask overlay;
- adjustment panel;
- undo/redo through edit events or manifest revisions.

No RAW is required.

## Phase 4 — RAW resolver

Resolver stages:

1. explicit lineage / embedded ID;
2. metadata narrowing;
3. basename/time candidate generation;
4. visual fingerprint retrieval if required;
5. verification;
6. ambiguous result if not uniquely established.

The resolver MUST not invent identity from basename alone.

## Phase 5 — algorithmic snippets

Implement only snippets with measurable value.

Suggested order:

1. rotation estimate;
2. global/subject sharpness;
3. rating rules over observations;
4. WB proposal for event/live scenes;
5. persistent sensor-spot candidates;
6. foreign-object candidates.

Each snippet is replaceable and independently testable.

## Phase 6 — mask/spot Adobe adapter

Do not guess undocumented storage.

Build a fixture matrix:

- one circular heal;
- one clone;
- one removal region;
- one brush mask;
- one linear gradient;
- one radial gradient;
- one add/subtract composite;
- one mask-local exposure change.

For each fixture:

- save before sidecars;
- edit once in target Lightroom;
- save after sidecars;
- collect XMP + ACR + relevant LRCAT state;
- diff;
- reload;
- verify.

Only promote write support for characterized target versions.

## Data model

### ProxyArtifact

- id
- digest
- width
- height
- orientation
- lineage_status
- locator hints

### EditSession

- id
- proxy_ref
- baseline_context_ref
- created_at
- current_revision

### Decision

- id
- session_ref
- kind
- portable payload
- source: human/rule/model/import
- status: proposed/accepted/rejected/superseded

### Mask

- id
- session_ref
- coordinate_space
- composition tree
- optional raster_asset_ref
- optional semantic_intent

### SpotEdit

- id
- session_ref
- mode
- target geometry
- source geometry
- parameters
- status

### SourceResolution

- proxy_ref
- raw_ref
- status
- evidence
- confidence
- alternatives

### TransferRun

- manifest revision
- raw_ref
- target adapter/version
- field results
- target artifact refs

## Manifest revision strategy

Use immutable revisions.

Every accepted edit produces a new logical manifest revision or append-only edit event.

A transfer run references the exact revision transferred.

## Transfer planner

The planner receives:

- manifest revision;
- resolved RAW;
- target adapter capability matrix.

It produces a plan per field:

```text
apply
skip
warn
requires-baseline
advisory-only
unsupported
ambiguous
```

Target writers execute only `apply`.

## Adobe adapter capability matrix

Capability MUST be data-driven by target version.

Example conceptual fields:

- rating: supported;
- rotation: supported;
- crop: supported;
- exposure: supported with baseline;
- WB: supported with baseline;
- brush mask: experimental by version;
- spot heal: experimental by version;
- generative remove: advisory/unsupported until characterized.

## Testing

### Unit

- coordinate transforms;
- crop normalization;
- rotation sign conventions;
- mask composition model;
- manifest validation;
- transfer class planning;
- resolver ambiguity.

### Golden fixtures

- proxy manifest -> expected XMP;
- proxy geometry -> expected full-resolution geometry;
- target adapter before/after round-trip fixtures.

### Integration

- open generated sidecar in target application;
- verify values;
- save metadata back out;
- compare normalized target state.

## Acceptance criteria for first implementation

The first implementation is usable when:

1. a 720px proxy can be edited without RAW access;
2. rating, crop, rotation, exposure delta, and WB delta persist in a manifest;
3. a later RAW can be resolved or explicitly paired;
4. the transfer planner reports what will and will not be applied;
5. verified basic Adobe fields can be written without touching RAW bytes;
6. every transfer is reproducible from manifest revision + adapter version;
7. unsupported mask/spot edits remain preserved rather than discarded.

## Immediate coding order

1. manifest schema + Python model;
2. coordinate utilities;
3. transfer planner;
4. Adobe scalar XMP adapter;
5. CLI `transfer-proxy-edit`;
6. fixture tests;
7. minimal API;
8. Web UI;
9. resolver;
10. algorithm snippets;
11. mask/spot target characterization;
12. ACR adapter.
