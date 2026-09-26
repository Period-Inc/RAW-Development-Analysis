---
pdm_version: "0.1"
id: "rda-core-domain"
name: "RAW Development Analysis Core Domain"
slug: "core-domain"
type: "specification.core"
status: "active"
created_at: "2026-09-26"
updated_at: "2026-09-26"
owners:
  - "Period-Inc"
relations: []
---

# RAW Development Analysis Core Domain

## Purpose

This document defines the stable semantic domain of RAW Development Analysis.

The core exists to describe how captured photographic source data becomes evidence, interpretation, development decisions, and tool-specific development artifacts without making any current RAW decoder, AI model, development application, or metadata format part of the permanent meaning of the system.

The design target is decades. Implementations are expected to change substantially while these semantic boundaries remain useful.

## Normative language

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are normative requirements.

## Domain statement

RAW Development Analysis is a system for producing traceable development decisions from photographic source data.

Its canonical flow is:

```text
Source Asset
  -> Observation Set
  -> Interpretation
  -> Development Decision
  -> Target Encoding
```

A Development Context may influence Interpretation and Development Decision. It MUST NOT alter or be represented as an Observation.

Evaluation may compare any resulting decision or rendering with a reference, human choice, prior decision, or acceptance criterion. Evaluation is downstream evidence, not a retroactive rewrite of the original observation.

## Core invariants

1. **The source is immutable.** The system MUST NOT require mutation of the original captured asset.
2. **Observation and interpretation are different kinds of information.** A statement about what was measured MUST NOT silently contain a judgment about what should be done.
3. **Every derived observation is attributable.** Its source identity, procedure identity, procedure version, and relevant parameters MUST be recoverable.
4. **Unknown is a first-class state.** Missing, unsupported, unavailable, and not-applicable MUST NOT be collapsed into zero, false, empty string, or guessed values.
5. **Lossy evidence is labeled as lossy.** A preview, map, thumbnail, or compressed representation MUST NOT be presented as equivalent to sensor/source data.
6. **Current tools are adapters.** Lightroom, Adobe Camera Raw, XMP, libraw, ExifTool, a particular AI provider, and a particular camera maker MUST NOT define Core semantics.
7. **Context does not contaminate observation.** A baseline preset such as `_Fundamental` belongs to Development Context, not to the Observation Set.
8. **AI is an actor, not an authority built into the domain.** Human, rules engine, statistical model, or future reasoning system MAY perform interpretation or decision roles under the same contracts.
9. **Vendor parameters are not universal intent.** Tool-specific slider values belong to Target Encoding or a target-specific decision extension.
10. **Historical results remain interpretable.** Stored records MUST carry enough version and provenance information to explain what produced them even when the producing software no longer exists.

## Aggregate model

### 1. Source Asset

A Source Asset is captured or otherwise authoritative input media.

Examples include a camera RAW file, DNG, TIFF scan, or another source representation accepted by an adapter.

A Source Asset has:

- stable source identity;
- cryptographic content identity when bytes are available;
- media/container type;
- byte length when known;
- capture metadata that can be extracted without interpretive judgment;
- one or more source planes or embedded representations when the source format exposes them.

A filename or filesystem path is a locator, not identity.

A Source Asset MAY have multiple byte-identical or semantically equivalent physical copies. Copy location is not part of its photographic meaning.

### 2. Observation Set

An Observation Set is a reproducible record of what a specific observation procedure obtained from a Source Asset.

An Observation Set is composed of three information classes:

#### 2.1 Extracted Fact

A value copied or decoded from the source without photographic evaluation.

Examples:

- camera make and model;
- recorded ISO;
- shutter duration;
- aperture;
- focal length;
- orientation;
- sensor black/white levels when present;
- as-shot white-balance coefficients when present.

An Extracted Fact MUST identify its source field or extraction procedure when ambiguity is possible.

#### 2.2 Measurement

A numeric or structured result computed from source data under an explicit Measurement Domain and Analysis Procedure.

Examples:

- luminance percentile;
- channel clipping fraction;
- histogram;
- estimated noise magnitude;
- highlight headroom expressed in EV;
- spatial frequency statistic.

A Measurement MUST define or reference:

