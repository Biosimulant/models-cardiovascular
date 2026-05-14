# Cooling2007 Ip3 Transients Myocyte Lab

This lab asks: **Does inositol trisphosphate stimulation create a calcium transient?**

The lab is composed of two sub-models: a `core` SBML simulator (encoded as SBML, solved by Tellurium) and a dedicated `viz` presenter that turns the raw simulation state into a friendly timeseries plot and a plain-language "What Happened" summary. The split keeps the SBML wrapper clean and makes it easy to swap or extend the visualization without touching the simulator. This a model from the article: Modeling hypertrophic inositol trisphosphate transients in the cardiac myocyte. It can be used to explore cardiac dynamics and compare response patterns across conditions.

## What You'll See

The lab opens as a canvas with three model nodes wired in series: the scenario driver on the left, the core simulator in the middle, and the visualization sub-model on the right. After running, the viz node emits four visualizations: an event-annotated absolute timeseries, a baseline-relative response timeseries, a signed response bar chart, and a question-and-answer table titled `What Happened` that answers `Does inositol trisphosphate stimulation create a calcium transient?` in plain language. The viz node also publishes the table as a structured `run_summary` record that downstream nodes can consume.

**Primary variables shown:** the core publishes a curated state record for the visualization, and the viz node presents these concepts with user-friendly labels:

- Inactive G-protein state
- Active G-protein state
- Receptor pool
- Ligand-bound receptor
- Activated receptor complex
- Ligand-bound active receptor
- Phosphorylated receptor complex
- Inositol trisphosphate
- Calcium-bound receptor state
- Calcium-bound active receptor state
- Inactive receptor state
- Active receptor state
- Calcium

The first screenshot shows the canvas and results panel with the absolute state trajectories and baseline-relative calcium-initial challenge response. The second scrolls down to the ranked response chart and the `What Happened` Q&A table for the same run.

![Cooling2007 IP3 transients lab canvas with absolute and baseline-relative calcium response trajectories](assets/cooling2007-ip3-timeseries-results.png)

![Cooling2007 IP3 transients ranked response chart and What Happened summary table](assets/cooling2007-ip3-response-summary.png)

## How the Models Connect

The canvas has two steps:

1. `cooling2007_ip3_transients_myocyte_core`: SBML simulator. Receives every contextual input port (ion concentrations, voltages, conductances, etc. — see below), drives roadrunner, and emits two outputs: `state` (per-window species/state-variable record) and `species_labels` (a one-time map of `{species_id: human_label}` lifted from the SBML `<species name=...>` attributes).
2. `cooling2007_ip3_transients_myocyte_viz`: visualization sub-model. Consumes both `state` and `species_labels` from the core, accumulates the per-window history, prettifies the labels, and renders the two visuals plus the `run_summary` output. No SBML, no roadrunner — pure presentation.

## How to Read the Visualizations

The absolute timeseries plot has one curve per state variable in the SBML model and marks when the challenge and recovery windows begin. The baseline-relative plot rescales each curve against the pre-challenge baseline so small but real responses are visible. The x-axis is simulation time in seconds and the y-axis is the variable's value in its native SBML unit (concentrations in mM or mol, voltages in mV, currents in pA, volumes in mL — refer to the SBML file for the exact unit per variable). In the default screenshot, the calcium-initial challenge starts at 0.25 s, changes calcium initial from 0.1 to 0.2, and recovery starts at 0.75 s.

The response bar chart ranks final-minus-baseline changes in native SBML units. The "What Happened" table explains the lab question, the applied challenge, the simulated duration, the strongest response, and the interpretation limits. In the shown run, calcium-bound receptor state is the strongest final-minus-baseline responder, increasing by about 0.0752 native SBML units.

## What This Lab Contains

- `lab.yaml` declares the two sub-models, runtime, IO, and wiring.
- `wiring-layout.json` places the two nodes on the canvas with the connecting edges.
- `models/core/model.yaml` describes the SBML simulator package.
- `models/core/src/cooling2007_ip3transients_cardiacmyocyte_biomd0000000400_model.py` is the SBML wrapper (no visualization code).
- `models/core/data/BIOMD0000000400.xml` is the original SBML file from BioModels.
- `models/core/tests/` checks instantiation, output accumulation, and output keys.
- `models/viz/model.yaml` describes the visualization sub-model.
- `models/viz/src/cooling2007_ip3_transients_myocyte_viz.py` consumes core state + labels and renders timeseries, Q&A table, and the `run_summary` record.
- `models/viz/tests/` exercises the viz with synthetic state inputs (no SBML or roadrunner needed).

## Inputs

This lab exposes a set of **contextual scalar ports** specific to its SBML, plus three **generic fallback ports** for everything else.

### Contextual ports (recommended)

These map a human-friendly port name onto a real SBML global parameter. Wire them from upstream nodes or set them in `lab.yaml` `runtime.initial_inputs`. Each scalar override is applied to roadrunner before the next `advance_window` call.

| Input | Meaning | Default | Unit |
|---|---|---|---|
| `inositol_trisphosphate_initial` | Sets inositol trisphosphate initial for the scenario. | 0.015 | — |
| `calcium_initial` | Sets calcium initial for the scenario. | 0.1 | — |
| `receptor_initial` | Sets receptor initial for the scenario. | 13.9 | — |
### Generic fallback ports

