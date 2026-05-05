# SPDX-FileCopyrightText: 2026-present Biosimulant Team
#
# SPDX-License-Identifier: MIT
"""Tests for the Niederer2006 Myocyte Relaxation visualization sub-model. No SBML or
roadrunner dependency — drives the viz with synthetic state records."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_MODEL_DIR = Path(__file__).resolve().parents[1]


def _find_bsim_src(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        for candidate in (parent / "biosim" / "src", parent / "bsim-active" / "biosim" / "src"):
            if (candidate / "biosim").is_dir():
                return candidate
    return None


def _ensure_paths() -> None:
    if str(_MODEL_DIR) not in sys.path:
        sys.path.insert(0, str(_MODEL_DIR))
    bsim_src = _find_bsim_src(_MODEL_DIR)
    if bsim_src is not None and str(bsim_src) not in sys.path:
        sys.path.insert(0, str(bsim_src))


_ensure_paths()


from src.niederer2006_myocyte_relaxation_viz import Niederer2006CardiacmyocyterelaxationModel8687196544ModelViz  # noqa: E402
from biosim.signals import RecordSignal, SignalSpec  # noqa: E402


def _record(name: str, payload):
    spec = SignalSpec.record(schema={"payload": "json"})
    return RecordSignal(source="test", name=name, value={"payload": payload},
                        emitted_at=0.0, spec=spec)


def test_instantiation():
    m = Niederer2006CardiacmyocyterelaxationModel8687196544ModelViz()
    assert set(m.inputs().keys()) == {"state", "species_labels", "scenario_metadata"}
    assert set(m.outputs().keys()) == {"run_summary"}


def test_advance_appends_history_and_emits_summary():
    m = Niederer2006CardiacmyocyterelaxationModel8687196544ModelViz()
    state = _record("state", {"v_membrane": -85.0, "ca_intracellular": 0.0001})
    labels = _record("species_labels", {"v_membrane": "Membrane Voltage", "ca_intracellular": "Intracellular Calcium"})
    m.advance_window(0.0, 0.5, inputs={"state": state, "species_labels": labels})
    assert len(m._history) == 1
    out = m.get_outputs()["run_summary"]
    payload = out.value["payload"]
    assert payload["state_variable_count"] == 2
    assert payload["point_count"] == 1
    rows = payload["rows"]
    # Peak row should reference the labelled variable.
    assert any("Membrane Voltage" in r[1] for r in rows)


def test_visualize_emits_two_visuals_with_friendly_labels():
    m = Niederer2006CardiacmyocyterelaxationModel8687196544ModelViz()
    state = _record("state", {"v_membrane": -85.0})
    labels = _record("species_labels", {"v_membrane": "Membrane Voltage"})
    m.advance_window(0.0, 0.5, inputs={"state": state, "species_labels": labels})
    visuals = m.visualize()
    assert len(visuals) == 4
    assert visuals[0]["render"] == "timeseries"
    assert visuals[1]["render"] == "timeseries"
    assert visuals[2]["render"] == "bar"
    assert visuals[3]["render"] == "table"
    series_names = [s["name"] for s in visuals[0]["data"]["series"]]
    assert "Membrane Voltage" in series_names  # SBML name attribute used verbatim
    subtitle = visuals[3]["data"]["subtitle"]
    assert "_" not in subtitle


def test_prettifier_fallback_when_labels_missing():
    m = Niederer2006CardiacmyocyterelaxationModel8687196544ModelViz()
    state = _record("state", {"V_sodium_current_m_gate": 0.5})
    m.advance_window(0.0, 0.5, inputs={"state": state})
    series_name = m.visualize()[0]["data"]["series"][0]["name"]
    assert series_name == "V Sodium Current M Gate"


def test_reset_clears_history():
    m = Niederer2006CardiacmyocyterelaxationModel8687196544ModelViz()
    state = _record("state", {"x": 1.0})
    m.advance_window(0.0, 0.5, inputs={"state": state})
    m.reset()
    assert m._history == []
    assert m.visualize() is None


def test_lab_question_threads_through_visuals():
    m = Niederer2006CardiacmyocyterelaxationModel8687196544ModelViz(lab_question="Does this experiment work?")
    state = _record("state", {"x": 1.0})
    m.advance_window(0.0, 0.5, inputs={"state": state})
    visuals = m.visualize()
    assert visuals[0]["data"]["title"] == "What did the model simulate?"
    assert "Does this experiment work?" in visuals[3]["data"]["subtitle"]


def test_generic_title_when_lab_question_blank():
    m = Niederer2006CardiacmyocyterelaxationModel8687196544ModelViz(lab_question="")
    state = _record("state", {"x": 1.0})
    m.advance_window(0.0, 0.5, inputs={"state": state})
    visuals = m.visualize()
    assert visuals[0]["data"]["title"] == "What did the model simulate?"
