---
pdm_version: "0.1"
id: "rda-photo-observation-package-conformance"
name: "Photo Observation Package Conformance"
slug: "photo-observation-package-conformance"
type: "specification.core"
status: "active"
created_at: "2026-09-26"
updated_at: "2026-09-26"
owners:
  - "Period-Inc"
relations:
  - type: "depends_on"
    target: "rda-photo-observation-package"
  - type: "depends_on"
    target: "rda-definition-registry-conformance"
---

# Photo Observation Package Conformance

## Purpose

This document defines stable machine-facing findings for validating POP manifests beyond structural JSON Schema.

## Scope

The initial conformance surface covers package identity, internal references, semantic closure, observation value contracts, procedure/domain compatibility, Signal State presence, asset references, and safe package-local paths.

Byte-level asset digest verification and numerical equivalence of analyzer outputs are separate later conformance layers.

## Requirements

A conforming POP Validator MUST first validate the manifest against `schemas/photo-observation-package.schema.json`.

It MUST then validate the embedded semantic closure using the Definition Registry contract and perform the cross-object checks defined here.

The validator MUST reproduce `fixtures/photo-observation-package-cases.yml`.

## Finding codes

- `RDA-POP-SCHEMA-INVALID` — the manifest violates the POP structural schema.
- `RDA-POP-ID-DUPLICATE` — two package objects share one package-wide object ID.
- `RDA-POP-REFERENCE-MISSING` — an internal package-object reference cannot be resolved.
- `RDA-POP-SEMANTIC-CLOSURE-INVALID` — the embedded Definition closure is invalid or incomplete.
- `RDA-POP-DEFINITION-MISSING` — a manifest Definition Reference is absent from the semantic closure.
- `RDA-POP-DEFINITION-KIND-INVALID` — a Definition Reference resolves to an incompatible definition kind.
- `RDA-POP-VALUE-CONTRACT-INVALID` — a known Observation value does not match its Observation Definition value contract.
- `RDA-POP-PROCEDURE-INVALID` — an Observation was produced by an invocation whose procedure is incompatible with the Observation Definition.
- `RDA-POP-SIGNAL-STATE-MISSING` — an Observation Definition requires a Signal Domain/State but the Observation has no Signal State.
- `RDA-POP-SIGNAL-DOMAIN-INVALID` — the referenced Signal State does not conform to an allowed Signal Domain Definition.
- `RDA-POP-ASSET-MISSING` — an asset-valued Observation references an unknown asset.
- `RDA-POP-PACKAGE-PATH-UNSAFE` — a package-local asset locator is absolute or traverses outside the package.
- `RDA-POP-INVOCATION-OUTPUT-INCOHERENT` — an invocation explicitly declares an output reference that does not resolve to the matching output object.
- `RDA-POP-INPUT-BINDING-INVALID` — a multi-input invocation omits, duplicates, or mislabels input roles required by its Analysis Procedure Definition.

Message wording is non-normative.

## Value-contract checking

The validator MUST preserve the distinction between JSON numbers and exact RDA typed values.

For `value_contract.type: rational`, the value MUST use the RDA rational object with integer numerator and non-zero integer denominator.

A floating-point approximation is not conforming merely because it is numerically close.

For `image`, `binary`, and `tensor` contracts, POP v0.1 expects an `asset_ref` value unless a future compatible profile defines another exact representation.

## Definition closure

The POP semantic closure MUST be sufficient to resolve the definitions required by the package without consulting "latest" registry state.

The closure is validated as a resolved Definition Registry subset.

A package that references a definition omitted from its closure is invalid even if the definition exists in the current repository Registry.

## Input-role compatibility

When an Analysis Procedure Definition declares more than one input role, a POP invocation MUST use role-qualified `input_bindings`.

The set of bound roles MUST match the declared procedure input roles unless the procedure definition explicitly marks a role optional in a future compatible extension.

A required role MUST NOT occur more than once unless the procedure definition explicitly declares a repeated/multi-valued role.

This preserves directional and relational meaning for comparisons.

## Signal State compatibility

If an Observation Definition declares `signal_domain_refs`, a known Measurement/Derived Representation MUST identify a Signal State unless the definition explicitly states that no concrete state is required.

The Signal State's `domain_ref` MUST be one of the allowed domain references.

Required Signal State property validation will become stricter as individual Signal Domain Definitions stabilize.

## Path safety

For `package_path` locators, validators MUST reject:

- absolute POSIX paths;
- absolute Windows paths;
- path components equal to `..`;
- drive-prefixed paths;
- paths whose normalization escapes the package root.

This is a transport-safety check and does not make filesystem paths semantic identities.

## Fixture contract

`fixtures/photo-observation-package-cases.yml` is normative test data.

Changing a stable finding meaning or changing an existing fixture expectation requires compatibility review.