- `integration_step` (`s`, scalar): override the ODE solver step. Smaller is more precise but slower. Default `0.001`.
- `parameter_overrides` (record, dict of `{parameter_id: value}`): apply override values to any SBML global parameter listed in the **SBML Parameters** table below — useful when you need to override a parameter that has no contextual port. Applied before each window.
- `initial_conditions` (record, dict of `{species_id: value}`): override the starting concentration of any species in the **SBML Species** table below. Applied at setup and on reset.

## Outputs

- `scenario_metadata` (from scenario): scenario name, active challenge input, baseline/challenge/recovery timing, and event markers used by the visualizations.
- `state` (from core): a record of every species and state variable in the SBML model at each communication step. Units are mixed; see the SBML file for per-species units.
- `run_summary` (from viz): structured Q&A record echoing the rows in the "What Happened" table — `{duration_s, point_count, state_variable_count, rows}`. Useful for downstream nodes that want to consume the same plain-language summary the user sees in the visualization.

## Running in Biosimulant Desktop

Import the lab source folder directly:

```bash
biosimulant labs import labs/cooling2007-ip3-transients-myocyte
```

Then open the imported lab and press Run. The results should include the state-variable timeseries and the `What Happened` Q&A table.

## Notes

- The bundled run uses a baseline plus challenge scenario so the first visualization shows a physiological perturbation without changing the upstream SBML equations.
- Default run length is `1` s with a `0.001` s communication step. These are conservative defaults chosen by category (single-cell electrophysiology vs whole-system circulation vs slow regulatory loop). Tune them in `lab.yaml`.
- Requires `tellurium==2.2.11.2`. The first import compiles the SBML to LLVM in-process.
- License: `CC0` (from upstream BioModels entry [biomodels_ebi:BIOMD0000000400](https://www.ebi.ac.uk/biomodels/BIOMD0000000400)).
- This wrapper does not modify the upstream biology. To change rates, initial conditions, or kinetic laws, edit the SBML file in `models/core/data/BIOMD0000000400.xml` directly.

### Advanced SBML Identifiers

<details>
<summary>Raw upstream identifiers for reproducibility and advanced overrides</summary>

#### SBML Parameters

Full list of global parameter IDs, for use with `parameter_overrides`. Defaults come from the upstream SBML.

| Parameter ID | Name | Default Value |
|---|---|---|
| `L` | L | _(unset)_ |
| `Ls` | Ls | 0.1 |
| `ts` | ts | 30 |
| `PIP2` | PIP2 | 4000 |
| `J1` | J1 | _(unset)_ |
| `kf1` | kf1 | 0.0003 |
| `kr1` | kr1 | _(unset)_ |
| `Kd1` | Kd1 | 3E-5 |
| `J2` | J2 | _(unset)_ |
| `kf2` | kf2 | 0.000275 |
| `kr2` | kr2 | _(unset)_ |
| `Kd2` | Kd2 | 27500 |
| `J3` | J3 | _(unset)_ |
| `kf3` | kf3 | 1 |
| `kr3` | kr3 | 0.001 |
| `J4` | J4 | _(unset)_ |
| `kf4` | kf4 | 0.3 |
| `kr4` | kr4 | _(unset)_ |
| `Kd4` | Kd4 | 3E-5 |
| `J5` | J5 | _(unset)_ |
| `kf5` | kf5 | 0.0004 |
| `J6` | J6 | _(unset)_ |
| `kf6` | kf6 | 1 |
| `J7` | J7 | _(unset)_ |
| `kf7` | kf7 | 0.15 |
| `J8` | J8 | _(unset)_ |
| `kf8` | kf8 | 0.0167 |
| `kr8` | kr8 | 0.0167 |
| `J9` | J9 | _(unset)_ |
| `kf9` | kf9 | 0.0042 |
| `kr9` | kr9 | 1 |
| `J10` | J10 | _(unset)_ |
| `kf10` | kf10 | 0.042 |
| `kr10` | kr10 | 1 |
| `J11` | J11 | _(unset)_ |
| `kf11` | kf11 | 0.0334 |
| `kr11` | kr11 | _(unset)_ |
| `Kd11` | Kd11 | 0.1 |
| `J12` | J12 | _(unset)_ |
| `kf12` | kf12 | 6 |
| `J13` | J13 | _(unset)_ |
| `kf13` | kf13 | 6 |
| `J14` | J14 | _(unset)_ |
| `kf14` | kf14 | 0.444 |
| `Km14` | Km14 | 19.8 |
| `J15` | J15 | _(unset)_ |
| `kf15` | kf15 | 3.8 |
| `Km15` | Km15 | 5 |
| `J16` | J16 | _(unset)_ |
| `kf16` | kf16 | 1.25 |
| _... 5 more, see SBML file_ | | |

#### SBML Species

Full list of species IDs, for use with `initial_conditions`.

| Species ID | Name | Initial Value |
|---|---|---|
| `Gd` | Gd | 10000 |
| `Gt` | Gt | 0 |
| `R` | R | 13.9 |
| `Rl` | Rl | 0 |
| `Rg` | Rg | 5.06 |
| `Rlg` | Rlg | 0 |
| `Rlgp` | Rlgp | 0 |
| `IP3` | IP3 | 0.015 |
| `Pc` | Pc | 9.09 |
| `Pcg` | Pcg | 0 |
| `P` | P | 90.9 |
| `Pg` | Pg | 0 |
| `Ca` | Ca | 0.1 |

</details>
