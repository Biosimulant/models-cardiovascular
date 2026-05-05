# Niederer2006 Myocyte Relaxation Lab

This lab asks: **How quickly does the myocyte relax after calcium activation?**

The lab is composed of two sub-models: a `core` SBML simulator (encoded as SBML, solved by Tellurium) and a dedicated `viz` presenter that turns the raw simulation state into a friendly timeseries plot and a plain-language "What Happened" summary. The split keeps the SBML wrapper clean and makes it easy to swap or extend the visualization without touching the simulator. This a model from the article: A quantitative analysis of cardiac myocyte relaxation: a simulation study. It can be used to explore cardiac dynamics and compare response patterns across conditions.

## What You'll See

The lab opens as a canvas with three model nodes wired in series: the scenario driver on the left, the core simulator in the middle, and the visualization sub-model on the right. After running, the viz node emits four visualizations: an event-annotated absolute timeseries, a baseline-relative response timeseries, a signed response bar chart, and a question-and-answer table titled `What Happened` that answers `How quickly does the myocyte relax after calcium activation?` in plain language. The viz node also publishes the table as a structured `run_summary` record that downstream nodes can consume.

**Primary variables shown:** the core publishes a curated state record for the visualization, and the viz node presents these concepts with user-friendly labels:

- Cytosolic calcium
- Bound calcium
- Troponin calcium-binding pool
- Z

Screenshots will land in `assets/` once the first published run produces them.

## How the Models Connect

The canvas has two steps:

1. `niederer2006_myocyte_relaxation_core`: SBML simulator. Receives every contextual input port (ion concentrations, voltages, conductances, etc. — see below), drives roadrunner, and emits two outputs: `state` (per-window species/state-variable record) and `species_labels` (a one-time map of `{species_id: human_label}` lifted from the SBML `<species name=...>` attributes).
2. `niederer2006_myocyte_relaxation_viz`: visualization sub-model. Consumes both `state` and `species_labels` from the core, accumulates the per-window history, prettifies the labels, and renders the two visuals plus the `run_summary` output. No SBML, no roadrunner — pure presentation.

## How to Read the Visualizations

The absolute timeseries plot has one curve per state variable in the SBML model and marks when the challenge and recovery windows begin. The baseline-relative plot rescales each curve against the pre-challenge baseline so small but real responses are visible. The x-axis is simulation time in seconds and the y-axis is the variable's value in its native SBML unit (concentrations in mM or mol, voltages in mV, currents in pA, volumes in mL — refer to the SBML file for the exact unit per variable). Look for periodic patterns (action-potential-style depolarisations, oscillations), monotonic trends, or steady-state plateaus.

The response bar chart ranks final-minus-baseline changes in native SBML units. The "What Happened" table explains the lab question, the applied challenge, the simulated duration, the strongest response, and the interpretation limits.

## What This Lab Contains

- `lab.yaml` declares the two sub-models, runtime, IO, and wiring.
- `wiring-layout.json` places the two nodes on the canvas with the connecting edges.
- `models/core/model.yaml` describes the SBML simulator package.
- `models/core/src/niederer2006_cardiacmyocyterelaxation_model8687196544_model.py` is the SBML wrapper (no visualization code).
- `models/core/data/MODEL8687196544.xml` is the original SBML file from BioModels.
- `models/core/tests/` checks instantiation, output accumulation, and output keys.
- `models/viz/model.yaml` describes the visualization sub-model.
- `models/viz/src/niederer2006_myocyte_relaxation_viz.py` consumes core state + labels and renders timeseries, Q&A table, and the `run_summary` record.
- `models/viz/tests/` exercises the viz with synthetic state inputs (no SBML or roadrunner needed).

## Inputs

This lab exposes a set of **contextual scalar ports** specific to its SBML, plus three **generic fallback ports** for everything else.

### Contextual ports (recommended)

These map a human-friendly port name onto a real SBML global parameter. Wire them from upstream nodes or set them in `lab.yaml` `runtime.initial_inputs`. Each scalar override is applied to roadrunner before the next `advance_window` call.

