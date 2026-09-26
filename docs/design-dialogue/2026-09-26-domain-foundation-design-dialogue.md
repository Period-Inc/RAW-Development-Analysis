---
pdm_version: "0.1"
id: "rda-domain-foundation-dialogue"
name: "Domain Foundation Design Dialogue"
slug: "domain-foundation"
type: "design.dialogue"
status: "active"
created_at: "2026-09-26"
updated_at: "2026-09-26"
owners:
  - "Period-Inc"
relations:
  - type: "explores"
    target: "rda-core-domain"
  - type: "informs"
    target: "rda-observation-model"
---

# Domain Foundation Design Dialogue

## Context

The project began from a practical workflow: mechanically analyze a RAW file, provide compact parameters and low-cost reference imagery to AI, ask AI to determine useful development adjustments, and generate XMP so that Lightroom starts closer to a useful base development.

A shared baseline preset, currently `_Fundamental`, already provides a meaningful starting point. The design discussion identified the intermediate representation between RAW decoding and AI reasoning as the highest-leverage architectural boundary.

The project is intentionally being designed for a lifetime measured in decades rather than around the current Adobe/AI toolchain.

## Question

What definitions must be made stable now so that future RAW formats, decoders, reasoning systems, development engines, and storage formats can replace today's implementations without invalidating historical observations or forcing the domain model to be rewritten?

## Exploration

### Package-first design

One proposal was to define a concrete "Photo Observation Package" containing JSON, maps, and several small diagnostic previews.

This is useful operationally but insufficient as the top-level abstraction because a directory/ZIP layout would become the accidental domain model.

### Domain-first design

The preferred approach defines Source Asset, Observation Set, Measurement Domain, Analysis Procedure, Development Context, Interpretation, Development Intent, Development Decision, Target Model, Target Encoding, and Evaluation Record first.

A package then becomes one serialization of an Observation Set.

### Observation versus interpretation

Early parameter ideas included labels such as underexposed, backlit, too warm, portrait, and scene type.

These may be useful, but they are not mechanical observations in the strict sense. Keeping them in the same namespace as measured percentiles, clipping ratios, or decoded metadata would make later auditing and algorithm replacement difficult.

They therefore belong to Interpretation or to an explicitly typed interpretation extension.

### RAW bytes versus derived evidence

Passing arbitrary RAW byte slices to a general AI was considered. The bytes have weak portable meaning without decoder, CFA, black-level, white-level, color and packing context.

The preferred direction is to mechanically transform RAW data into explicit measurements and evidence representations whose semantics are defined.

The original source remains the authority.

### Numeric-only versus visual-only evidence

Numeric summaries alone discard spatial relationships. A normal preview alone hides sensor headroom and may contain a camera-maker look.

The candidate observation profile therefore combines typed measurements with standardized low-cost evidence representations such as luminance/clipping maps and diagnostic previews.

### Universal development parameters

A universal set of sliders would simplify implementation but risks false equivalence. Controls such as Adobe Highlights/Shadows may change semantics by process version and may not map to another renderer.

The preferred model distinguishes vendor-neutral Development Intent where semantics are genuinely portable from target-specific operations where they are not.

## Outcomes

The following outcomes are accepted and canonicalized:

1. The domain is stage-separated as Source -> Observation -> Interpretation -> Development Decision -> Target Encoding.
2. Development Context, including `_Fundamental`, is outside Observation.
3. AI is a replaceable Interpretation/Decision actor.
4. XMP and Lightroom are target-side adapters.
5. Photo Observation Package is a serialization candidate, not the domain authority.
6. Derived observations require explicit provenance, procedure identity, and measurement domains.
7. Missing/unsupported data must remain distinguishable from actual zero/false values.
8. Preview and map assets are evidence representations and must declare their transform/lossiness.
9. Vendor-specific controls must not be given false universal semantics.
10. Historical interpretability has priority over silent normalization to the newest analyzer.

The following questions remain deliberately unresolved:

- exact stable ID syntax and registry format for measurement/domain/procedure definitions;
- exact reference RAW decoding pipeline used by the initial base observation profile;
- exact mathematical definition of luminance and percentile measurements;
- exact clipping/headroom definitions across RAW formats;
- exact diagnostic preview transforms and color-management pipeline;
- whether quantitative maps should use image containers, array containers, or both;
- which initial measurements materially improve development decisions in real experiments;
- how much of Development Intent can be made target-neutral without creating false equivalence;
- privacy/export policy for GPS, serial numbers, timestamps, faces, and other sensitive evidence;
- whether "Photo Observation Package (POP)" remains the public serialization name after schema experiments.

Unresolved items MUST NOT be smuggled into Core through implementation convenience.

## Canonicalization

Accepted domain semantics are canonicalized in:

- `rda-core-domain` — `docs/spec/core-domain-spec.md`
- `rda-evolution-policy` — `docs/spec/evolution-and-compatibility-spec.md`
- `rda-observation-model` — `docs/spec/observation-set-spec.md`
- `rda-adr-observation-boundary` — `docs/architecture/2026-09-26-observation-boundary-decision.md`

This Design Dialogue remains non-normative and preserves the reasoning and unresolved boundary questions that should drive the next specification and experiments.
