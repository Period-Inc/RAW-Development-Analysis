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

## Scope

This specification defines the durable domain vocabulary, semantic boundaries, and invariants shared by analyzers, AI or human reasoning actors, development-decision components, target adapters, and evaluation tooling.

It does not define a concrete package layout, RAW decoding library, AI prompt, Lightroom workflow, or application UI.

## Requirements

Implementations claiming Core compatibility MUST preserve the stage boundaries and invariants in this document even when their internal storage or execution pipeline differs.

Core concepts MUST be represented with enough provenance and type information that source assertion, measurement, execution, interpretation, decision, and target-specific encoding cannot be silently conflated.

Core provenance semantics SHOULD remain mappable to established provenance models rather than inventing incompatible concepts where an established mapping exists. Such standards are interoperability targets, not Core dependencies.

## Normative language

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are normative requirements.

## Domain statement

RAW Development Analysis is a system for producing traceable development decisions from photographic source data.

A common dependency path is:

```text
Source Artifact
  -> Observation Set
  -> Interpretation
  -> Development Decision
  -> Target Encoding
```

This diagram is not a required linear pipeline. The authoritative structure is a provenance/dependency graph. An Interpretation MAY request additional Observation Runs; a Development Decision MAY be revised after target execution or evaluation; multiple Interpretations and Decisions MAY share the same Observation Set.

A Development Context may influence Interpretation and Development Decision. It MUST NOT alter or be represented as an Observation.

Evaluation may compare any resulting decision or rendered result with a reference, human choice, prior decision, or acceptance criterion. Evaluation is downstream evidence, not a retroactive rewrite of the original observation.

## Core invariants

1. **Source artifacts are immutable content objects.** Any byte-changing conversion or rewrite creates a distinct Source Artifact linked by provenance; a filesystem copy alone does not change photographic meaning.
2. **Observation and interpretation are different kinds of information.** A statement about what was measured MUST NOT silently contain a judgment about what should be done.
3. **Every derived observation is attributable.** Its source identity, observation definition, procedure definition, execution identity, implementation/build identity, and materially relevant parameters MUST be recoverable.
4. **Unknown is a first-class state.** Missing, unsupported, unavailable, and not-applicable MUST NOT be collapsed into zero, false, empty string, or guessed values.
5. **Lossy evidence is labeled as lossy.** A preview, map, thumbnail, or compressed representation MUST NOT be presented as equivalent to sensor/source data.
6. **Current tools are adapters.** Lightroom, Adobe Camera Raw, XMP, libraw, ExifTool, a particular AI provider, and a particular camera maker MUST NOT define Core semantics.
7. **Context does not contaminate observation.** A baseline preset such as `_Fundamental` belongs to Development Context, not to the Observation Set.
8. **AI is an actor, not an authority built into the domain.** Human, rules engine, statistical model, or future reasoning system MAY perform interpretation or decision roles under the same contracts.
9. **Vendor parameters are not universal intent.** Tool-specific slider values belong to Target Encoding or a target-specific decision extension.
10. **Historical results remain interpretable.** Stored records MUST carry enough version and provenance information to explain what produced them even when the producing software no longer exists.

## Aggregate model

### 1. Source Artifact

A Source Artifact is an immutable byte-bearing input object accepted by the system.

Examples include an original camera RAW file, a DNG created from another source, or a future capture container. Non-RAW inputs MAY be supported by adapters, but they do not expand the guaranteed RAW-development scope of this project.

A Source Artifact has:

- stable artifact identity;
- one or more cryptographic content digests when bytes are available;
- media/container type;
- byte length when known;
- optional lineage relations to other Source Artifacts;
- optional capture/group relations when multiple artifacts are known to originate from the same capture event.

A filename, filesystem path, cloud object key, or library record is a locator, not artifact identity.

A byte-identical physical copy MAY share the same content identity. A byte-changing conversion, metadata rewrite, normalization, or DNG conversion is a new Source Artifact even when it represents the same photographic capture.

Source metadata is not part of Source Artifact semantics merely because it is stored inside the file. Once decoded, it is represented as Source Assertions with provenance.

### 2. Observation Run and Observation Set

An **Observation Run** is an execution event: a particular implementation, configuration, dependency set, and procedure collection acting on one or more declared input representations of a Source Artifact.

An **Observation Set** is the immutable result of an Observation Run. It contains observations and references the run that produced them.

Run identity and result identity are different. Two repeated runs MAY produce semantically equivalent or byte-identical Observation Sets while remaining distinct execution events.

