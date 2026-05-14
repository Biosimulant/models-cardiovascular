# Clancy2001 Potassium Channel Lab

This lab asks: **How does the delayed rectifier potassium channel state distribution respond to voltage?**

The lab is composed of two sub-models: a `core` SBML simulator (encoded as SBML, solved by Tellurium) and a dedicated `viz` presenter that turns the raw simulation state into a friendly timeseries plot and a plain-language "What Happened" summary. The split keeps the SBML wrapper clean and makes it easy to swap or extend the visualization without touching the simulator. This model is according to the paper Cellular consequences of HEGR mutations in the long QT syndrome: precursors to sudden cardiac death. The author used Markovian model of cardiac Ikr in the paper.

## What You'll See

The lab opens as a canvas with three model nodes wired in series: the scenario driver on the left, the core simulator in the middle, and the visualization sub-model on the right. After running, the viz node emits four visualizations: an event-annotated absolute timeseries, a baseline-relative response timeseries, a signed response bar chart, and a question-and-answer table titled `What Happened` that answers `How does the delayed rectifier potassium channel state distribution respond to voltage?` in plain language. The viz node also publishes the table as a structured `run_summary` record that downstream nodes can consume.

**Primary variables shown:** the core publishes a curated state record for the visualization, and the viz node presents these concepts with user-friendly labels:

- Closed potassium-channel state 3
- Closed potassium-channel state 2
- Closed potassium-channel state 1
- Open potassium-channel state
- Inactivated potassium-channel state
- Cardiac delayed rectifier potassium current

The first screenshot shows the canvas and results panel with the absolute channel-state trajectories and baseline-relative voltage-step response. The second scrolls down to the ranked response chart and the `What Happened` Q&A table for the same holding-voltage challenge run.

![Clancy2001 potassium channel lab canvas with absolute and baseline-relative voltage-step trajectories](assets/clancy2001-potassium-timeseries-results.png)

![Clancy2001 potassium channel ranked response chart and What Happened summary table](assets/clancy2001-potassium-response-summary.png)

## How the Models Connect

The canvas has two steps:

1. `clancy2001_potassium_channel_core`: SBML simulator. Receives every contextual input port (ion concentrations, voltages, conductances, etc. — see below), drives roadrunner, and emits two outputs: `state` (per-window species/state-variable record) and `species_labels` (a one-time map of `{species_id: human_label}` lifted from the SBML `<species name=...>` attributes).
2. `clancy2001_potassium_channel_viz`: visualization sub-model. Consumes both `state` and `species_labels` from the core, accumulates the per-window history, prettifies the labels, and renders the two visuals plus the `run_summary` output. No SBML, no roadrunner — pure presentation.

## How to Read the Visualizations

The absolute timeseries plot has one curve per state variable in the SBML model and marks when the challenge and recovery windows begin. The baseline-relative plot rescales each curve against the pre-challenge baseline so small but real responses are visible. The x-axis is simulation time in seconds and the y-axis is the variable's value in its native SBML unit (concentrations in mM or mol, voltages in mV, currents in pA, volumes in mL — refer to the SBML file for the exact unit per variable). In the default screenshot, the holding-voltage challenge starts at 0.25 s, moves from -40 mV to -60 mV, and recovery starts at 0.75 s.

The response bar chart ranks final-minus-baseline changes in native SBML units. The "What Happened" table explains the lab question, the applied challenge, the simulated duration, the strongest response, and the interpretation limits. In the shown run, the cardiac delayed rectifier potassium current is the strongest final-minus-baseline responder, decreasing by about 0.0304 native SBML units, with the open potassium-channel state also decreasing.

## What This Lab Contains

- `lab.yaml` declares the two sub-models, runtime, IO, and wiring.
- `wiring-layout.json` places the two nodes on the canvas with the connecting edges.
- `models/core/model.yaml` describes the SBML simulator package.
- `models/core/src/clancy2001_kchannel_biomd0000000121_model.py` is the SBML wrapper (no visualization code).
- `models/core/data/BIOMD0000000121.xml` is the original SBML file from BioModels.
- `models/core/tests/` checks instantiation, output accumulation, and output keys.
- `models/viz/model.yaml` describes the visualization sub-model.
- `models/viz/src/clancy2001_potassium_channel_viz.py` consumes core state + labels and renders timeseries, Q&A table, and the `run_summary` record.
- `models/viz/tests/` exercises the viz with synthetic state inputs (no SBML or roadrunner needed).

## Inputs

