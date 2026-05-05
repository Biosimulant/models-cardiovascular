# SPDX-FileCopyrightText: 2026-present Biosimulant Team
#
# SPDX-License-Identifier: MIT
"""Scenario driver for a cardiovascular lab.

Emits a baseline window, a physiological challenge window, and a recovery window
using the lab's public contextual input ports. The core SBML model remains the
source of scientific dynamics; this module only supplies time-varying inputs and
plain-language scenario metadata.
"""
from __future__ import annotations

from typing import Any, Optional

import biosim
from biosim.signals import RecordSignal, ScalarSignal, SignalSpec


class CardiovascularScenarioModel(biosim.BioModule):
    def __init__(
        self,
        scenario_name: str = "Physiological challenge",
        scenario_description: str = "Baseline, challenge, and recovery input protocol.",
        baseline_until: float = 0.25,
        challenge_until: float = 0.75,
        schedule: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        if baseline_until < 0:
            raise ValueError("baseline_until must be non-negative")
        if challenge_until <= baseline_until:
            raise ValueError("challenge_until must be greater than baseline_until")
        self.scenario_name = str(scenario_name)
        self.scenario_description = str(scenario_description)
        self.baseline_until = float(baseline_until)
        self.challenge_until = float(challenge_until)
        self.schedule = dict(schedule or {})
        self._outputs: dict[str, Any] = {}
        self._t = 0.0

    def setup(self, config: Optional[dict[str, Any]] = None) -> None:
        self._t = 0.0
        self._publish(0.0)

    def reset(self) -> None:
        self._outputs = {}
        self._t = 0.0
        self._publish(0.0)

    def inputs(self) -> dict[str, SignalSpec]:
        return {}

    def outputs(self) -> dict[str, SignalSpec]:
        specs: dict[str, SignalSpec] = {}
        for port, cfg in self.schedule.items():
            specs[port] = SignalSpec.scalar(
                dtype="float64",
                emitted_unit=str(cfg.get("unit") or "dimensionless"),
                description=str(cfg.get("description") or f"Scenario value for {port}."),
            )
        specs["scenario_metadata"] = SignalSpec.record(
            schema={"payload": "json"},
            description="Plain-language scenario name, timing, active input, and event markers.",
        )
        return specs

    def set_inputs(self, inputs: dict[str, Any] | None) -> None:
        return

    def advance_window(self, start: float, end: float, inputs=None) -> None:
        self._t = float(end)
        self._publish(self._t)

    def get_outputs(self) -> dict[str, Any]:
        return dict(self._outputs)

    def _phase(self, t: float) -> str:
        if t < self.baseline_until - 1e-12:
            return "baseline"
        if t < self.challenge_until - 1e-12:
            return "challenge"
        return "recovery"

    def _value_for(self, cfg: dict[str, Any], phase: str) -> float:
        key = phase if phase in cfg else "baseline"
        try:
            return float(cfg.get(key, cfg.get("baseline", 0.0)))
        except (TypeError, ValueError):
            return 0.0

    def _metadata(self, phase: str) -> dict[str, Any]:
        active_port = None
        for port, cfg in self.schedule.items():
            if cfg.get("active"):
                active_port = port
                break
        active_cfg = self.schedule.get(active_port or "", {})
        events = [
            {"time": self.baseline_until, "label": "Challenge starts"},
            {"time": self.challenge_until, "label": "Recovery starts"},
        ]
        return {
            "scenario_name": self.scenario_name,
            "scenario_description": self.scenario_description,
            "phase": phase,
            "baseline_until": self.baseline_until,
            "challenge_until": self.challenge_until,
            "active_port": active_port,
            "active_label": active_cfg.get("label") or (active_port or "scenario input").replace("_", " "),
            "baseline_value": active_cfg.get("baseline"),
            "challenge_value": active_cfg.get("challenge"),
            "recovery_value": active_cfg.get("recovery", active_cfg.get("baseline")),
            "unit": active_cfg.get("unit") or "dimensionless",
            "events": events,
        }

    def _publish(self, t: float) -> None:
        source = getattr(self, "_world_name", self.__class__.__name__)
        phase = self._phase(float(t))
        specs = self.outputs()
        outputs: dict[str, Any] = {}
        for port, cfg in self.schedule.items():
            outputs[port] = ScalarSignal(
                source=source,
                name=port,
                value=self._value_for(cfg, phase),
                emitted_at=float(t),
                spec=specs[port],
            )
        outputs["scenario_metadata"] = RecordSignal(
            source=source,
            name="scenario_metadata",
            value={"payload": self._metadata(phase)},
            emitted_at=float(t),
            spec=specs["scenario_metadata"],
        )
        self._outputs = outputs
