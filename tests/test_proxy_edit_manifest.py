import json
from pathlib import Path

import jsonschema
import yaml

from rda_toolchain.registry import ROOT


def test_proxy_edit_manifest_example_conforms_to_schema():
    schema = json.loads(
        (ROOT / "schemas/proxy-edit-manifest.schema.json").read_text(encoding="utf-8")
    )
    fixture = yaml.safe_load(
        (ROOT / "fixtures/proxy-edit-manifest-example.yml").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(schema).validate(fixture)
