# SPDX-FileCopyrightText: 2025-present Demi <bjaiye1@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Auto-generated SBML BioModule wrapper for Guyton1972_Autonomics.

Source: biomodels_ebi:MODEL0911270005
Original: https://www.ebi.ac.uk/biomodels/MODEL0911270005
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    from biosim import BioWorld

import biosim
from biosim.signals import (AcceptedSignalProfile, ArraySignal, BioSignal, EventSignal, RecordSignal, ScalarSignal, SignalSpec)

import logging

logger = logging.getLogger(__name__)


def _schema_type(value):
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    return "json"


def _signal_value(signal):
    value = signal.value
    if isinstance(value, dict) and set(value.keys()) == {"payload"}:
        return value["payload"]
    return value


def _rr_get(rr, symbol):
    try:
        return rr[symbol]
    except TypeError:
        if hasattr(rr, "getValue"):
            return rr.getValue(symbol)
        return getattr(rr, symbol)


def _rr_set(rr, symbol, value):
    try:
        rr[symbol] = value
    except TypeError:
        if hasattr(rr, "setValue"):
            rr.setValue(symbol, value)
            return
        setattr(rr, symbol, value)


def _generic_input_spec(description=None):
    return SignalSpec.record(
        schema={"payload": "json"},
        accepted_profiles=(
            AcceptedSignalProfile(signal_type="record", schema={"payload": "json"}),
            AcceptedSignalProfile(signal_type="scalar"),
        ),
        description=description,
    )


def _make_signal(*, source, name, value, emitted_at, spec=None):
    if spec is None:
        if isinstance(value, dict):
            spec = SignalSpec.record(schema={str(key): _schema_type(item) for key, item in value.items()})
        elif isinstance(value, (list, tuple)):
            spec = SignalSpec.record(schema={"payload": "json"})
        else:
            spec = SignalSpec.scalar(dtype=_schema_type(value))

    if spec.signal_type == "scalar":
        return ScalarSignal(source=source, name=name, value=value, emitted_at=emitted_at, spec=spec)
    if spec.signal_type == "array":
        return ArraySignal(source=source, name=name, value=value, emitted_at=emitted_at, spec=spec)
    if spec.signal_type == "event":
        event_value = value
        if spec.schema is not None and not (isinstance(value, dict) and set(value.keys()) == set(spec.schema.keys())):
            event_value = {"payload": value}
        return EventSignal(source=source, name=name, value=event_value, emitted_at=emitted_at, spec=spec)

    record_value = value
    if not isinstance(value, dict) or set(value.keys()) != set((spec.schema or {}).keys()):
        record_value = {"payload": value}
    return RecordSignal(source=source, name=name, value=record_value, emitted_at=emitted_at, spec=spec)