An Observation Set is composed of three information classes:

#### 2.1 Source Assertion

A Source Assertion is a value declared or encoded by the source and decoded by a procedure without adding a photographic-development judgment.

It is an assertion **from the source**, not necessarily an independently verified fact about the physical scene or camera.

Examples:

- camera make and model;
- recorded ISO;
- shutter duration;
- aperture;
- focal length;
- orientation;
- sensor black/white levels when present;
- as-shot white-balance coefficients when present.

A Source Assertion MUST identify its source field or extraction procedure when ambiguity is possible. Conflicting source assertions MAY coexist if provenance distinguishes them.

#### 2.2 Measurement

A numeric or structured result computed from source data under an explicit Signal Domain and Analysis Procedure.

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

#### 2.3 Derived Representation

A derived representation intended to preserve or expose information for machine or human inspection.

Examples:

- diagnostic preview;
- luminance map;
- channel-clipping mask;
- low-resolution linear representation;
- histogram image;
- segmentation-independent spatial map.

An Derived Representation MUST declare:

- how it was produced;
- its dimensions;
- coordinate system;
- color or numeric domain;
- transfer function when applicable;
- lossy/lossless status;
- compression/encoding;
- relationship to the Source Artifact.

A Derived Representation is a transformed view of source information for inspection, measurement support, or downstream reasoning. It is not a substitute for the Source Artifact and does not by itself assert that an interpretation is true.

### 3. Signal Domain

A Signal Domain specifies the signal/image representation state in which a value has meaning.

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

An Analysis Procedure defines the semantic method used to produce a Source Assertion, Measurement, or Derived Representation.

Procedure identity describes **what method means**, not which executable happened to run it.

A procedure definition MUST identify:

- stable procedure ID;
- procedure version;
- required inputs and their domains;
- algorithmic or transformation semantics sufficient to distinguish materially different methods;
- parameters that are part of the procedure contract.

Two outputs with the same field name but produced by materially different procedures are not assumed equivalent.

### 5. Procedure Implementation and Execution

A **Procedure Implementation** is an executable realization of an Analysis Procedure. Multiple implementations MAY conform to the same procedure definition.

An **Observation Run** records the execution provenance required to explain an actual result, including as applicable:

- procedure-definition IDs and versions;
- implementation name/version/build or immutable code identity;
- decoder/library dependencies whose behavior is material;
- runtime parameters;
- execution environment when it can materially affect results;
- execution timestamp;
- input Source Artifact and representation identities.

Reproducibility claims MUST state whether they mean semantic equivalence, tolerance-bounded numeric equivalence, or byte-identical output.

### 6. Development Context

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

### 7. Interpretation

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

### 8. Development Decision

A Development Decision is an explicit choice of development action based on an Observation Set, optional Interpretation, and Development Context.

A decision MAY contain:

- target-neutral intent assertions where a stable semantic definition actually exists;
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

### 11. Rendered Result

A Rendered Result is a materialized visual or numeric output produced by applying a Development Decision, directly or through a Target Encoding, using a declared Target Model or renderer.

A Rendered Result SHOULD retain enough provenance to identify:

- Source Artifact;
- Development Decision;
- Target Model / renderer version;
- Target Encoding when used;
- output color/transfer domain;
- material rendering parameters.

Rendered Results are derived artifacts. They do not overwrite Source Artifacts or Observations.

### 12. Evaluation Record

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
  -> rendered result identity (when materialized)
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

A **Photo Observation Package (POP)** MAY serialize an Observation Set and its Derived Representations for transport, caching, archival inspection, or AI input.

POP is a serialization profile, not the domain itself.

Changing POP layout MUST NOT require changing the meaning of Source Artifact, Observation, Interpretation, or Development Decision.

## Current-project mapping

The current concept maps as follows:

| Current term | Core concept |
| --- | --- |
| RAW file | Source Artifact |
| converted DNG | distinct Source Artifact linked by lineage |
| EXIF / RAW metadata extraction | Source Assertions |
| histogram / clipping / noise calculation | Measurements |
| neutral / highlight / shadow small previews | Derived Representations |
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
8. **Re-execution test** — can two executions of the same semantic procedure be distinguished from the Observation Set they produce?
9. **Lineage test** — does a byte-changing conversion create a new Source Artifact while preserving its derivation from the prior artifact?

If a concept fails these tests, it SHOULD live in an adapter, profile, experiment, or extension rather than Core.
