# Guyton1972 Capillary Dynamics Lab

This lab asks: **Does fluid move into or out of the capillaries?**

The lab is composed of two sub-models: a `core` SBML simulator (encoded as SBML, solved by Tellurium) and a dedicated `viz` presenter that turns the raw simulation state into a friendly timeseries plot and a plain-language "What Happened" summary. The split keeps the SBML wrapper clean and makes it easy to swap or extend the visualization without touching the simulator. This a model from the article: Circulation: overall regulation. It can be used to explore cardiac dynamics and compare response patterns across conditions.

## What You'll See

The lab opens as a canvas with three model nodes wired in series: the scenario driver on the left, the core simulator in the middle, and the visualization sub-model on the right. After running, the viz node emits four visualizations: an event-annotated absolute timeseries, a baseline-relative response timeseries, a signed response bar chart, and a question-and-answer table titled `What Happened` that answers `Does fluid move into or out of the capillaries?` in plain language. The viz node also publishes the table as a structured `run_summary` record that downstream nodes can consume.

**Primary variables shown:** the core publishes a curated state record for the visualization, and the viz node presents these concepts with user-friendly labels:

- Total capillary volume
- Plasma fluid volume
- Extracellular fluid volume
- Baseline filtration pressure

Screenshots will land in `assets/` once the first published run produces them.

## How the Models Connect

The canvas has two steps:

1. `guyton1972_capillary_dynamics_core`: SBML simulator. Receives every contextual input port (ion concentrations, voltages, conductances, etc. — see below), drives roadrunner, and emits two outputs: `state` (per-window species/state-variable record) and `species_labels` (a one-time map of `{species_id: human_label}` lifted from the SBML `<species name=...>` attributes).
2. `guyton1972_capillary_dynamics_viz`: visualization sub-model. Consumes both `state` and `species_labels` from the core, accumulates the per-window history, prettifies the labels, and renders the two visuals plus the `run_summary` output. No SBML, no roadrunner — pure presentation.

## How to Read the Visualizations

The absolute timeseries plot has one curve per state variable in the SBML model and marks when the challenge and recovery windows begin. The baseline-relative plot rescales each curve against the pre-challenge baseline so small but real responses are visible. The x-axis is simulation time in seconds and the y-axis is the variable's value in its native SBML unit (concentrations in mM or mol, voltages in mV, currents in pA, volumes in mL — refer to the SBML file for the exact unit per variable). Look for periodic patterns (action-potential-style depolarisations, oscillations), monotonic trends, or steady-state plateaus.

The response bar chart ranks final-minus-baseline changes in native SBML units. The "What Happened" table explains the lab question, the applied challenge, the simulated duration, the strongest response, and the interpretation limits.

## What This Lab Contains

- `lab.yaml` declares the two sub-models, runtime, IO, and wiring.
- `wiring-layout.json` places the two nodes on the canvas with the connecting edges.
- `models/core/model.yaml` describes the SBML simulator package.
- `models/core/src/guyton1972_capillarydynamics_model0912160000_model.py` is the SBML wrapper (no visualization code).
- `models/core/data/MODEL0912160000.xml` is the original SBML file from BioModels.
- `models/core/tests/` checks instantiation, output accumulation, and output keys.
- `models/viz/model.yaml` describes the visualization sub-model.
- `models/viz/src/guyton1972_capillary_dynamics_viz.py` consumes core state + labels and renders timeseries, Q&A table, and the `run_summary` record.
- `models/viz/tests/` exercises the viz with synthetic state inputs (no SBML or roadrunner needed).

## Inputs

This lab exposes a set of **contextual scalar ports** specific to its SBML, plus three **generic fallback ports** for everything else.

### Contextual ports (recommended)

These map a human-friendly port name onto a real SBML global parameter. Wire them from upstream nodes or set them in `lab.yaml` `runtime.initial_inputs`. Each scalar override is applied to roadrunner before the next `advance_window` call.

| Input | Meaning | Default | Unit |
|---|---|---|---|
| `capillary_pressure` | Sets capillary pressure for the scenario. | 16.9144 | — |
| `filtration_coefficient` | Sets filtration coefficient for the scenario. | -4.078e-07 | — |
### Generic fallback ports

- `integration_step` (`s`, scalar): override the ODE solver step. Smaller is more precise but slower. Default `1`.
- `parameter_overrides` (record, dict of `{parameter_id: value}`): apply override values to any SBML global parameter listed in the **SBML Parameters** table below — useful when you need to override a parameter that has no contextual port. Applied before each window.
- `initial_conditions` (record, dict of `{species_id: value}`): override the starting concentration of any species in the **SBML Species** table below. Applied at setup and on reset.

