import yaml

from rda_toolchain.pop import validate_pop_fixture_contract
from rda_toolchain.registry import ROOT, load_registry, validate_fixture_contract, validate_registry


def test_repository_registry_is_valid():
    result = validate_registry(load_registry())
    assert result.result == "valid", result.as_dict()


def test_definition_registry_fixture_contract():
    fixture_path = ROOT / "fixtures/definition-registry-cases.yml"
    fixture_document = yaml.safe_load(fixture_path.read_text(encoding="utf-8")) or {}
    failures = validate_fixture_contract(fixture_document)
    assert failures == []


def test_pop_fixture_contract():
    fixture_path = ROOT / "fixtures/photo-observation-package-cases.yml"
    fixture_document = yaml.safe_load(fixture_path.read_text(encoding="utf-8")) or {}
    failures = validate_pop_fixture_contract(fixture_document)
    assert failures == []


def test_registry_has_no_premature_raw_measurement_definitions():
    registry = load_registry()
    ids = {definition.get("id") for definition in registry.get("definitions") or []}
    premature = {
        "rda.observation.tone.luminance-percentile",
        "rda.observation.tone.highlight-headroom",
        "rda.observation.quality.noise-level",
    }
    assert ids.isdisjoint(premature)
