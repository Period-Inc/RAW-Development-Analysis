from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

import yaml

from .lrcat import trace_fixture_manifest
from .pop import load_pop, validate_pop, validate_pop_fixture_contract
from .raw_probe import probe_raw
from .registry import ROOT, load_registry, validate_fixture_contract, validate_registry


def _print_json(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rda")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-registry", help="Validate the RDA semantic definition registry")
    validate.add_argument("path", nargs="?", default=str(ROOT / "registry/definitions.yml"))

    fixtures = sub.add_parser("test-registry-fixtures", help="Run registry conformance fixtures")
    fixtures.add_argument(
        "path",
        nargs="?",
        default=str(ROOT / "fixtures/definition-registry-cases.yml"),
    )

    validate_pop_cmd = sub.add_parser("validate-pop", help="Validate a POP manifest")
    validate_pop_cmd.add_argument("path")

    probe_raw_cmd = sub.add_parser(
        "probe-raw",
        help="Experimentally inspect decoder-exposed unpacked RAW sensor state",
    )
    probe_raw_cmd.add_argument("path")

    lrcat_fixtures = sub.add_parser(
        "trace-lrcat-fixtures",
        help="Experimentally trace Lightroom catalog state for a fixture manifest",
    )
    lrcat_fixtures.add_argument("path")
    lrcat_fixtures.add_argument("--workspace", required=True)
    lrcat_fixtures.add_argument("--out", required=True)

    pop_fixtures = sub.add_parser("test-pop-fixtures", help="Run POP conformance fixtures")
    pop_fixtures.add_argument(
        "path",
        nargs="?",
        default=str(ROOT / "fixtures/photo-observation-package-cases.yml"),
    )

    args = parser.parse_args(argv)

    if args.command == "validate-registry":
        result = validate_registry(load_registry(pathlib.Path(args.path)))
        _print_json(result.as_dict())
        return 0 if result.result == "valid" else 1

    if args.command == "test-registry-fixtures":
        document = yaml.safe_load(pathlib.Path(args.path).read_text(encoding="utf-8")) or {}
        failures = validate_fixture_contract(document)
        _print_json({"result": "valid" if not failures else "invalid", "failures": failures})
        return 0 if not failures else 1

    if args.command == "validate-pop":
        result = validate_pop(load_pop(pathlib.Path(args.path)))
        _print_json(result.as_dict())
        return 0 if result.result == "valid" else 1

    if args.command == "probe-raw":
        try:
            _print_json(probe_raw(pathlib.Path(args.path)))
        except RuntimeError as exc:
            _print_json({"result": "unavailable", "error": str(exc)})
            return 2
        return 0

    if args.command == "trace-lrcat-fixtures":
        try:
            result = trace_fixture_manifest(
                pathlib.Path(args.path),
                workspace=pathlib.Path(args.workspace),
                output_dir=pathlib.Path(args.out),
            )
            _print_json(result)
            return 0
        except (FileNotFoundError, ValueError, sqlite3.Error) as exc:
            _print_json({"result": "invalid", "error": str(exc)})
            return 1

    if args.command == "test-pop-fixtures":
        document = yaml.safe_load(pathlib.Path(args.path).read_text(encoding="utf-8")) or {}
        failures = validate_pop_fixture_contract(document)
        _print_json({"result": "valid" if not failures else "invalid", "failures": failures})
        return 0 if not failures else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