- measurement definition identity;
- value;
- unit or dimension;
- measurement domain;
- analysis procedure;
- input representation;
- spatial scope when not global;
- uncertainty or validity information when the procedure provides it.

Names such as `brightness`, `quality`, or `color_score` are insufficient unless their measurement semantics are explicitly defined.

#### 2.3 Evidence Representation

A derived representation intended to preserve or expose information for machine or human inspection.

Examples:

- diagnostic preview;
- luminance map;
- channel-clipping mask;
- low-resolution linear representation;
- histogram image;
- segmentation-independent spatial map.

An Evidence Representation MUST declare:

- how it was produced;
- its dimensions;
- coordinate system;
- color or numeric domain;
- transfer function when applicable;
- lossy/lossless status;
- compression/encoding;
- relationship to the Source Asset.

Evidence Representation is evidence for reasoning. It is not a substitute for the Source Asset.

### 3. Measurement Domain

A Measurement Domain specifies the mathematical and imaging space in which a value has meaning.

It MUST be explicit whenever the same numeric value could have different meanings under different processing stages.

Examples include:

- sensor mosaic / CFA sample domain;
- normalized sensor-linear domain;
- demosaiced camera-linear RGB;
- scene-referred XYZ;
- display-referred sRGB;
- log-encoded diagnostic domain.

A domain definition SHOULD specify, as applicable:

- channel semantics;
- black/white normalization;
- demosaic state;
- white-balance state;
- color transform;
- transfer function;
- bit depth / numeric range;
- clipping behavior.

### 4. Analysis Procedure

An Analysis Procedure is the reproducible method used to produce an Extracted Fact, Measurement, or Evidence Representation.

Procedure identity is semantic; executable filename is not.

A procedure record MUST identify:

- procedure name or stable ID;
- implementation/version;
- parameters that materially affect output;
- decoder or dependent procedure versions when they materially affect output.

Two values with the same field name but produced by materially different procedures are not assumed equivalent.

### 5. Development Context

Development Context is information intentionally supplied to guide interpretation or decision.

Examples:

- baseline development profile such as `_Fundamental`;
- desired rendering style;
- destination medium;
- output color space;
- photographer-specific preferences;
- constraints such as "do not alter crop";
- target application capabilities.

Development Context is not evidence about the source.

### 6. Interpretation

Interpretation assigns meaning to observations under a context.

Examples:

- "the subject is substantially darker than the background";
- "highlight preservation is likely to be important";
- "the image appears warmer than the requested neutral rendering";
- scene or subject classification.

Interpretation MAY be produced by AI, deterministic rules, a human, or another actor.

Interpretation SHOULD record:

- actor/procedure identity;
- input Observation Set identity;
- Development Context identity when used;
- output assertions;
- confidence or uncertainty where meaningful;
- rationale/evidence references when available.

Interpretive labels MUST NOT be inserted into the Observation Set as if they were measurements.

### 7. Development Intent

Development Intent expresses a desired photographic or rendering change independently of a specific application's storage format when such independence is semantically possible.

Examples:

- global exposure compensation in EV;
- neutralize a measured chromatic cast under a stated reference;
- retain highlight separation;
- raise subject-relative luminance;
- preserve local contrast.

Some development operations cannot be meaningfully normalized across vendors. Such operations MUST remain explicitly target-specific rather than being given a false universal meaning.

### 8. Development Decision

A Development Decision is an explicit choice of development action based on an Observation Set, optional Interpretation, and Development Context.

A decision MAY contain:

- vendor-neutral intents;
- bounded numeric operations with defined semantics;
- target-specific operations;
- confidence;
- constraints;
- references to supporting observations/interpretations.

A baseline-plus-delta decision is valid, but the baseline identity MUST be explicit.

### 9. Target Model

A Target Model describes the capabilities and parameter semantics of a concrete development system.

Examples:

- a particular Adobe Camera Raw process version;
- another RAW processor;
- a future renderer;
- an internal reference renderer.

The Target Model is an adapter-side concept. It MUST NOT redefine Observation semantics.

### 10. Target Encoding

A Target Encoding is the serialized artifact that applies or communicates a Development Decision to a Target Model.

Examples:

- Adobe XMP sidecar;
- application-specific JSON;
- command-line arguments;
- future metadata or API request.

Target Encoding is derived and replaceable. It is never the canonical meaning of the Development Decision.

