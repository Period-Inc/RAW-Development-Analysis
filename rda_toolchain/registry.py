from __future__ import annotations

import copy
import json
import pathlib
import re
from dataclasses import dataclass
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = pathlib.Path(__file__).resolve().parent.parent

_KIND_PREFIX = {
    "observation": "rda.observation.",
    "signal_domain": "rda.signal-domain.",
    "procedure": "rda.procedure.",
}


@dataclass(frozen=True)
class Finding:
    code: str
    path: str = "-"
    message: str = ""
    evidence: Any = None

    def as_dict(self) -> dict[str, Any]:
        result = {"code": self.code, "path": self.path, "message": self.message}
        if self.evidence is not None:
            result["evidence"] = self.evidence
        return result


@dataclass(frozen=True)
class ValidationResult:
    result: str
    findings: tuple[Finding, ...]

    @property
    def finding_codes(self) -> tuple[str, ...]:
        return tuple(item.code for item in self.findings)

    def as_dict(self) -> dict[str, Any]:
        return {
            "result": self.result,
            "findings": [item.as_dict() for item in self.findings],
        }


def _classify(findings: Iterable[Finding]) -> str:
    return "valid" if not tuple(findings) else "invalid"


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry(path: pathlib.Path | str | None = None) -> dict[str, Any]:
    path = pathlib.Path(path) if path else ROOT / "registry/definitions.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _schema_findings(
    registry: dict[str, Any],
    *,
    root: pathlib.Path,
) -> list[Finding]:
    schema = _load_json(root / "schemas/definition-registry.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    findings: list[Finding] = []
    for error in sorted(validator.iter_errors(registry), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path)
        suffix = f" ({location})" if location else ""
        findings.append(
            Finding(
                "RDA-REGISTRY-SCHEMA-INVALID",
                location or "registry",
                f"{error.message}{suffix}",
            )
        )
    return findings


def _key(ref: dict[str, Any]) -> tuple[str, str]:
    return (str(ref.get("id") or ""), str(ref.get("version") or ""))


def _definition_path(index: int, definition: dict[str, Any]) -> str:
    return f"definitions[{index}]({definition.get('id')}@{definition.get('version')})"


def _iter_semantic_refs(definition: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any], str | None]]:
    kind = definition.get("kind")

    for i, ref in enumerate(definition.get("supersedes") or []):
        if isinstance(ref, dict):
            yield (f"supersedes[{i}]", ref, None)

    if kind == "observation":
        for i, ref in enumerate(definition.get("signal_domain_refs") or []):
            if isinstance(ref, dict):
                yield (f"signal_domain_refs[{i}]", ref, "signal_domain")
        for i, ref in enumerate(definition.get("procedure_refs") or []):
            if isinstance(ref, dict):
                yield (f"procedure_refs[{i}]", ref, "procedure")

    if kind == "procedure":
        for i, item in enumerate(definition.get("inputs") or []):
            if not isinstance(item, dict):
                continue
            ref = item.get("signal_domain")
            if isinstance(ref, dict):
                yield (f"inputs[{i}].signal_domain", ref, "signal_domain")
        for i, ref in enumerate(definition.get("outputs") or []):
            if isinstance(ref, dict):
                yield (f"outputs[{i}]", ref, "observation")


def _supersession_cycle(definitions: dict[tuple[str, str], dict[str, Any]]) -> bool:
    graph: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for key, definition in definitions.items():
        graph[key] = [
            _key(ref)
            for ref in definition.get("supersedes") or []
            if isinstance(ref, dict) and _key(ref) in definitions
        ]

    visiting: set[tuple[str, str]] = set()
    visited: set[tuple[str, str]] = set()

    def visit(node: tuple[str, str]) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for target in graph.get(node, []):
            if visit(target):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph if node not in visited)


