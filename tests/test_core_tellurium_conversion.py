from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

from biosim.contrib.sbml import TelluriumSBMLBioModule


REPO_ROOT = Path(__file__).resolve().parents[1]
CORE_SOURCES = sorted(REPO_ROOT.glob("labs/*/models/core/src/*.py"))


def _load_module(path: Path):
    module_name = f"cardiovascular_core_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sbml_symbols(xml_path: Path) -> set[str]:
    root = ET.parse(xml_path).getroot()
    symbols: set[str] = set()
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag in {"parameter", "species", "compartment"}:
            symbol = element.attrib.get("id")
            if symbol:
                symbols.add(symbol)
        elif tag in {"assignmentRule", "rateRule"}:
            symbol = element.attrib.get("variable")
            if symbol:
                symbols.add(symbol)
        elif tag == "initialAssignment":
            symbol = element.attrib.get("symbol")
            if symbol:
                symbols.add(symbol)
    return symbols


def test_all_core_wrappers_use_tellurium_base() -> None:
    assert len(CORE_SOURCES) == 27
    for source in CORE_SOURCES:
        module = _load_module(source)
        wrappers = {
            id(value): value
            for value in module.__dict__.values()
            if isinstance(value, type)
            and issubclass(value, TelluriumSBMLBioModule)
            and value is not TelluriumSBMLBioModule
        }
        assert len(wrappers) == 1, source


def test_core_ports_and_manifests_match_conversion_contract() -> None:
    for source in CORE_SOURCES:
        module = _load_module(source)
        wrapper = next(
            value
            for value in module.__dict__.values()
            if isinstance(value, type)
            and issubclass(value, TelluriumSBMLBioModule)
            and value is not TelluriumSBMLBioModule
        )
        instance = wrapper()
        inputs = instance.inputs()
        outputs = instance.outputs()
        manifest_text = source.parents[1].joinpath("model.yaml").read_text()

        assert {"integration_step", "parameter_overrides", "initial_conditions"}.issubset(inputs)
        assert {"state", "summary", "species_labels"}.issubset(outputs)
        assert outputs["state"].schema == {"payload": "json"}
        assert outputs["species_labels"].schema == {"payload": "json"}
        assert "  - name: summary\n" in manifest_text
        assert "  - name: species_labels\n" in manifest_text


def test_declared_sbml_ports_resolve_to_shipped_xml_symbols() -> None:
    for source in CORE_SOURCES:
        module = _load_module(source)
        wrapper = next(
            value
            for value in module.__dict__.values()
            if isinstance(value, type)
            and issubclass(value, TelluriumSBMLBioModule)
            and value is not TelluriumSBMLBioModule
        )
        xml_path = source.parents[1] / wrapper()._model_path.name
        if not xml_path.exists():
            xml_path = source.parents[1] / "data" / wrapper()._model_path.name
        symbols = _sbml_symbols(xml_path)

        for input_name, (sbml_id, _default, _unit, _description) in wrapper._PARAMETER_INPUTS.items():
            assert sbml_id in symbols, f"{source}: input {input_name!r} maps to missing {sbml_id!r}"
        for observable in wrapper._OBSERVABLES or []:
            assert observable in symbols, f"{source}: observable {observable!r} is not in SBML"
