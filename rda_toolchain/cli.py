from __future__ import annotations

import argparse
import json
import pathlib
import sys

import yaml

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

    return 2


if __name__ == "__main__":
    sys.exit(main())
