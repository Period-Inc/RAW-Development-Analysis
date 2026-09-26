from __future__ import annotations

import copy
import json
import pathlib
import re
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from .registry import Finding, ROOT, ValidationResult, validate_registry


_COLLECTION_IDS = {
    "sources": "source_id",
    "implementations": "implementation_id",
    "runs": "run_id",
    "procedure_invocations": "invocation_id",
    "signal_states": "signal_state_id",
    "observations": "observation_id",
    "assets": "asset_id",
    "coordinate_spaces": "coordinate_space_id",
}


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_pop(path: pathlib.Path | str) -> dict[str, Any]:
    path = pathlib.Path(path)
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_findings(manifest: dict[str, Any], *, root: pathlib.Path) -> list[Finding]:
    schema = _load_json(root / "schemas/photo-observation-package.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    findings: list[Finding] = []
    for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path)
        findings.append(
            Finding(
                "RDA-POP-SCHEMA-INVALID",
                location or "manifest",
                error.message,
            )
        )
    return findings


def _ref_key(ref: dict[str, Any]) -> tuple[str, str]:
    return (str(ref.get("id") or ""), str(ref.get("version") or ""))


def _definition_map(manifest: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    closure = manifest.get("semantic_closure") or {}
    return {
        _ref_key(definition): definition
        for definition in closure.get("definitions") or []
        if isinstance(definition, dict)
    }


def _closure_registry(manifest: dict[str, Any]) -> dict[str, Any]:
    closure = manifest.get("semantic_closure") or {}
    return {
        "rda_registry": "0.1",
        "registry_id": closure.get("registry_id"),
        "registry_version": closure.get("registry_version"),
        "namespace": closure.get("namespace"),
        "status": closure.get("status"),
        "definitions": copy.deepcopy(closure.get("definitions") or []),
    }


def _object_index(manifest: dict[str, Any]) -> tuple[dict[str, tuple[str, dict[str, Any]]], list[Finding]]:
    index: dict[str, tuple[str, dict[str, Any]]] = {}
    findings: list[Finding] = []
    for collection, id_field in _COLLECTION_IDS.items():
        for position, item in enumerate(manifest.get(collection) or []):
            if not isinstance(item, dict):
                continue
            object_id = str(item.get(id_field) or "")
            if not object_id:
                continue
            path = f"{collection}[{position}].{id_field}"
            if object_id in index:
                prior_collection, _ = index[object_id]
                findings.append(
                    Finding(
                        "RDA-POP-ID-DUPLICATE",
                        path,
                        f"object id {object_id!r} is already used in {prior_collection}",
                    )
                )
            else:
                index[object_id] = (collection, item)
    return index, findings


def _definition(
    definitions: dict[tuple[str, str], dict[str, Any]],
    ref: Any,
    *,
    path: str,
    expected_kind: str | None,
    findings: list[Finding],
) -> dict[str, Any] | None:
    if not isinstance(ref, dict):
        return None
    key = _ref_key(ref)
    definition = definitions.get(key)
    if definition is None:
        findings.append(
            Finding(
                "RDA-POP-DEFINITION-MISSING",
                path,
                f"definition not present in semantic closure: {key[0]}@{key[1]}",
            )
        )
        return None
    if expected_kind and definition.get("kind") != expected_kind:
        findings.append(
            Finding(
                "RDA-POP-DEFINITION-KIND-INVALID",
                path,
                f"expected definition kind {expected_kind}, got {definition.get('kind')}",
            )
        )
        return None
    return definition


def _check_ref(
    ref: Any,
    *,
    allowed_collections: set[str],
    object_index: dict[str, tuple[str, dict[str, Any]]],
    path: str,
    findings: list[Finding],
) -> dict[str, Any] | None:
    ref_id = str(ref or "")
    entry = object_index.get(ref_id)
    if entry is None:
        findings.append(
            Finding(
                "RDA-POP-REFERENCE-MISSING",
                path,
                f"unresolved package reference: {ref_id}",
            )
        )
        return None
    collection, item = entry
    if collection not in allowed_collections:
        findings.append(
            Finding(
                "RDA-POP-REFERENCE-MISSING",
                path,
                f"reference {ref_id!r} resolves to {collection}, expected {sorted(allowed_collections)}",
            )
        )
        return None
    return item


def _is_rational(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("kind") == "rational"
        and isinstance(value.get("numerator"), int)
        and not isinstance(value.get("numerator"), bool)
        and isinstance(value.get("denominator"), int)
        and not isinstance(value.get("denominator"), bool)
        and value.get("denominator") != 0
    )


def _is_asset_ref(value: Any) -> bool:
    return isinstance(value, dict) and value.get("kind") == "asset_ref" and bool(value.get("asset_id"))


def _matches_value_contract(value: Any, contract: dict[str, Any]) -> bool:
    expected = contract.get("type")
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "rational":
        return _is_rational(value)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    if expected in {"binary", "image", "tensor"}:
        return _is_asset_ref(value)
    return False


def _safe_package_path(value: str) -> bool:
    if not value or "\\" in value:
        return False
    if value.startswith("/"):
        return False
    if re.match(r"^[A-Za-z]:", value):
        return False
    parts = pathlib.PurePosixPath(value).parts
    return ".." not in parts and all(part not in {"", "."} for part in parts)


def validate_pop(
    manifest: dict[str, Any],
    *,
    root: pathlib.Path | str = ROOT,
) -> ValidationResult:
    root = pathlib.Path(root)
    findings = _schema_findings(manifest, root=root)
    if findings:
        return ValidationResult("invalid", tuple(findings))

    closure_result = validate_registry(_closure_registry(manifest), root=root)
    if closure_result.result != "valid":
        findings.append(
            Finding(
                "RDA-POP-SEMANTIC-CLOSURE-INVALID",
                "semantic_closure",
                "embedded definition closure does not satisfy the Definition Registry contract",
                list(closure_result.finding_codes),
            )
        )
        return ValidationResult("invalid", tuple(findings))

    definitions = _definition_map(manifest)
    object_index, id_findings = _object_index(manifest)
    findings.extend(id_findings)

    sources = {str(item.get("source_id")): item for item in manifest.get("sources") or [] if isinstance(item, dict)}
    implementations = {
        str(item.get("implementation_id")): item
        for item in manifest.get("implementations") or []
        if isinstance(item, dict)
    }
    runs = {str(item.get("run_id")): item for item in manifest.get("runs") or [] if isinstance(item, dict)}
    invocations = {
        str(item.get("invocation_id")): item
        for item in manifest.get("procedure_invocations") or []
        if isinstance(item, dict)
    }
    signal_states = {
        str(item.get("signal_state_id")): item
        for item in manifest.get("signal_states") or []
        if isinstance(item, dict)
    }
    observations = {
        str(item.get("observation_id")): item
        for item in manifest.get("observations") or []
        if isinstance(item, dict)
    }
    assets = {str(item.get("asset_id")): item for item in manifest.get("assets") or [] if isinstance(item, dict)}

    for index, source in enumerate(manifest.get("sources") or []):
        if not isinstance(source, dict):
            continue
        for j, ref in enumerate(source.get("lineage") or []):
            _check_ref(
                ref,
                allowed_collections={"sources"},
                object_index=object_index,
                path=f"sources[{index}].lineage[{j}]",
                findings=findings,
            )

    for index, run in enumerate(manifest.get("runs") or []):
        if not isinstance(run, dict):
            continue
        _check_ref(
            run.get("implementation_ref"),
            allowed_collections={"implementations"},
            object_index=object_index,
            path=f"runs[{index}].implementation_ref",
            findings=findings,
        )
        for j, ref in enumerate(run.get("source_refs") or []):
            _check_ref(
                ref,
                allowed_collections={"sources"},
                object_index=object_index,
                path=f"runs[{index}].source_refs[{j}]",
                findings=findings,
            )

    for index, invocation in enumerate(manifest.get("procedure_invocations") or []):
        if not isinstance(invocation, dict):
            continue
        _check_ref(
            invocation.get("run_ref"),
            allowed_collections={"runs"},
            object_index=object_index,
            path=f"procedure_invocations[{index}].run_ref",
            findings=findings,
        )
        procedure_definition = _definition(
            definitions,
            invocation.get("procedure_ref"),
            path=f"procedure_invocations[{index}].procedure_ref",
            expected_kind="procedure",
            findings=findings,
        )

        if procedure_definition is not None:
            declared_roles = [
                str(item.get("role") or "")
                for item in procedure_definition.get("inputs") or []
                if isinstance(item, dict) and item.get("role")
            ]
            bindings = [
                item for item in invocation.get("input_bindings") or []
                if isinstance(item, dict)
            ]
            if len(declared_roles) > 1:
                bound_roles = [str(item.get("role") or "") for item in bindings]
                if sorted(bound_roles) != sorted(declared_roles):
                    findings.append(
                        Finding(
                            "RDA-POP-INPUT-BINDING-INVALID",
                            f"procedure_invocations[{index}].input_bindings",
                            f"declared input roles {declared_roles}, bound roles {bound_roles}",
                        )
                    )
        for j, ref in enumerate(invocation.get("input_refs") or []):
            if str(ref or "") not in object_index:
                findings.append(
                    Finding(
                        "RDA-POP-REFERENCE-MISSING",
                        f"procedure_invocations[{index}].input_refs[{j}]",
                        f"unresolved package reference: {ref}",
                    )
                )
        for j, binding in enumerate(invocation.get("input_bindings") or []):
            if not isinstance(binding, dict):
                continue
            ref = binding.get("ref")
            if str(ref or "") not in object_index:
                findings.append(
                    Finding(
                        "RDA-POP-REFERENCE-MISSING",
                        f"procedure_invocations[{index}].input_bindings[{j}].ref",
                        f"unresolved package reference: {ref}",
                    )
                )
        for j, ref in enumerate(invocation.get("output_observation_refs") or []):
            if str(ref or "") not in observations:
                findings.append(
                    Finding(
                        "RDA-POP-INVOCATION-OUTPUT-INCOHERENT",
                        f"procedure_invocations[{index}].output_observation_refs[{j}]",
                        f"declared output observation does not exist: {ref}",
                    )
                )
        for j, ref in enumerate(invocation.get("output_signal_state_refs") or []):
            if str(ref or "") not in signal_states:
                findings.append(
                    Finding(
                        "RDA-POP-INVOCATION-OUTPUT-INCOHERENT",
                        f"procedure_invocations[{index}].output_signal_state_refs[{j}]",
                        f"declared output signal state does not exist: {ref}",
                    )
                )

    for index, state in enumerate(manifest.get("signal_states") or []):
        if not isinstance(state, dict):
            continue
        _definition(
            definitions,
            state.get("domain_ref"),
            path=f"signal_states[{index}].domain_ref",
            expected_kind="signal_domain",
            findings=findings,
        )
        if state.get("source_ref") is not None:
            _check_ref(
                state.get("source_ref"),
                allowed_collections={"sources"},
                object_index=object_index,
                path=f"signal_states[{index}].source_ref",
                findings=findings,
            )
        if state.get("parent_signal_state_ref") is not None:
            _check_ref(
                state.get("parent_signal_state_ref"),
                allowed_collections={"signal_states"},
                object_index=object_index,
                path=f"signal_states[{index}].parent_signal_state_ref",
                findings=findings,
            )
        if state.get("produced_by_invocation_ref") is not None:
            _check_ref(
                state.get("produced_by_invocation_ref"),
                allowed_collections={"procedure_invocations"},
                object_index=object_index,
                path=f"signal_states[{index}].produced_by_invocation_ref",
                findings=findings,
            )

    for index, observation in enumerate(manifest.get("observations") or []):
        if not isinstance(observation, dict):
            continue
        base_path = f"observations[{index}]"
        definition = _definition(
            definitions,
            observation.get("definition_ref"),
            path=f"{base_path}.definition_ref",
            expected_kind="observation",
            findings=findings,
        )
        invocation = _check_ref(
            observation.get("procedure_invocation_ref"),
            allowed_collections={"procedure_invocations"},
            object_index=object_index,
            path=f"{base_path}.procedure_invocation_ref",
            findings=findings,
        )

        state = None
        if observation.get("signal_state_ref") is not None:
            state = _check_ref(
                observation.get("signal_state_ref"),
                allowed_collections={"signal_states"},
                object_index=object_index,
                path=f"{base_path}.signal_state_ref",
                findings=findings,
            )

        if definition is None:
            continue

        if observation.get("status") == "known":
            contract = definition.get("value_contract") or {}
            value = observation.get("value")
            if not _matches_value_contract(value, contract):
                findings.append(
                    Finding(
                        "RDA-POP-VALUE-CONTRACT-INVALID",
                        f"{base_path}.value",
                        f"value does not match contract type {contract.get('type')}",
                    )
                )

            if _is_asset_ref(value):
                asset_id = str(value.get("asset_id"))
                if asset_id not in assets:
                    findings.append(
                        Finding(
                            "RDA-POP-ASSET-MISSING",
                            f"{base_path}.value.asset_id",
                            f"unknown asset: {asset_id}",
                        )
                    )

        allowed_domains = {
            _ref_key(ref)
            for ref in definition.get("signal_domain_refs") or []
            if isinstance(ref, dict)
        }
        if allowed_domains and observation.get("status") == "known":
            if state is None:
                findings.append(
                    Finding(
                        "RDA-POP-SIGNAL-STATE-MISSING",
                        f"{base_path}.signal_state_ref",
                        "known observation requires a Signal State",
                    )
                )
            else:
                state_domain = _ref_key(state.get("domain_ref") or {})
                if state_domain not in allowed_domains:
                    findings.append(
                        Finding(
                            "RDA-POP-SIGNAL-DOMAIN-INVALID",
                            f"{base_path}.signal_state_ref",
                            f"Signal State domain {state_domain[0]}@{state_domain[1]} is not allowed",
                        )
                    )

        allowed_procedures = {
            _ref_key(ref)
            for ref in definition.get("procedure_refs") or []
            if isinstance(ref, dict)
        }
        if allowed_procedures and invocation is not None:
            actual_procedure = _ref_key(invocation.get("procedure_ref") or {})
            if actual_procedure not in allowed_procedures:
                findings.append(
                    Finding(
                        "RDA-POP-PROCEDURE-INVALID",
                        f"{base_path}.procedure_invocation_ref",
                        f"procedure {actual_procedure[0]}@{actual_procedure[1]} is not allowed",
                    )
                )

    for index, asset in enumerate(manifest.get("assets") or []):
        if not isinstance(asset, dict):
            continue
        locator = asset.get("locator") or {}
        if locator.get("type") == "package_path":
            value = str(locator.get("value") or "")
            if not _safe_package_path(value):
                findings.append(
                    Finding(
                        "RDA-POP-PACKAGE-PATH-UNSAFE",
                        f"assets[{index}].locator.value",
                        f"unsafe package path: {value!r}",
                    )
                )

    return ValidationResult("valid" if not findings else "invalid", tuple(findings))


_PATH_TOKEN = re.compile(r"([A-Za-z0-9_]+)(?:\[([0-9]+)\])?")


def _set_path(target: Any, path: str, value: Any) -> None:
    current = target
    tokens = path.split(".")
    for index, token in enumerate(tokens):
        match = _PATH_TOKEN.fullmatch(token)
        if not match:
            raise ValueError(f"unsupported fixture path: {path}")
        name, list_index = match.groups()
        last = index == len(tokens) - 1
        if not isinstance(current, dict) or name not in current:
            raise KeyError(path)
        if list_index is None:
            if last:
                current[name] = copy.deepcopy(value)
                return
            current = current[name]
        else:
            sequence = current[name]
            item_index = int(list_index)
            if last:
                sequence[item_index] = copy.deepcopy(value)
                return
            current = sequence[item_index]


def _delete_path(target: Any, path: str) -> None:
    current = target
    tokens = path.split(".")
    for index, token in enumerate(tokens):
        match = _PATH_TOKEN.fullmatch(token)
        if not match:
            raise ValueError(f"unsupported fixture path: {path}")
        name, list_index = match.groups()
        last = index == len(tokens) - 1
        if list_index is None:
            if last:
                del current[name]
                return
            current = current[name]
        else:
            sequence = current[name]
            item_index = int(list_index)
            if last:
                del sequence[item_index]
                return
            current = sequence[item_index]


def resolve_pop_fixture(case_id: str, fixture_document: dict[str, Any]) -> dict[str, Any]:
    bases = fixture_document.get("bases") or {}
    cases = {str(case.get("id")): case for case in fixture_document.get("cases") or []}
    case = cases[case_id]
    base_name = str(case.get("from") or "")
    if base_name not in bases:
        raise KeyError(f"unknown POP fixture base: {base_name}")
    manifest = copy.deepcopy(bases[base_name])

    mutation = case.get("mutation") or {}
    for entry in mutation.get("set") or []:
        _set_path(manifest, str(entry["path"]), entry.get("value"))
    for path in mutation.get("delete") or []:
        _delete_path(manifest, str(path))

    return manifest


def validate_pop_fixture_contract(
    fixture_document: dict[str, Any],
    *,
    root: pathlib.Path | str = ROOT,
) -> list[str]:
    failures: list[str] = []
    for case in fixture_document.get("cases") or []:
        case_id = str(case.get("id") or "")
        manifest = resolve_pop_fixture(case_id, fixture_document)
        actual = validate_pop(manifest, root=root)
        expected_result = str(case.get("expect") or "")
        expected_codes = tuple(case.get("findings") or [])

        if actual.result != expected_result:
            failures.append(
                f"{case_id}: expected {expected_result}, got {actual.result} "
                f"({', '.join(actual.finding_codes)})"
            )
            continue

        missing = [code for code in expected_codes if code not in set(actual.finding_codes)]
        if missing:
            failures.append(
                f"{case_id}: missing findings {missing}; got {list(actual.finding_codes)}"
            )

    return failures