class SbmlGuyton1972Autonomics(biosim.BioModule):
    """BioModule wrapper for SBML model: Guyton1972_Autonomics."""

    _PORT_TO_SBML: dict[str, str] = {
        "arterial_pressure": "PA",
        "arterial_oxygen": "PO2ART",
        "left_atrial_pressure": "PLA",
        "right_atrial_pressure": "PRA",
    }
    _SPECIES_LABELS: dict[str, str] = {
        "AUC": "AUC",
        "AU6C": "AU6C",
        "AUC2": "AUC2",
        "AUC3": "AUC3",
    }
    _STATE_VARIABLES: list[str] = [
        "AUC",
        "AU6C",
        "AUC2",
        "AUC3",
    ]
    def __init__(self, model_path: str = "data/MODEL0911270005.xml", integration_step: float = 0.01) -> None:
        self.integration_step = float(integration_step)
        self._model_path = Path(__file__).parent.parent / model_path
        self._t = 0.0
        self._rr = None
        self._species_ids: list[str] = []
        self._outputs: Dict[str, BioSignal] = {}
        self._param_overrides: dict[str, float] = {}
        self._initial_overrides: dict[str, float] = {}
        self._pending_overrides: bool = False
        self._pending_initial: bool = False

    def setup(self, config: Optional[Dict[str, Any]] = None) -> None:
        import tellurium as te

        self._rr = te.loadSBMLModel(str(self._model_path))
        floating_ids = list(self._rr.getFloatingSpeciesIds())
        boundary_ids = list(self._rr.getBoundarySpeciesIds())
        parameter_ids = list(self._rr.getGlobalParameterIds())
        self._species_ids = floating_ids or boundary_ids or parameter_ids
        self._t = 0.0

    def reset(self) -> None:
        if self._rr is not None:
            self._rr.reset()
        self._t = 0.0
        self._outputs = {}
        self._pending_overrides = bool(self._param_overrides)
        self._pending_initial = bool(self._initial_overrides)

    def inputs(self) -> dict[str, SignalSpec]:
        return {
            "arterial_pressure": SignalSpec.scalar(
                dtype="float64",
                accepted_profiles=(
                    AcceptedSignalProfile(signal_type="scalar", dtype="float64", accepted_units=("dimensionless",)),
                    AcceptedSignalProfile(signal_type="record", schema={"payload": "json"}),
                ),
                description="Sets arterial pressure for the simulation scenario. Default `103.525`.",
            ),
            "arterial_oxygen": SignalSpec.scalar(
                dtype="float64",
                accepted_profiles=(
                    AcceptedSignalProfile(signal_type="scalar", dtype="float64", accepted_units=("dimensionless",)),
                    AcceptedSignalProfile(signal_type="record", schema={"payload": "json"}),
                ),
                description="Sets arterial oxygen for the simulation scenario. Default `97.0439`.",
            ),
            "left_atrial_pressure": SignalSpec.scalar(
                dtype="float64",
                accepted_profiles=(
                    AcceptedSignalProfile(signal_type="scalar", dtype="float64", accepted_units=("dimensionless",)),
                    AcceptedSignalProfile(signal_type="record", schema={"payload": "json"}),
                ),
                description="Sets left atrial pressure for the simulation scenario. Default `2.0`.",
            ),
            "right_atrial_pressure": SignalSpec.scalar(
                dtype="float64",
                accepted_profiles=(
                    AcceptedSignalProfile(signal_type="scalar", dtype="float64", accepted_units=("dimensionless",)),
                    AcceptedSignalProfile(signal_type="record", schema={"payload": "json"}),
                ),
                description="Sets right atrial pressure for the simulation scenario. Default `0.00852183`.",
            ),
            "integration_step": SignalSpec.scalar(
                dtype="float64",
                accepted_profiles=(
                    AcceptedSignalProfile(signal_type="scalar", dtype="float64", accepted_units=("s",)),
                    AcceptedSignalProfile(signal_type="record", schema={"payload": "json"}),
                ),
                description="ODE solver integration step in seconds. Smaller = more precise but slower.",
            ),
            "parameter_overrides": _generic_input_spec(
                description="Map of SBML global parameter name to override value. Use this to override any parameter not surfaced as a named port above."
            ),
            "initial_conditions": _generic_input_spec(
                description="Map of SBML species ID to initial concentration override, applied at setup and on reset."
            ),
        }

    def set_inputs(self, inputs):
        if not inputs:
            return
        # Per-lab contextual scalar ports map to SBML global parameters
        # via self._PORT_TO_SBML; updates are staged into _param_overrides
        # so _apply_overrides() pushes them into roadrunner.
        for port_name, sbml_id in self._PORT_TO_SBML.items():
            if port_name not in inputs:
                continue
            v = _signal_value(inputs[port_name])
            try:
                self._param_overrides[sbml_id] = float(v)
                self._pending_overrides = True
            except (TypeError, ValueError):
                pass
        if "integration_step" in inputs:
            v = _signal_value(inputs["integration_step"])
            try:
                step = float(v)
                if step > 0:
                    self.integration_step = step
            except (TypeError, ValueError):
                pass
        if "parameter_overrides" in inputs:
            v = _signal_value(inputs["parameter_overrides"])
            if isinstance(v, dict):
                for k, val in v.items():
                    try:
                        self._param_overrides[str(k)] = float(val)
                    except (TypeError, ValueError):
                        pass
                self._pending_overrides = True
        if "initial_conditions" in inputs:
            v = _signal_value(inputs["initial_conditions"])
            if isinstance(v, dict):
                for k, val in v.items():
                    try:
                        self._initial_overrides[str(k)] = float(val)
                    except (TypeError, ValueError):
                        pass
                self._pending_initial = True

    def _apply_overrides(self):
        if self._rr is None:
            return
        if self._pending_initial:
            for sid, value in self._initial_overrides.items():
                try:
                    _rr_set(self._rr, sid, float(value))
                except (KeyError, RuntimeError, ValueError):
                    logger.warning("initial_conditions: species %s not in model", sid)
            self._pending_initial = False
        if self._pending_overrides:
            for pid, value in self._param_overrides.items():
                try:
                    _rr_set(self._rr, pid, float(value))
                except (KeyError, RuntimeError, ValueError):
                    logger.warning("parameter_overrides: parameter %s not in model", pid)
            self._pending_overrides = False

    def outputs(self) -> dict[str, SignalSpec]:
        return {
            'state': SignalSpec.record(schema={'payload': 'json'},
                description='Species concentrations and SBML state variables (mixed units, see SBML file).'),
            'species_labels': SignalSpec.record(schema={'payload': 'json'},
                description='Static map of SBML species id to human-friendly label.'),
        }

    def advance_window(self, start: float, end: float, inputs=None) -> None:
        if inputs:
            self.set_inputs(inputs)
        t = float(end)
        if self._rr is None:
            self.setup()
        self._apply_overrides()

        if t > self._t:
            self._rr.simulate(self._t, t)
            self._t = t

        source_name = getattr(self, "_world_name", self.__class__.__name__)
        # Curated _STATE_VARIABLES wins; fall back to floating-species ids when empty.
        keys = list(self._STATE_VARIABLES) if self._STATE_VARIABLES else list(self._species_ids)
        state = {}
        for sid in keys:
            try:
                state[sid] = float(_rr_get(self._rr, sid))
            except (KeyError, ValueError, TypeError):
                logger.warning("Failed to read %s, defaulting to 0.0", sid)
                state[sid] = 0.0

        specs = self.outputs()
        self._outputs = {
            "state": _make_signal(source=source_name, name="state", value=state, emitted_at=t, spec=specs.get("state")),
            "species_labels": _make_signal(source=source_name, name="species_labels", value=dict(self._SPECIES_LABELS), emitted_at=t, spec=specs.get("species_labels")),
        }
    def get_outputs(self) -> Dict[str, BioSignal]:
        return dict(self._outputs)


# Canonical alias for stable entrypoint naming.
Guyton1972AutonomicsModel0911270005Model = SbmlGuyton1972Autonomics
