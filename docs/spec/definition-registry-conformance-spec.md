---
pdm_version: "0.1"
id: "rda-definition-registry-conformance"
name: "Definition Registry Conformance"
slug: "definition-registry-conformance"
type: "specification.core"
status: "active"
created_at: "2026-09-26"
updated_at: "2026-09-26"
owners:
  - "Period-Inc"
relations:
  - type: "depends_on"
    target: "rda-definition-registry"
---

# Definition Registry Conformance

## Purpose

This document defines observable conformance behavior for the RDA Definition Registry.

A Registry is not considered interoperable merely because it parses as YAML or JSON. Conforming validators must agree on semantic integrity findings for the normative fixtures.

## Scope

This specification governs:

- schema validation;
- definition identity and version uniqueness;
- namespace/kind consistency;
- internal definition-reference resolution;
- supersession integrity;
- stability dependencies;
- registry bundle identity;
- normative fixture expectations.

It does not yet define Observation Set validation, POP validation, numerical analyzer tolerances, or target-adapter conformance.

## Requirements

A conforming Definition Registry Validator MUST:

1. validate a resolved Registry object against `schemas/definition-registry.schema.json`;
2. enforce the cross-validation rules in `docs/spec/definition-registry-spec.md`;
3. emit the stable finding codes defined here;
4. reproduce the expectations in `fixtures/definition-registry-cases.yml`;
5. treat unrecognized optional fields as preservable extension data rather than silently assigning them semantics;
6. never repair substantive definition meaning automatically.

## Finding codes

### Schema

- `RDA-REGISTRY-SCHEMA-INVALID` — the Registry violates the JSON Schema.
- `RDA-REGISTRY-ID-KIND-MISMATCH` — a definition ID namespace does not match its declared kind.
- `RDA-REGISTRY-DEFINITION-DUPLICATE` — the same `(id, version)` appears more than once.
- `RDA-REGISTRY-REFERENCE-MISSING` — an internal Definition Reference cannot be resolved.
- `RDA-REGISTRY-REFERENCE-KIND-INVALID` — a resolved reference points to the wrong definition kind.
- `RDA-REGISTRY-SUPERSESSION-CYCLE` — supersession references form a cycle.
- `RDA-REGISTRY-STABLE-DEPENDS-PROVISIONAL` — a stable definition depends semantically on a provisional definition without an explicit policy exception.
- `RDA-REGISTRY-RELEASE-IDENTITY-INVALID` — a declared Registry release identity does not uniquely identify one resolved bundle.
- `RDA-REGISTRY-DEFINITION-MUTATED` — the same released `(id, version)` is observed with different canonical semantic content.
- `RDA-REGISTRY-PROCEDURE-OUTPUT-INVALID` — a procedure output reference does not resolve to an Observation Definition.
- `RDA-REGISTRY-PROCEDURE-DOMAIN-INVALID` — a procedure input signal-domain reference does not resolve to a Signal Domain Definition.
- `RDA-REGISTRY-OBSERVATION-DOMAIN-INVALID` — an Observation Definition signal-domain reference does not resolve to a Signal Domain Definition.
- `RDA-REGISTRY-OBSERVATION-PROCEDURE-INVALID` — an Observation Definition procedure reference does not resolve to an Analysis Procedure Definition.

Message wording is non-normative. Finding-code meaning is normative.

## Fixture contract

`fixtures/definition-registry-cases.yml` is normative cross-implementation test data.

Each case contains:

- stable fixture `id`;
- expected result: `valid`, `warning`, or `invalid`;
- expected finding codes where applicable;
- a minimal resolved Registry object or mutation sufficient to reproduce the condition.

A new Core rule that changes an existing fixture result requires a compatibility review.

## Validation order

A validator SHOULD evaluate in this order:

1. parse;
2. JSON Schema;
3. unique identity;
4. namespace/kind coherence;
5. reference resolution;
6. reference kind constraints;
7. supersession graph;
8. stability dependency rules;
9. release/bundle identity rules.

If schema failure prevents reliable interpretation of later stages, the validator MAY stop after `RDA-REGISTRY-SCHEMA-INVALID`.

## Canonical semantic content

To detect mutation of a released definition, implementations need a canonical-content comparison contract.

Until a canonical byte serialization is standardized, implementations SHOULD compare a normalized semantic projection that:

- includes every normative definition field;
- excludes transport-only comments;
- excludes registry ordering;
- preserves arrays where order is semantically meaningful;
- sorts object keys;
- serializes UTF-8 consistently.

The exact canonical serialization is intentionally not stable in v0.1.

Therefore, cross-tool `RDA-REGISTRY-DEFINITION-MUTATED` conformance is provisional until canonicalization is separately specified.

## Repair policy

Automatic repair MAY:

- reorder non-semantic Registry entries;
- normalize formatting;
- add missing derived indexes that do not change meaning.

Automatic repair MUST NOT:

- change a definition ID;
- change a definition version;
- change normative description or contract fields;
- redirect a missing reference;
- change provisional/stable/deprecated status;
- infer a supersession relation.

Semantic changes require a new reviewed Registry version/definition version.