def validate_registry(
    registry: dict[str, Any],
    *,
    root: pathlib.Path | str = ROOT,
) -> ValidationResult:
    root = pathlib.Path(root)
    findings = _schema_findings(registry, root=root)
    if findings:
        return ValidationResult("invalid", tuple(findings))

    raw_definitions = registry.get("definitions") or []
    definitions: dict[tuple[str, str], dict[str, Any]] = {}
    definition_paths: dict[tuple[str, str], str] = {}

    for index, definition in enumerate(raw_definitions):
        if not isinstance(definition, dict):
            continue

        path = _definition_path(index, definition)
        key = (str(definition.get("id") or ""), str(definition.get("version") or ""))

        if key in definitions:
            findings.append(
                Finding(
                    "RDA-REGISTRY-DEFINITION-DUPLICATE",
                    path,
                    f"duplicate definition identity: {key[0]}@{key[1]}",
                )
            )
        else:
            definitions[key] = definition
            definition_paths[key] = path

        kind = str(definition.get("kind") or "")
        prefix = _KIND_PREFIX.get(kind)
        definition_id = str(definition.get("id") or "")
        if prefix and not definition_id.startswith(prefix):
            findings.append(
                Finding(
                    "RDA-REGISTRY-ID-KIND-MISMATCH",
                    f"{path}.id",
                    f"{definition_id!r} does not use the {kind!r} namespace prefix {prefix!r}",
                )
            )

    for key, definition in definitions.items():
        base_path = definition_paths[key]
        source_stability = definition.get("stability")

        for relative_path, ref, expected_kind in _iter_semantic_refs(definition):
            target_key = _key(ref)
            target = definitions.get(target_key)
            path = f"{base_path}.{relative_path}"

            if target is None:
                findings.append(
                    Finding(
                        "RDA-REGISTRY-REFERENCE-MISSING",
                        path,
                        f"unresolved definition reference: {target_key[0]}@{target_key[1]}",
                    )
                )
                continue

            if expected_kind and target.get("kind") != expected_kind:
                if definition.get("kind") == "procedure" and relative_path.startswith("outputs"):
                    code = "RDA-REGISTRY-PROCEDURE-OUTPUT-INVALID"
                elif definition.get("kind") == "procedure" and ".signal_domain" in relative_path:
                    code = "RDA-REGISTRY-PROCEDURE-DOMAIN-INVALID"
                elif definition.get("kind") == "observation" and relative_path.startswith("signal_domain_refs"):
                    code = "RDA-REGISTRY-OBSERVATION-DOMAIN-INVALID"
                elif definition.get("kind") == "observation" and relative_path.startswith("procedure_refs"):
                    code = "RDA-REGISTRY-OBSERVATION-PROCEDURE-INVALID"
                else:
                    code = "RDA-REGISTRY-REFERENCE-KIND-INVALID"

                findings.append(
                    Finding(
                        code,
                        path,
                        f"expected {expected_kind}, got {target.get('kind')}",
                    )
                )
                continue

            if (
                source_stability == "stable"
                and target.get("stability") == "provisional"
                and not relative_path.startswith("supersedes")
            ):
                findings.append(
                    Finding(
                        "RDA-REGISTRY-STABLE-DEPENDS-PROVISIONAL",
                        path,
                        f"stable definition depends on provisional {target_key[0]}@{target_key[1]}",
                    )
                )

    if _supersession_cycle(definitions):
        findings.append(
            Finding(
                "RDA-REGISTRY-SUPERSESSION-CYCLE",
                "definitions",
                "definition supersession graph contains a cycle",
            )
        )

    return ValidationResult(_classify(findings), tuple(findings))


_PATH_TOKEN = re.compile(r"([A-Za-z0-9_]+)(?:\[([0-9]+)\])?")


def _set_path(target: Any, path: str, value: Any) -> None:
    tokens = path.split(".")
    current = target

    for index, token in enumerate(tokens):
        match = _PATH_TOKEN.fullmatch(token)
        if not match:
            raise ValueError(f"unsupported fixture path: {path}")
        name, list_index = match.groups()
        is_last = index == len(tokens) - 1

        if not isinstance(current, dict) or name not in current:
            raise KeyError(f"fixture path not found: {path}")

        if list_index is None:
            if is_last:
                current[name] = copy.deepcopy(value)
                return
            current = current[name]
            continue

        sequence = current[name]
        item_index = int(list_index)
        if not isinstance(sequence, list) or item_index >= len(sequence):
            raise KeyError(f"fixture path not found: {path}")

        if is_last:
            sequence[item_index] = copy.deepcopy(value)
            return
        current = sequence[item_index]

    raise ValueError(f"could not set fixture path: {path}")


def _find_definition(registry: dict[str, Any], ref: dict[str, Any]) -> dict[str, Any]:
    key = _key(ref)
    for definition in registry.get("definitions") or []:
        if isinstance(definition, dict) and _key(definition) == key:
            return definition
    raise KeyError(f"fixture definition not found: {key[0]}@{key[1]}")


def resolve_fixture_registry(
    case_id: str,
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    by_id = {str(case.get("id")): case for case in cases}
    case = by_id[case_id]

    if "registry" in case:
        return copy.deepcopy(case["registry"])

    mutation = case.get("mutation") or {}
    base_id = str(mutation.get("from") or "")
    if not base_id:
        raise ValueError(f"fixture {case_id} has neither registry nor mutation.from")

    registry = resolve_fixture_registry(base_id, cases)

    if "append_definition" in mutation:
        registry.setdefault("definitions", []).append(copy.deepcopy(mutation["append_definition"]))

    replacement = mutation.get("replace")
    if isinstance(replacement, dict):
        target = _find_definition(registry, replacement["definition"])
        target.clear()
        target.update(copy.deepcopy(replacement["with"]))

    replace_reference = mutation.get("replace_reference")
    if isinstance(replace_reference, dict):
        target = _find_definition(registry, replace_reference["in"])
        _set_path(target, str(replace_reference["path"]), replace_reference["value"])

    return registry


def validate_fixture_contract(
    fixture_document: dict[str, Any],
    *,
    root: pathlib.Path | str = ROOT,
) -> list[str]:
    cases = fixture_document.get("cases") or []
    failures: list[str] = []

    for case in cases:
        case_id = str(case.get("id") or "")
        registry = resolve_fixture_registry(case_id, cases)
        actual = validate_registry(registry, root=root)

        expected_result = str(case.get("expect") or "")
        expected_codes = tuple(case.get("findings") or [])

        if actual.result != expected_result:
            failures.append(
                f"{case_id}: expected result {expected_result}, got {actual.result} "
                f"({', '.join(actual.finding_codes)})"
            )
            continue

        if expected_codes:
            actual_set = set(actual.finding_codes)
            missing = [code for code in expected_codes if code not in actual_set]
            if missing:
                failures.append(
                    f"{case_id}: missing findings {missing}; got {list(actual.finding_codes)}"
                )

    return failures