This lab exposes a set of **contextual scalar ports** specific to its SBML, plus three **generic fallback ports** for everything else.

### Contextual ports (recommended)

These map a human-friendly port name onto a real SBML global parameter. Wire them from upstream nodes or set them in `lab.yaml` `runtime.initial_inputs`. Each scalar override is applied to roadrunner before the next `advance_window` call.

| Input | Meaning | Default | Unit |
|---|---|---|---|
| `temperature` | Sets temperature for the scenario. | 310 | — |
| `extracellular_potassium` | Sets extracellular potassium for the scenario. | 5.4 | mM |
| `intracellular_potassium` | Sets intracellular potassium for the scenario. | 140 | mM |
| `holding_voltage` | Sets holding voltage for the scenario. | -40 | mV |
| `test_voltage` | Sets test voltage for the scenario. | 0 | mV |
### Generic fallback ports

- `integration_step` (`s`, scalar): override the ODE solver step. Smaller is more precise but slower. Default `0.01`.
- `parameter_overrides` (record, dict of `{parameter_id: value}`): apply override values to any SBML global parameter listed in the **SBML Parameters** table below — useful when you need to override a parameter that has no contextual port. Applied before each window.
- `initial_conditions` (record, dict of `{species_id: value}`): override the starting concentration of any species in the **SBML Species** table below. Applied at setup and on reset.

## Outputs

- `scenario_metadata` (from scenario): scenario name, active challenge input, baseline/challenge/recovery timing, and event markers used by the visualizations.
- `state` (from core): a record of every species and state variable in the SBML model at each communication step. Units are mixed; see the SBML file for per-species units.
- `run_summary` (from viz): structured Q&A record echoing the rows in the "What Happened" table — `{duration_s, point_count, state_variable_count, rows}`. Useful for downstream nodes that want to consume the same plain-language summary the user sees in the visualization.

## Running in Biosimulant Desktop

Import the lab source folder directly:

```bash
biosimulant labs import labs/clancy2001-potassium-channel
```

Then open the imported lab and press Run. The results should include the state-variable timeseries and the `What Happened` Q&A table.

## Notes

- The bundled run uses a baseline plus challenge scenario so the first visualization shows a physiological perturbation without changing the upstream SBML equations.
- Default run length is `1` s with a `0.01` s communication step. These are conservative defaults chosen by category (single-cell electrophysiology vs whole-system circulation vs slow regulatory loop). Tune them in `lab.yaml`.
- Requires `tellurium==2.2.11.2`. The first import compiles the SBML to LLVM in-process.
- License: `CC0` (from upstream BioModels entry [biomodels_ebi:BIOMD0000000121](https://www.ebi.ac.uk/biomodels/BIOMD0000000121)).
- This wrapper does not modify the upstream biology. To change rates, initial conditions, or kinetic laws, edit the SBML file in `models/core/data/BIOMD0000000121.xml` directly.

### Advanced SBML Identifiers

<details>
<summary>Raw upstream identifiers for reproducibility and advanced overrides</summary>

#### SBML Parameters

Full list of global parameter IDs, for use with `parameter_overrides`. Defaults come from the upstream SBML.

| Parameter ID | Name | Default Value |
|---|---|---|
| `R` | gas constant | 8.314 |
| `F` | Faraday constant | 96.485 |
| `Temp` | temperature | 310 |
| `ko` | extracellular K | 5.4 |
| `ki` | introcellular K | 140 |
| `vhold` | holding_potential | -40 |
| `vtest` | test_potential | 0 |
| `vk` | reversal potential for k | _(unset)_ |
| `Gk` | membrane_conductance | _(unset)_ |
| `a` | — | _(unset)_ |
| `b` | — | _(unset)_ |
| `ain` | — | 2.172 |
| `bin` | — | 1.077 |
| `aa` | — | _(unset)_ |
| `bb` | — | _(unset)_ |
| `ai` | — | _(unset)_ |
| `bi` | — | _(unset)_ |
| `u` | — | _(unset)_ |
| `v` | membrane_potential | -40 |

#### SBML Species

Full list of species IDs, for use with `initial_conditions`.

| Species ID | Name | Initial Value |
|---|---|---|
| `c3` | ClosedState_3 | 1 |
| `c2` | ClosedState_2 | 0 |
| `c1` | ClosedState_1 | 0 |
| `o` | OpenState | 0.06 |
| `i` | InactivationState | 0 |
| `ik` | cardiac delayed rectifier current | 0.1 |

</details>