| Input | Meaning | Default | Unit |
|---|---|---|---|
| `troponin_pool` | Sets troponin pool for the scenario. | 0.067593139865 | — |
| `relaxation_rate` | Sets relaxation rate for the scenario. | 0.002 | — |
| `cooperativity` | Sets cooperativity for the scenario. | 0.008 | — |
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
biosimulant labs import labs/niederer2006-myocyte-relaxation
```

Then open the imported lab and press Run. The results should include the state-variable timeseries and the `What Happened` Q&A table.

## Notes

- The bundled run uses a baseline plus challenge scenario so the first visualization shows a physiological perturbation without changing the upstream SBML equations.
- Default run length is `1` s with a `0.001` s communication step. These are conservative defaults chosen by category (single-cell electrophysiology vs whole-system circulation vs slow regulatory loop). Tune them in `lab.yaml`.
- Requires `tellurium==2.2.11.2`. The first import compiles the SBML to LLVM in-process.
- License: `CC0` (from upstream BioModels entry [biomodels_ebi:MODEL8687196544](https://www.ebi.ac.uk/biomodels/MODEL8687196544)).
- This wrapper does not modify the upstream biology. To change rates, initial conditions, or kinetic laws, edit the SBML file in `models/core/data/MODEL8687196544.xml` directly.

### Advanced SBML Identifiers

<details>
<summary>Raw upstream identifiers for reproducibility and advanced overrides</summary>

#### SBML Parameters

Full list of global parameter IDs, for use with `parameter_overrides`. Defaults come from the upstream SBML.

| Parameter ID | Name | Default Value |
|---|---|---|
| `Ca_i` | Ca_i | _(unset)_ |
| `Ca_b` | Ca_b | _(unset)_ |
| `TRPN` | TRPN | 0.067593139865 |
| `z` | z | 0.014417937837 |
| `z_max` | z_max | _(unset)_ |
| `alpha_0` | alpha_0 | 0.008 |
| `alpha_r1` | alpha_r1 | 0.002 |
| `alpha_r2` | alpha_r2 | 0.00175 |
| `n_Rel` | n_Rel | 3 |
| `K_z` | K_z | 0.15 |
| `n_Hill` | n_Hill | 3 |
| `Ca_50ref` | Ca_50ref | 0.00105 |
| `z_p` | z_p | 0.85 |
| `beta_1` | beta_1 | -4 |
| `Ca_50` | Ca_50 | _(unset)_ |
| `Ca_TRPN_50` | Ca_TRPN_50 | _(unset)_ |
| `K_2` | K_2 | _(unset)_ |
| `K_1` | K_1 | _(unset)_ |
| `alpha_Tm` | alpha_Tm | _(unset)_ |
| `beta_Tm` | beta_Tm | _(unset)_ |
| `J_TRPN` | J_TRPN | _(unset)_ |
| `Ca_TRPN_Max` | Ca_TRPN_Max | 0.07 |
| `k_off` | k_off | _(unset)_ |
| `k_on` | k_on | 100 |
| `k_Ref_off` | k_Ref_off | 0.2 |
| `gamma_trpn` | gamma_trpn | 2 |
| `lambda` | lambda | _(unset)_ |
| `ExtensionRatio` | ExtensionRatio | _(unset)_ |
| `dExtensionRatiodt` | dExtensionRatiodt | _(unset)_ |
| `lambda_prev` | lambda_prev | _(unset)_ |
| `overlap` | overlap | _(unset)_ |
| `beta_0` | beta_0 | 4.9 |
| `T_ref` | T_ref | 56.2 |
| `T_Base` | T_Base | _(unset)_ |
| `T_0` | T_0 | _(unset)_ |
| `Q` | Q | _(unset)_ |
| `a` | a | 0.35 |
| `Q_1` | Q_1 | 0 |
| `Q_2` | Q_2 | 0 |
| `Q_3` | Q_3 | 0 |
| `A_1` | A_1 | -29 |
| `A_2` | A_2 | 138 |
| `A_3` | A_3 | 129 |
| `alpha_1` | alpha_1 | 0.03 |
| `alpha_2` | alpha_2 | 0.13 |
| `alpha_3` | alpha_3 | 0.625 |
| `Tension` | Tension | _(unset)_ |

#### SBML Species

Full list of species IDs, for use with `initial_conditions`.

_No species declared in this SBML file._

</details>
