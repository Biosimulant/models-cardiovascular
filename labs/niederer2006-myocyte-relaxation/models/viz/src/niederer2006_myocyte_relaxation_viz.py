# SPDX-FileCopyrightText: 2026-present Biosimulant Team
#
# SPDX-License-Identifier: MIT
"""Visualization sub-model for the Niederer2006 Myocyte Relaxation lab.

Consumes the core SBML simulator's `state` stream and `species_labels` record,
accumulates per-window history, and emits:
  - a timeseries plot of every state variable over the run window
  - a "What Happened" Q&A table with a plain-language subtitle
  - a `run_summary` structured record echoing the table rows

No SBML, no roadrunner, no domain biology — pure data-to-presentation.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Optional

import biosim
from biosim.signals import (
    AcceptedSignalProfile,
    BioSignal,
    RecordSignal,
    SignalSpec,
)

logger = logging.getLogger(__name__)


def _signal_value(signal):
    if signal is None:
        return None
    value = getattr(signal, "value", None)
    if isinstance(value, dict) and set(value.keys()) == {"payload"}:
        return value["payload"]
    return value


_FRIENDLY_LABELS: dict[str, str] = {
    "ADH": "Antidiuretic hormone activity",
    "ADHC": "Antidiuretic hormone concentration",
    "ADHMK": "Kidney water-retention response",
    "ADHMV": "Vascular water-retention response",
    "ADP": "Spent energy pool",
    "AHY": "Volume-receptor drive",
    "AHZ": "Volume-receptor adaptation",
    "AHTH": "Thirst drive",
    "AHTH1": "Delayed thirst drive",
    "AM": "Aldosterone activity",
    "AMC": "Aldosterone concentration effect",
    "AMK": "Potassium-driven aldosterone effect",
    "AMM": "Muscle blood-flow response",
    "AMM1": "Fast muscle-flow response",
    "AMM2": "Delayed muscle-flow response",
    "AMM4": "Local muscle-flow adaptation",
    "AMP": "Low-energy nucleotide pool",
    "AMR": "Renal aldosterone response",
    "ANC": "Angiotensin concentration",
    "ANM": "Angiotensin multiplier",
    "ANP": "Atrial natriuretic peptide activity",
    "ANPC": "Atrial natriuretic peptide concentration",
    "ANPL": "Atrial natriuretic peptide release",
    "ANPR": "Angiotensin pressure response",
    "ANPX": "Atrial natriuretic peptide excretion response",
    "ANT": "Angiotensin tissue effect",
    "ANU": "Angiotensin urine-flow effect",
    "ANV": "Angiotensin vascular effect",
    "AR1": "Non-muscle resistance state 1",
    "AR2": "Non-muscle resistance state 2",
    "AR3": "Non-muscle resistance state 3",
    "ARM": "Non-muscle autoregulation response",
    "ARM1": "Delayed non-muscle autoregulation response",
    "ATP": "Cellular energy pool",
    "ATRFBM": "Atrial feedback multiplier",
    "ATRRFB": "Right-atrial feedback",
    "ATRVFB": "Atrial volume feedback",
    "ATRVM": "Atrial volume multiplier",
    "AU6C": "Autonomic control signal",
    "AUC": "Autonomic response",
    "AUC2": "Delayed autonomic response",
    "AUC3": "Secondary autonomic response",
    "AUHR": "Autonomic heart-rate drive",
    "BFN": "Baseline filtration pressure",
    "BPG": "Bisphosphoglycerate pool",
    "C0": "Closed sodium-channel state 0",
    "C1": "Closed sodium-channel state 1",
    "C2": "Closed sodium-channel state 2",
    "C3": "Closed sodium-channel state 3",
    "C4": "Closed sodium-channel state 4",
    "Ca": "Calcium",
    "CaJSR": "Junctional sarcoplasmic-reticulum calcium",
    "CaNSR": "Network sarcoplasmic-reticulum calcium",
    "CaSS": "Subspace calcium",
    "Ca_b": "Bound calcium",
    "Ca_i": "Cytosolic calcium",
    "Cai": "Cytosolic calcium",
    "Citrulline": "Citrulline",
    "ClosedState_1": "Closed potassium-channel state 1",
    "ClosedState_2": "Closed potassium-channel state 2",
    "ClosedState_3": "Closed potassium-channel state 3",
    "Cms": "Surface-membrane capacitance",
    "Cmt": "T-tubule membrane capacitance",
    "CO2": "Carbon dioxide",
    "DHAP": "Dihydroxyacetone phosphate",
    "E_Na": "Sodium reversal voltage",
    "F6P": "Fructose 6-phosphate",
    "Fe2": "Reduced enzyme pool",
    "Fe2+": "Reduced enzyme pool",
    "Fe2_Arg": "Reduced arginine-bound enzyme",
    "Fe2+_Arg": "Reduced arginine-bound enzyme",
    "Fe2__Arg": "Reduced arginine-bound enzyme",
    "Fe2+_NO": "Reduced nitric-oxide-bound enzyme",
    "Fe2__NO": "Reduced nitric-oxide-bound enzyme",
    "Fe2+_NOHA": "Reduced hydroxyarginine-bound enzyme",
    "Fe3": "Ferric enzyme pool",
    "Fe3+(enos)": "Ferric endothelial nitric oxide synthase pool",
    "Fe3_Arg": "Arginine-bound nitric oxide synthase",
    "Fe3+_Arg": "Arginine-bound nitric oxide synthase",
    "Fe3__Arg": "Arginine-bound nitric oxide synthase",
    "Fe3+_NO": "Nitric-oxide-bound nitric oxide synthase",
    "Fe3_NO": "Nitric-oxide-bound nitric oxide synthase",
    "Fe3__NO": "Nitric-oxide-bound nitric oxide synthase",
    "Fe3_NOHA": "Hydroxyarginine-bound nitric oxide synthase",
    "Fe3+_NOHA": "Hydroxyarginine-bound nitric oxide synthase",
    "Fe3__NOHA": "Hydroxyarginine-bound nitric oxide synthase",
    "Fe3+_O2-_Arg": "Oxygen-and-arginine-bound nitric oxide synthase",
    "Fe3+_O2-_NOHA": "Oxygen-and-hydroxyarginine-bound nitric oxide synthase",
    "Fe3__enos": "Ferric endothelial nitric oxide synthase pool",
    "Fru1,6-P2": "Fructose 1,6-bisphosphate",
    "Fru2,6-P2": "Fructose 2,6-bisphosphate",
    "G3P": "Glyceraldehyde 3-phosphate",
    "G6P": "Glucose 6-phosphate",
    "Gd": "Inactive G-protein state",
    "Glc(ext)": "Extracellular glucose",
    "Glc(int)": "Intracellular glucose",
    "Gt": "Active G-protein state",
    "HDHR": "Hemodynamic heart-rate drive",
    "HM": "Hematocrit",
    "HMD": "Heart-muscle mass deficit",
    "HR": "Heart rate",
    "HSL": "Heart-strength lower state",
    "HSR": "Heart-strength response",
    "I": "Inactivated sodium-channel state",
    "InactivationState": "Inactivated potassium-channel state",
    "IP3": "Inositol trisphosphate",
    "KE": "Extracellular potassium",
    "Ki": "Intracellular potassium",
    "KOD": "Potassium output rate",
    "KTOT": "Total body potassium",
    "Lac": "Lactate",
    "Lac(ext)": "Extracellular lactate",
    "NAE": "Extracellular sodium",
    "NAD": "Oxidized nicotinamide adenine dinucleotide",
    "NADH": "Reduced nicotinamide adenine dinucleotide",
    "Nai": "Intracellular sodium",
    "NED": "Exchangeable sodium",
    "NO": "Nitric oxide",
    "NOHA": "Hydroxyarginine",
    "O1": "Open sodium-channel state 1",
    "O2": "Oxygen",
    "O2_chem": "Oxygen",
    "O2_met": "Oxygen",
    "O2_sodium": "Oxygen",
    "OSA": "Arterial oxygen saturation",
    "OVA": "Venous oxygen saturation",
    "OpenState": "Open potassium-channel state",
    "P": "Inactive receptor state",
    "P2G": "2-phosphoglycerate",
    "P3G": "3-phosphoglycerate",
    "Pc": "Calcium-bound receptor state",
    "Pcg": "Calcium-bound active receptor state",
    "PEP": "Phosphoenolpyruvate",
    "PFI": "Pulmonary fluid influx",
    "Pg": "Active receptor state",
    "PLF": "Pulmonary lymph flow",
    "PO2ALV": "Alveolar oxygen pressure",
    "PO2ART": "Arterial oxygen pressure",
    "P_open": "Open-channel probability",
    "PPI": "Pulmonary interstitial pressure",
    "PRHR": "Pressure-reflex heart-rate drive",
    "Pyr": "Pyruvate",
    "R": "Receptor pool",
    "Rg": "Activated receptor complex",
    "Rl": "Ligand-bound receptor",
    "Rlg": "Ligand-bound active receptor",
    "Rlgp": "Phosphorylated receptor complex",
    "SR": "Stress-relaxation response",
    "SR2": "Delayed stress-relaxation response",
    "SVO": "Stroke volume output",
    "TRPN": "Troponin calcium-binding pool",
    "TVD": "Drinking response",
    "TVZ": "Salt-appetite response",
    "V": "Membrane voltage",
    "VB": "Blood volume",
    "VEC": "Extracellular fluid volume",
    "VIM": "Blood viscosity multiplier",
    "VPF": "Plasma fluid volume",
    "VRC": "Red-cell volume",
    "VTC": "Total capillary volume",
    "Vd": "Deep cytosol volume",
    "Vt": "T-tubule volume",
    "VV6": "Venous stress-relaxation state 1",
    "VV7": "Venous stress-relaxation state 2",
    "alpha_0": "Baseline relaxation coefficient",
    "alpha_r1": "Relaxation-rate coefficient",
    "cardiac delayed rectifier current": "Cardiac delayed rectifier potassium current",
    "citrulline": "Citrulline",
    "g_Na": "Sodium conductance",
    "glycerol": "Glycerol",
    "glycogen": "Glycogen",
    "i_tot": "Total membrane current",
}

_SHORT_UPPER_TOKENS = {
    "NA": "Sodium",
    "K": "Potassium",
    "CA": "Calcium",
    "CL": "Chloride",
    "MG": "Magnesium",
    "PH": "pH",
    "NO": "Nitric oxide",
    "O2": "Oxygen",
    "CO2": "Carbon dioxide",
    "ATP": "Cellular energy pool",
    "ADP": "Spent energy pool",
    "AMP": "Low-energy nucleotide pool",
}


def _title_words(raw: str) -> str:
    s = str(raw).replace("_", " ").strip()
    if not s:
        return str(raw)
    words = []
    for w in s.split():
        upper = w.upper()
        if upper in _SHORT_UPPER_TOKENS:
            words.append(_SHORT_UPPER_TOKENS[upper])
        elif w.isupper() and len(w) > 1:
            words.append(w.title())
        else:
            words.append(w[:1].upper() + w[1:])
    return " ".join(words)


def prettify_label(raw: str) -> str:
    text = str(raw).strip()
    if text in _FRIENDLY_LABELS:
        return _FRIENDLY_LABELS[text]
    return _title_words(text)


def _looks_like_raw_identifier(label: str) -> bool:
    text = str(label).strip()
    if not text:
        return True
    if "_" in text or "__" in text:
        return True
    if re.fullmatch(r"[A-Z]{2,}\d*[A-Z0-9]*", text):
        return True
    if re.fullmatch(r"[A-Za-z]{1,3}\d+", text):
        return True
    if re.fullmatch(r"[kK]\d+", text):
        return True
    if re.search(r"\b(ADH|ANP|IP3|PGI|NOS|IKr|CSQN|RYR|G6P)\b", text):
        return True
    return False


def friendly_label(raw: str, fallback: str | None = None) -> str:
    for candidate in (fallback, raw):
        if candidate is None:
            continue
        text = str(candidate).strip()
        if text in _FRIENDLY_LABELS:
            return _FRIENDLY_LABELS[text]
    display = str(fallback).strip() if fallback else str(raw).strip()
    label = prettify_label(display)
    if _looks_like_raw_identifier(label):
        return "Additional model signal"
    return label


class Niederer2006CardiacmyocyterelaxationModel8687196544ModelViz(biosim.BioModule):
    """Pure presentation sub-model — no SBML, no simulation."""

    def __init__(self, integration_step: float = 0.01,
                 lab_title: str = "Niederer2006 Myocyte Relaxation",
                 lab_question: str = "How quickly does the myocyte relax after calcium activation?") -> None:
        if integration_step <= 0:
            raise ValueError("integration_step must be positive")
        self.integration_step = float(integration_step)
        self.lab_title = str(lab_title)
        self.lab_question = str(lab_question or "").strip()
        self._history: list[tuple[float, dict]] = []
        self._labels: dict[str, str] = {}
        self._latest_state: dict[str, float] = {}
        self._scenario_metadata: dict[str, Any] = {}
        self._outputs: dict[str, BioSignal] = {}
        self._t = 0.0

    def setup(self, config: Optional[dict[str, Any]] = None) -> None:
        self._t = 0.0

    def reset(self) -> None:
        self._history = []
        self._labels = {}
        self._latest_state = {}
        self._scenario_metadata = {}
        self._outputs = {}
        self._t = 0.0

    def inputs(self) -> dict[str, SignalSpec]:
        return {
            "state": SignalSpec.record(
                schema={"payload": "json"},
                accepted_profiles=(
                    AcceptedSignalProfile(signal_type="record", schema={"payload": "json"}),
                ),
                description="Per-window species/state-variable record from the core SBML model.",
            ),
            "species_labels": SignalSpec.record(
                schema={"payload": "json"},
                accepted_profiles=(
                    AcceptedSignalProfile(signal_type="record", schema={"payload": "json"}),
                ),
                description="Static {species_id: human_label} record from the core SBML model.",
            ),
            "scenario_metadata": SignalSpec.record(
                schema={"payload": "json"},
                accepted_profiles=(
                    AcceptedSignalProfile(signal_type="record", schema={"payload": "json"}),
                ),
                description="Scenario timing, active challenge, and plain-language metadata from the scenario driver.",
            ),
        }

    def outputs(self) -> dict[str, SignalSpec]:
        return {
            "run_summary": SignalSpec.record(
                schema={"payload": "json"},
                description=(
                    "Structured Q&A record echoing the rows in the 'What Happened' table."
                ),
            ),
        }

    def set_inputs(self, inputs: dict[str, BioSignal] | None) -> None:
        if not inputs:
            return
        if "species_labels" in inputs:
            v = _signal_value(inputs["species_labels"])
            if isinstance(v, dict) and v:
                self._labels = {str(k): str(val) for k, val in v.items()}
        if "scenario_metadata" in inputs:
            v = _signal_value(inputs["scenario_metadata"])
            if isinstance(v, dict):
                self._scenario_metadata = dict(v)
        if "state" in inputs:
            v = _signal_value(inputs["state"])
            if isinstance(v, dict):
                clean: dict[str, float] = {}
                for k, val in v.items():
                    try:
                        clean[str(k)] = float(val)
                    except (TypeError, ValueError):
                        pass
                self._latest_state = clean

    def advance_window(self, start: float, end: float, inputs=None) -> None:
        if inputs:
            self.set_inputs(inputs)
        t = float(end)
        if self._latest_state:
            self._history.append((t, dict(self._latest_state)))
        self._t = t
        self._publish_summary(t)

    def get_outputs(self) -> dict[str, BioSignal]:
        return dict(self._outputs)

    # ---- presentation helpers ----

    def _label_for(self, sid: str) -> str:
        return friendly_label(sid, self._labels.get(sid))

    def _publish_summary(self, t: float) -> None:
        rows = self._summary_rows(t)
        source = getattr(self, "_world_name", self.__class__.__name__)
        spec = self.outputs()["run_summary"]
        species = list(self._history[0][1].keys()) if self._history else list(self._latest_state.keys())
        payload = {
            "duration_s": t,
            "point_count": len(self._history),
            "state_variable_count": len(self._latest_state),
            "scenario": self._scenario(),
            "response_metrics": self._response_metrics(species) if species else [],
            "rows": rows,
        }
        self._outputs = {
            "run_summary": RecordSignal(
                source=source,
                name="run_summary",
                value={"payload": payload},
                emitted_at=float(t),
                spec=spec,
            )
        }

    def _scenario(self) -> dict[str, Any]:
        return dict(self._scenario_metadata or {})

    def _scenario_events(self) -> list[dict[str, Any]]:
        events = self._scenario().get("events")
        if isinstance(events, list):
            clean = []
            for event in events:
                if not isinstance(event, dict):
                    continue
                try:
                    time = float(event.get("time"))
                except (TypeError, ValueError):
                    continue
                label = str(event.get("label") or "Scenario event")
                clean.append({"time": time, "label": label})
            return clean
        return []

    def _baseline_until(self) -> float | None:
        try:
            return float(self._scenario().get("baseline_until"))
        except (TypeError, ValueError):
            return None

    def _baseline_means(self, species: list[str]) -> dict[str, float]:
        cutoff = self._baseline_until()
        if cutoff is None:
            source = self._history[:1]
        else:
            source = [(t, vals) for t, vals in self._history if t <= cutoff + 1e-12]
            if not source:
                source = self._history[:1]
        means: dict[str, float] = {}
        for sid in species:
            values = [float(vals.get(sid, 0.0)) for _t, vals in source]
            means[sid] = sum(values) / len(values) if values else 0.0
        return means

    def _response_metrics(self, species: list[str]) -> list[dict[str, Any]]:
        if not self._history:
            return []
        baselines = self._baseline_means(species)
        latest_t, latest_vals = self._history[-1]
        metrics: list[dict[str, Any]] = []
        for sid in species:
            baseline = float(baselines.get(sid, 0.0))
            final = float(latest_vals.get(sid, 0.0))
            trajectory = [float(vals.get(sid, 0.0)) for _t, vals in self._history]
            peak = max(trajectory, key=lambda value: abs(value - baseline)) if trajectory else final
            delta = final - baseline
            if abs(baseline) > 1e-12:
                percent = (delta / abs(baseline)) * 100.0
            else:
                percent = None
            metrics.append({
                "id": sid,
                "label": self._label_for(sid),
                "baseline": baseline,
                "final": final,
                "peak": peak,
                "delta": delta,
                "percent_change": percent,
                "direction": "increased" if delta > 0 else "decreased" if delta < 0 else "stayed near baseline",
            })
        metrics.sort(key=lambda item: abs(float(item["delta"])), reverse=True)
        return metrics

    def _normalized_series(self, species: list[str]) -> list[dict[str, Any]]:
        baselines = self._baseline_means(species)
        normalized = []
        for sid in species:
            baseline = float(baselines.get(sid, 0.0))
            points = []
            for t, vals in self._history:
                value = float(vals.get(sid, 0.0))
                if abs(baseline) > 1e-12:
                    plotted = ((value - baseline) / abs(baseline)) * 100.0
                else:
                    plotted = value - baseline
                points.append([t, plotted])
            normalized.append({"name": self._label_for(sid), "points": points})
        scenario = self._scenario()
        active_label = scenario.get("active_label")
        try:
            baseline_value = float(scenario.get("baseline_value"))
            challenge_value = float(scenario.get("challenge_value"))
            recovery_value = float(scenario.get("recovery_value", baseline_value))
            baseline_until = float(scenario.get("baseline_until"))
            challenge_until = float(scenario.get("challenge_until"))
        except (TypeError, ValueError):
            return normalized
        if active_label and self._history:
            denom = abs(baseline_value) if abs(baseline_value) > 1e-12 else 1.0
            input_points = []
            for t, _vals in self._history:
                if t < baseline_until - 1e-12:
                    raw = baseline_value
                elif t < challenge_until - 1e-12:
                    raw = challenge_value
                else:
                    raw = recovery_value
                input_points.append([t, ((raw - baseline_value) / denom) * 100.0])
            normalized.append({"name": f"Applied challenge: {active_label}", "points": input_points})
        return normalized

    def _summary_rows(self, t: float) -> list[list[str]]:
        question = self.lab_question or f"What changed in the {self.lab_title} run?"
        scenario = self._scenario()
        scenario_name = str(scenario.get("scenario_name") or "Baseline scenario")
        if not self._latest_state:
            return [
                ["What question did this run answer?", question],
                ["What challenge was applied?", scenario_name],
                ["What did the model emit?", "No state variables emitted yet."],
                ["How should this be interpreted?", f"The {self.lab_title} run did not yet provide a trajectory to summarize."],
            ]
        species = list(self._history[0][1].keys()) if self._history else list(self._latest_state.keys())
        metrics = self._response_metrics(species)
        top = metrics[0] if metrics else None
        if top is None:
            response_answer = "The selected outputs stayed near their baseline values under this scenario."
        elif abs(float(top["delta"])) <= 1e-12:
            response_answer = f"{top['label']} stayed near baseline; the selected outputs did not materially move under this scenario."
        else:
            pct = top.get("percent_change")
            pct_text = f" ({pct:.3g}% from baseline)" if isinstance(pct, float) else ""
            response_answer = f"{top['label']} {top['direction']} by {float(top['delta']):.3g}{pct_text}."
        active = scenario.get("active_label") or "scenario input"
        baseline_value = scenario.get("baseline_value")
        challenge_value = scenario.get("challenge_value")
        unit = scenario.get("unit") or ""
        return [
            ["What question did this run answer?", question],
            ["What challenge was applied?", f"{scenario_name}: {active} changed from {baseline_value} to {challenge_value} {unit}."],
            ["How much simulated time was evaluated?", f"{t:.3g} s across {len(self._history)} recorded time points"],
            ["Which variable responded most?", response_answer],
            ["How should this be interpreted?", "Treat this as a modelled physiological challenge, not a clinical prediction; inspect the absolute and baseline-relative plots together."],
        ]

    def visualize(self):
        if not self._history:
            return None
        species = list(self._history[0][1].keys())
        events = self._scenario_events()
        absolute_series = [
            {"name": self._label_for(sid),
              "points": [[t, vals.get(sid, 0.0)] for t, vals in self._history]}
            for sid in species
        ]
        normalized_series = self._normalized_series(species)
        metrics = self._response_metrics(species)
        bar_items = [
            {
                "label": item["label"],
                "value": float(item["delta"]),
                "unit": "native SBML units",
                "color": "#0f766e" if float(item["delta"]) >= 0 else "#dc2626",
            }
            for item in metrics[:8]
        ]
        latest_t, _latest_vals = self._history[-1]
        rows = self._summary_rows(latest_t)
        scenario = self._scenario()
        scenario_name = str(scenario.get("scenario_name") or "Physiological challenge")
        question = self.lab_question or "What changed in the simulated system?"
        qa_subtitle = (
            f"Answers `{question}` using {scenario_name.lower()} over a {latest_t:.3g}-second Tellurium run."
        )
        return [
            {
                "render": "timeseries",
                "description": "Absolute model state values in their native SBML scale, annotated with the scenario timing.",
                "data": {
                    "title": "What did the model simulate?",
                    "series": absolute_series,
                    "x_label": "Time (s)",
                    "y_label": "Native SBML value",
                    "events": events,
                    "reference_lines": [{"axis": "y", "value": 0, "label": "zero"}],
                    "value_mode": "absolute",
                },
            },
            {
                "render": "timeseries",
                "description": "Baseline-relative trajectories show which signals moved after the challenge instead of hiding small changes on an absolute scale.",
                "data": {
                    "title": "What changed after the challenge?",
                    "series": normalized_series,
                    "x_label": "Time (s)",
                    "y_label": "Change from baseline",
                    "y_unit": "% when baseline is nonzero; native delta otherwise",
                    "events": events,
                    "reference_lines": [{"axis": "y", "value": 0, "label": "baseline"}],
                    "value_mode": "percent_change",
                },
            },
            {
                "render": "bar",
                "description": "Signed final-minus-baseline changes rank the strongest responses in the selected model outputs.",
                "data": {
                    "title": "Which variables responded most?",
                    "items": bar_items,
                    "x_label": "Model variable",
                    "y_label": "Final minus baseline",
                    "y_unit": "native SBML units",
                },
            },
            {
                "render": "table",
                "description": f"Answers `{question}` for the {self.lab_title} run.",
                "data": {
                    "title": "What Happened",
                    "subtitle": qa_subtitle,
                    "columns": ["Question", "Answer"],
                    "rows": rows,
                },
            },
        ]
