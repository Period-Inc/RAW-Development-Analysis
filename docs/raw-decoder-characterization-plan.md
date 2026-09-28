---
pdm_version: "0.1"
id: "rda-raw-decoder-characterization-plan"
name: "RAW Decoder Characterization Plan"
slug: "raw-decoder-characterization"
type: "planning.plan"
status: "active"
created_at: "2026-09-26"
updated_at: "2026-09-26"
owners:
  - "Period-Inc"
relations:
  - type: "depends_on"
    target: "rda-foundational-axioms"
  - type: "depends_on"
    target: "rda-base-observation-profile-plan"
---

# RAW Decoder Characterization Plan

## Objective

Characterize what a practical RAW decoder exposes before RDA defines stable sensor-side Observation semantics.

The first implementation probe uses rawpy/LibRaw only as an experimental instrument.

It MUST NOT make rawpy, LibRaw, or their current behavior part of Core meaning.

The experiment begins before postprocessing because LibRaw/rawpy postprocessing can perform scaling, white balance, demosaic, automatic brightness, highlight handling, gamma, and color conversion depending on configuration.

The initial probe therefore observes the unpacked visible sensor array and decoder-exposed metadata without calling `postprocess()`.

## Scope

In scope:

- exact source digest;
- decoder implementation/version;
- visible unpacked sensor array shape/type;
- CFA/color-index representation where exposed;
- active/visible dimensions and margins where exposed;
- decoder-reported black levels;
- decoder-reported white/saturation levels;
- CFA pattern and color description;
- differences across representative RAW formats/cameras.

Out of scope for this probe:

- development decisions;
- display previews;
- demosaic quality;
- white-balance rendering;
- color-space conversion;
- stable clipping/headroom measurements;
- stable noise measurements;
- claims that decoder-reported levels are physical ground truth.

## Steps

### 1. Probe the unpacked sensor-side state

Run:

`rda probe-raw <path-to-raw>`

The command intentionally does not call rawpy `postprocess()`.

The output records a source SHA-256 digest plus the decoder-exposed state required to inspect later Signal Domain candidates.

### 2. Test three candidate sensor domains

The experiment evaluates these candidates without promoting them to the stable Registry yet.

#### Candidate A — unpacked source sensor code

Concept:

- visible sensor sample values exposed after RAW container decoding/unpacking;
- no RDA black subtraction;
- no RDA white normalization;
- no RDA white balance;
- no RDA demosaic;
- native CFA/color-index arrangement retained.

This domain is closest to decoder-exposed sensor codes, but RDA MUST NOT call it camera-original bytes: unpacking and decoder-specific interpretation have already occurred.

Required Signal State candidates:

- Source Artifact identity;
- decoder implementation/build;
- active/visible array bounds;
- CFA/color-index semantics;
- numeric dtype/range;
- decoder-exposed black-level metadata;
- decoder-exposed white/saturation metadata.

#### Candidate B — black-referenced sensor code

Concept:

`b = s - B(position, channel)`

where:

- `s` is Candidate A sample value;
- `B` is the explicitly identified black-level value/function for that sample.

This candidate remains in sensor-code scale.

Open cases that MUST be tested before stabilization:

- per-channel black levels;
- row/column or region-dependent black levels;
- masked-pixel-derived black;
- negative values after subtraction;
- cameras where metadata and effective decoder behavior differ.

#### Candidate C — saturation-normalized sensor-linear

Concept:

`n = (s - B) / (W - B)`

where `W` is the explicitly identified white/saturation level applicable to that sample.

This is only meaningful when both `B` and `W` semantics are explicit.

The experiment MUST determine:

- global versus channel-specific `W`;
- values above 1 and below 0;
- whether to preserve out-of-range values;
- cameras with multiple gain/readout regimes;
- HDR/multi-frame/stacked RAW cases;
- whether decoder metadata is sufficient to define `W` reproducibly.

No clipping should be silently applied by the normalization definition.

### 3. Compare decoder exposure across fixtures

For each RAW fixture, record:

- whether `raw_image_visible` is available;
- dimensions and dtype;
- CFA/color map;
- black levels;
- `white_level`;
- per-channel camera white levels if available;
- missing/unsupported fields;
- unusual layouts such as non-Bayer or multi-channel sources.

### 4. Detect hidden assumptions

The experiment must explicitly test whether:

- unpacked sensor values change between decoder versions;
- active-area cropping changes;
- black/white metadata changes;
- CFA/color descriptions change;
- camera-specific fallbacks are used.

Any such dependency becomes Procedure Implementation / Run provenance, not hidden Core semantics.

### 5. Promote the minimum viable domain

Only one sensor-side domain needs to become stable first.

Promotion requires:

- exact semantic description;
- representative real RAW fixtures;
- stable Signal State requirements;
- reproducible values or explicitly bounded equivalence;
- no dependence on undocumented decoder behavior;
- a demonstrated observation that benefits from the domain.

## Dependencies

- representative real RAW files;
- rawpy/LibRaw experimental implementation;
- Definition Registry;
- POP;
- Base RAW Observation Profile Plan.

Current implementation research references:

- LibRaw documentation: https://www.libraw.org/docs
- LibRaw data structures / processing parameters: https://www.libraw.org/node/31
- rawpy RawPy API: https://letmaik.github.io/rawpy/api/rawpy.RawPy.html
- rawpy Params API: https://letmaik.github.io/rawpy/api/rawpy.Params.html

These links document the current experimental implementation only. They are not semantic authorities for future RDA Core definitions.

## Completion

This characterization phase is complete when:

- the probe has been run against the representative fixture corpus;
- decoder-exposed states are recorded with source digests;
- anomalous/missing camera cases are documented;
- Candidates A/B/C have explicit accept/reject/revise findings;
- at least one sensor-side Signal Domain is justified for Registry promotion;
- the first mathematically exact measurement can be defined on that domain.