### 11. Evaluation Record

An Evaluation Record compares an observation, interpretation, decision, encoding, or rendered result against a reference or criterion.

Examples:

- difference between AI proposal and a photographer's final settings;
- acceptance of a generated XMP;
- perceptual comparison of two renderings;
- regression result across analyzer versions.

A human final adjustment MAY be used as a reference. It MUST NOT be treated as objective truth unless the evaluation contract explicitly defines it as the authority for that experiment.

## Provenance chain

Every derived item SHOULD be traceable through a chain of identities:

```text
Source identity
  -> decoder/procedure identity
  -> observation identity
  -> interpretation identity
  -> decision identity
  -> target model identity
  -> target encoding identity
```

A system MAY materialize only part of this chain, but it MUST NOT erase provenance required to distinguish materially different results.

## Spatial semantics

Spatial data MUST declare its coordinate system.

Core recognizes at least these distinct concepts:

- source sensor coordinates;
- decoded image coordinates;
- oriented image coordinates;
- normalized image coordinates;
- cropped/output coordinates.

A map or region MUST NOT rely on implicit orientation or an undocumented crop.

Normalized coordinates SHOULD be used for portable references, with the transform back to the referenced pixel domain recorded or derivable.

## Color and tone semantics

Color and tone measurements are meaningless without their processing domain.

Therefore:

- "RGB" without a defined RGB space is insufficient;
- "luminance" without a defined transform is insufficient;
- normalized values MUST define normalization endpoints;
- transfer functions MUST be stated;
- white-balance state MUST be stated when it affects the value;
- clipping measurements MUST define the clipping threshold and domain.

## Missing and uncertain information

Core distinguishes:

- `known` — a value is available under its declared procedure;
- `unknown` — the value is conceptually applicable but not known;
- `unsupported` — the current procedure cannot obtain it;
- `unavailable` — required source data is not available;
- `not_applicable` — the concept does not apply.

Implementations MAY use a different wire representation, but these semantic states MUST remain distinguishable when relevant.

Measurement uncertainty and Interpretation confidence are different concepts and MUST NOT be conflated.

## Package boundary

The Core does not define a directory, ZIP layout, or transport format.

A **Photo Observation Package (POP)** MAY serialize an Observation Set and its Evidence Representations for transport, caching, archival inspection, or AI input.

POP is a serialization profile, not the domain itself.

Changing POP layout MUST NOT require changing the meaning of Source Asset, Observation, Interpretation, or Development Decision.

## Current-project mapping

The current concept maps as follows:

| Current term | Core concept |
| --- | --- |
| RAW file | Source Asset |
| EXIF / RAW metadata extraction | Extracted Facts |
| histogram / clipping / noise calculation | Measurements |
| neutral / highlight / shadow small previews | Evidence Representations |
| intermediate package | serialization of an Observation Set (candidate: POP) |
| `_Fundamental.xmp` | Development Context / baseline profile |
| AI analysis | Interpretation and/or Development Decision actor |
| AI delta from `_Fundamental` | baseline-relative Development Decision |
| generated XMP | Target Encoding |
| Lightroom / Camera Raw | Target Model / adapter |
| manually finalized settings | human Development Decision; optionally an Evaluation reference |

This mapping is intentionally one-way: current implementation concepts are placed inside the Core domain, but Core is not defined by them.

## Domain boundary tests

A proposed Core concept SHOULD pass these tests:

1. **Lightroom disappearance test** — would the concept still make sense if Adobe products no longer existed?
2. **AI replacement test** — would the concept still make sense if current LLM/VLM systems were replaced by a different reasoning technology?
3. **RAW format replacement test** — would the concept still make sense with a future capture format?
4. **Decoder replacement test** — can a new decoder coexist without rewriting historical meaning?
5. **Fifty-year audit test** — can a future reader determine what was observed, how it was observed, what was inferred, and what was decided?
6. **No-hidden-judgment test** — can a measurement be explained without using words such as good, appropriate, too dark, natural, or beautiful?
7. **No-false-universality test** — is a vendor-specific parameter kept vendor-specific when no stable cross-vendor semantics exist?

If a concept fails these tests, it SHOULD live in an adapter, profile, experiment, or extension rather than Core.
