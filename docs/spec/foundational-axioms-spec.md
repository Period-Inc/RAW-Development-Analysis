---
pdm_version: "0.1"
id: "rda-foundational-axioms"
name: "RDA Foundational Axioms"
slug: "foundational-axioms"
type: "specification.core"
status: "active"
created_at: "2026-09-26"
updated_at: "2026-09-26"
owners:
  - "Period-Inc"
relations: []
---

# RDA Foundational Axioms

## Purpose

This document defines the smallest set of principles that give RAW Development Analysis its identity.

The Core Domain may grow, split, rename concepts, add capabilities, or replace implementations.

These axioms sit below that evolution.

A change that contradicts one of these axioms is not an ordinary Core evolution. It is a change to the identity of the system and MUST be treated as such.

The preservation horizon is 1,000 years.

The goal is not to preserve today's software. The goal is to preserve enough meaning that future people and systems can reconstruct what was observed, what was inferred, what was changed, what remained uncertain, and how each state came to exist.

## Scope

These axioms constrain:

- Core domain design;
- Observation semantics;
- provenance;
- transformations;
- interpretation and decision layers;
- comparison and retrieval;
- serialization;
- migrations;
- implementations;
- future applications built on the foundation.

They intentionally avoid current photographic, vendor, AI, database, file-format, and programming-language details.

## Requirements

All normative Core specifications MUST remain consistent with these axioms.

When a design choice conflicts with an axiom, the axiom takes precedence.

A specification MUST NOT weaken an axiom merely for implementation convenience, performance, compatibility with a vendor, or product requirements.

## Simplicity as a preservation strategy

The foundational layer MUST remain deliberately small and simple.

This is not aesthetic minimalism. It is a preservation strategy.

Complex systems depend on more assumptions, more context, more conventions, and more hidden knowledge. Over long periods, those dependencies are more likely to disappear.

Simple distinctions are easier to:

- explain;
- copy;
- translate;
- reimplement;
- verify;
- migrate;
- preserve across organizations, cultures, technologies, and centuries.

Therefore RDA SHOULD place only principles that are both fundamental and difficult to reduce further in this layer.

Anything that can safely live in the Core Domain, a profile, a procedure, an implementation, or an application SHOULD remain outside the Foundational Axioms.

The preservation premise is:

> Simpler things are more likely to survive.

## Axiom 1 — Describe before deciding

**The system describes the world before deciding what should be done about it.**

Observation, Interpretation, and Decision are fundamentally different kinds of information.

A statement about what was observed MUST NOT silently contain a recommendation.

A recommendation MUST NOT rewrite the observation that led to it.

This is the primary epistemic boundary of RDA.

Conceptually:

```text
World / Source
    ↓
Observation
    ↓
Interpretation
    ↓
Decision
```

The arrows represent dependency, not equivalence.

## Axiom 2 — Representation is not the thing represented

A Source Artifact, Observation, preview, fingerprint, embedding, XMP file, index entry, and rendered image are different representations or derived artifacts.

None of them becomes identical to the underlying event, scene, capture, or meaning merely because it is useful.

A representation MUST identify the domain and transformation assumptions required to interpret it.

Derived convenience MUST NOT erase the distinction between source and representation.

## Axiom 3 — Derivation creates lineage, not replacement

A transformation creates a new state or artifact related to what came before.

It does not retroactively replace its source.

Examples include:

- RAW to DNG;
- source to normalized signal;
- observation to fingerprint;
- decision to XMP;
- old schema to migrated schema;
- original image to crop or recompression.

When information changes, the system SHOULD preserve the lineage:

```text
before
  ↓ transformation
after
```

History is appendable. It is not silently rewritten.

## Axiom 4 — Provenance is part of meaning

A derived value without recoverable provenance is semantically incomplete.

For any durable derived information, it MUST be possible to recover, as applicable:

- what input it came from;
- which definition gave it meaning;
- which procedure produced it;
- which implementation executed that procedure;
- which materially relevant parameters were used;
- which transformation path led to the result.

The same numeric value produced under different semantics MUST NOT be assumed to mean the same thing.

## Axiom 5 — Unknown, ambiguity, and contradiction are information

Absence of certainty is not absence of information.

The system MUST preserve distinctions such as:

- unknown;
- unavailable;
- unsupported;
- not applicable;
- conflicting assertions;
- competing interpretations;
- unresolved lineage;
- uncertain measurements.

These states MUST NOT be collapsed into zero, false, empty, default, or a guessed answer for convenience.

Where multiple plausible interpretations remain, coexistence is preferable to silent forced convergence.

## Axiom 6 — Meaning must survive implementation extinction

No durable semantic meaning may depend solely on a current:

- executable;
- library;
- AI model;
- database;
- vector index;
- hosted service;
- repository;
- vendor;
- organization;
- file path;
- undocumented behavior.

Implementations are replaceable realizations.

Definitions and preserved records MUST contain enough semantic closure that a future implementation can recover the intended meaning without requiring the original runtime to exist.

## Axiom 7 — Loss must be explicit

Lossy transformation is permitted.

Hidden loss is not.

If a transformation, compression, projection, migration, redaction, approximation, or interpretation discards information, that loss MUST be identifiable when it materially affects future interpretation.

A future migration that cannot preserve a semantic distinction MUST record that fact rather than silently substituting a new meaning.

## Axiom 8 — Identity, similarity, and usefulness are different relations

Being identical, being derived from the same origin, being visually similar, being semantically similar, and being useful for the same task are different relations.

The system MUST NOT collapse them into one generic similarity or relevance concept.

This applies to:

- duplicate detection;
- fingerprinting;
- comparison;
- search;
- ranking;
- archive grouping;
- development-reference selection.

Composite scores MAY exist, but their component meanings and combination procedure MUST remain recoverable.

## Axiom 9 — Projections are rebuildable; authority is upstream

Indexes, caches, rankings, thumbnails, vector stores, search results, and convenience projections are operational derivatives.

They MUST NOT become the sole authority for preserved source or observation meaning.

A projection SHOULD be reconstructable from more authoritative preserved records whenever practical.

The loss of an index must not imply the loss of the archive's meaning.

## Axiom 10 — Future reinterpretation must remain possible

Preservation is not only about reproducing an old answer.

It is also about preserving enough source, observation, definitions, and provenance that future people can ask new questions.

Therefore the system SHOULD preserve reusable observations instead of only final conclusions.

A later Interpretation MAY disagree with an earlier Interpretation without invalidating the original Observation.

A later Decision MAY differ from an earlier Decision without rewriting history.

The system preserves the possibility of new understanding.

## Axiom precedence

The intended precedence is:

```text
Foundational Axioms
        ↓
Core Domain
        ↓
Domain Specifications / Profiles
        ↓
Serialization / Registry / Procedures
        ↓
Implementations
        ↓
Applications / Services
```

Lower layers may specialize higher layers but MUST NOT contradict them.

## Change policy

These axioms are expected to change far less frequently than the Core Domain.

A proposed change to an axiom MUST:

1. state which prior axiom is being changed;
2. explain why the existing principle is no longer valid;
3. identify which historical records or semantics could be reinterpreted;
4. determine whether the change constitutes a new major identity of RDA;
5. preserve the prior axiom set as a historical semantic reference.

Normal feature work MUST NOT modify these axioms.

## Preservation statement

RDA's deepest commitment is:

> Preserve the distinction between the world, its records, our interpretations, and our decisions.

Everything else may be replaced.