## Outputs

- `scenario_metadata` (from scenario): scenario name, active challenge input, baseline/challenge/recovery timing, and event markers used by the visualizations.
- `state` (from core): a record of every species and state variable in the SBML model at each communication step. Units are mixed; see the SBML file for per-species units.
- `run_summary` (from viz): structured Q&A record echoing the rows in the "What Happened" table — `{duration_s, point_count, state_variable_count, rows}`. Useful for downstream nodes that want to consume the same plain-language summary the user sees in the visualization.

## Running in Biosimulant Desktop

Import the lab source folder directly:

```bash
biosimulant labs import labs/guyton1972-capillary-dynamics
```

Then open the imported lab and press Run. The results should include the state-variable timeseries and the `What Happened` Q&A table.

## Notes

- The bundled run uses a baseline plus challenge scenario so the first visualization shows a physiological perturbation without changing the upstream SBML equations.
- Default run length is `600` s with a `1` s communication step. These are conservative defaults chosen by category (single-cell electrophysiology vs whole-system circulation vs slow regulatory loop). Tune them in `lab.yaml`.
- Requires `tellurium==2.2.11.2`. The first import compiles the SBML to LLVM in-process.
- License: `CC0` (from upstream BioModels entry [biomodels_ebi:MODEL0912160000](https://www.ebi.ac.uk/biomodels/MODEL0912160000)).
- This wrapper does not modify the upstream biology. To change rates, initial conditions, or kinetic laws, edit the SBML file in `models/core/data/MODEL0912160000.xml` directly.

### Advanced SBML Identifiers

<details>
<summary>Raw upstream identifiers for reproducibility and advanced overrides</summary>

#### SBML Parameters

Full list of global parameter IDs, for use with `parameter_overrides`. Defaults come from the upstream SBML.

| Parameter ID | Name | Default Value |
|---|---|---|
| `VEC` | VEC | 14.8548 |
| `PPD` | PPD | 4.4805e-06 |
| `RVS` | RVS | 2.77751 |
| `DFP` | DFP | -4.078e-07 |
| `VPF` | VPF | 0.0123238 |
| `BFN` | BFN | 2.79521 |
| `PVS` | PVS | 3.71612 |
| `PC` | PC | 16.9144 |
| `VTC` | VTC | _(unset)_ |
| `VP` | VP | 3.00449 |
| `VPD` | VPD | _(unset)_ |
| `CPP` | CPP | _(unset)_ |
| `DLP` | DLP | _(unset)_ |
| `CPPD` | CPPD | _(unset)_ |
| `VTCPL` | VTCPL | _(unset)_ |
| `PRCD` | PRCD | _(unset)_ |
| `DPC` | DPC | _(unset)_ |
| `PRP` | PRP | 216.243 |
| `DPP` | DPP | _(unset)_ |
| `PPC` | PPC | _(unset)_ |
| `VTS` | VTS | _(unset)_ |
| `VTS1` | VTS1 | _(unset)_ |
| `VTS2` | VTS2 | 0 |
| `TSP` | TSP | 279.945 |
| `DPI` | DPI | _(unset)_ |
| `CPI` | CPI | _(unset)_ |
| `PTCPR` | PTCPR | _(unset)_ |
| `DPL` | DPL | _(unset)_ |
| `CHY` | CHY | _(unset)_ |
| `PGH` | PGH | _(unset)_ |
| `POSHYL` | POSHYL | _(unset)_ |
| `PTC` | PTC | _(unset)_ |
| `PTT` | PTT | _(unset)_ |
| `PIF` | PIF | _(unset)_ |
| `PTS` | PTS | _(unset)_ |
| `VTL` | VTL | _(unset)_ |
| `PLD1` | PLD1 | _(unset)_ |
| `PLD` | PLD | _(unset)_ |
| `VG` | VG | _(unset)_ |
| `VIF` | VIF | _(unset)_ |
| `CFC` | CFC | 0.01167 |
| `TRPL` | TRPL | 0 |
| `CPR` | CPR | 40 |
| `LPDE` | LPDE | 8 |
| `PCE` | PCE | 1 |
| `PCR` | PCR | 15 |
| `LPK` | LPK | 2.728e-14 |
| `LPPR` | LPPR | 0.03 |
| `CPK` | CPK | 0.000253 |
| `TSSLML` | TSSLML | 0.15 |
| _... 7 more, see SBML file_ | | |

#### SBML Species

Full list of species IDs, for use with `initial_conditions`.

_No species declared in this SBML file._

</details>
