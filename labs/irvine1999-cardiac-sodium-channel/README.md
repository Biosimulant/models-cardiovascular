# Irvine1999 Cardiac Sodium Channel Lab

This lab asks: **How does the cardiac sodium channel recover and inactivate?**

The lab is composed of two sub-models: a `core` SBML simulator (encoded as SBML, solved by Tellurium) and a dedicated `viz` presenter that turns the raw simulation state into a friendly timeseries plot and a plain-language "What Happened" summary. The split keeps the SBML wrapper clean and makes it easy to swap or extend the visualization without touching the simulator. This a model from the article: Cardiac sodium channel Markov model with temperature dependence and recoveryfrom inactivation. It can be used to explore cardiac dynamics and compare response patterns across conditions.

## What You'll See

The lab opens as a canvas with three model nodes wired in series: the scenario driver on the left, the core simulator in the middle, and the visualization sub-model on the right. After running, the viz node emits four visualizations: an event-annotated absolute timeseries, a baseline-relative response timeseries, a signed response bar chart, and a question-and-answer table titled `What Happened` that answers `How does the cardiac sodium channel recover and inactivate?` in plain language. The viz node also publishes the table as a structured `run_summary` record that downstream nodes can consume.

**Primary variables shown:** the core publishes a curated state record for the visualization, and the viz node presents these concepts with user-friendly labels:

- Open sodium-channel state 1
- Oxygen
- Closed sodium-channel state 0
- Closed sodium-channel state 1
- Closed sodium-channel state 2
- Closed sodium-channel state 3
- Closed sodium-channel state 4
- Inactivated sodium-channel state
- Open-channel probability

The captured run applies the configured voltage-step channel challenge, changing holding voltage from `-0.12` to `-0.02` during the challenge window before returning to baseline. It evaluates 1 s of simulated dynamics across Open sodium-channel state 1, Oxygen, Closed sodium-channel state 0, Closed sodium-channel state 1, and 5 other tracked variables; read the absolute trajectories, baseline-relative plot, response ranking, and summary table together because the variables use different native scales.

<!-- BIOSIMULANT_VISUALS_START -->
### Output Visualizations

The first chart shows the absolute model state trajectories in their native units with the challenge timing included.

![What did the model simulate?](assets/01-what-did-the-model-simulate.png)

The second chart normalizes each trajectory against its baseline so smaller relative shifts are visible beside larger state variables.

![What changed after the challenge?](assets/02-what-changed-after-the-challenge.png)

The response ranking summarizes final-minus-baseline changes and highlights which selected variables moved most during the configured run.

![Which variables responded most?](assets/03-which-variables-responded-most.png)

The summary table restates the lab question, challenge, simulated duration, strongest response, and interpretation limits in plain language.

![What Happened](assets/04-what-happened.png)

<!-- BIOSIMULANT_VISUALS_END -->

## How the Models Connect

The canvas has two steps:

1. `irvine1999_cardiac_sodium_channel_core`: SBML simulator. Receives every contextual input port (ion concentrations, voltages, conductances, etc. — see below), drives roadrunner, and emits two outputs: `state` (per-window species/state-variable record) and `species_labels` (a one-time map of `{species_id: human_label}` lifted from the SBML `<species name=...>` attributes).
2. `irvine1999_cardiac_sodium_channel_viz`: visualization sub-model. Consumes both `state` and `species_labels` from the core, accumulates the per-window history, prettifies the labels, and renders the two visuals plus the `run_summary` output. No SBML, no roadrunner — pure presentation.

## How to Read the Visualizations

The absolute timeseries plot has one curve per state variable in the SBML model and marks when the challenge and recovery windows begin. The baseline-relative plot rescales each curve against the pre-challenge baseline so small but real responses are visible. The x-axis is simulation time in seconds and the y-axis is the variable's value in its native SBML unit (concentrations in mM or mol, voltages in mV, currents in pA, volumes in mL — refer to the SBML file for the exact unit per variable). Look for periodic patterns (action-potential-style depolarisations, oscillations), monotonic trends, or steady-state plateaus.

The response bar chart ranks final-minus-baseline changes in native SBML units. The "What Happened" table explains the lab question, the applied challenge, the simulated duration, the strongest response, and the interpretation limits.

## What This Lab Contains

- `lab.yaml` declares the two sub-models, runtime, IO, and wiring.
- `wiring-layout.json` places the two nodes on the canvas with the connecting edges.
- `models/core/model.yaml` describes the SBML simulator package.
- `models/core/src/irvine1999_cardiacsodiumchannel_model0848062679_model.py` is the SBML wrapper (no visualization code).
- `models/core/data/MODEL0848062679.xml` is the original SBML file from BioModels.
- `models/core/tests/` checks instantiation, output accumulation, and output keys.
- `models/viz/model.yaml` describes the visualization sub-model.
- `models/viz/src/irvine1999_cardiac_sodium_channel_viz.py` consumes core state + labels and renders timeseries, Q&A table, and the `run_summary` record.
- `models/viz/tests/` exercises the viz with synthetic state inputs (no SBML or roadrunner needed).

## Inputs

This lab exposes a set of **contextual scalar ports** specific to its SBML, plus three **generic fallback ports** for everything else.

### Contextual ports (recommended)

These map a human-friendly port name onto a real SBML global parameter. Wire them from upstream nodes or set them in `lab.yaml` `runtime.initial_inputs`. Each scalar override is applied to roadrunner before the next `advance_window` call.

| Input | Meaning | Default | Unit |
|---|---|---|---|
| `holding_voltage` | Sets holding voltage for the scenario. | -0.12 | mV |
| `sodium_reversal_voltage` | Sets sodium reversal voltage for the scenario. | 0.044675 | mV |
| `sodium_conductance` | Sets sodium conductance for the scenario. | 0.0131 | mS_per_uF |
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
biosimulant labs import labs/irvine1999-cardiac-sodium-channel
```

Then open the imported lab and press Run. The results should include the state-variable timeseries and the `What Happened` Q&A table.

## Notes

- The bundled run uses a baseline plus challenge scenario so the first visualization shows a physiological perturbation without changing the upstream SBML equations.
- Default run length is `1` s with a `0.001` s communication step. These are conservative defaults chosen by category (single-cell electrophysiology vs whole-system circulation vs slow regulatory loop). Tune them in `lab.yaml`.
- Requires `tellurium==2.2.11.2`. The first import compiles the SBML to LLVM in-process.
- License: `CC0` (from upstream BioModels entry [biomodels_ebi:MODEL0848062679](https://www.ebi.ac.uk/biomodels/MODEL0848062679)).
- This wrapper does not modify the upstream biology. To change rates, initial conditions, or kinetic laws, edit the SBML file in `models/core/data/MODEL0848062679.xml` directly.

### Advanced SBML Identifiers

<details>
<summary>Raw upstream identifiers for reproducibility and advanced overrides</summary>

#### SBML Parameters

Full list of global parameter IDs, for use with `parameter_overrides`. Defaults come from the upstream SBML.

| Parameter ID | Name | Default Value |
|---|---|---|
| `V` | V | -0.12 |
| `i_Na` | i_Na | _(unset)_ |
| `E_Na` | E_Na | 0.044675 |
| `g_Na` | g_Na | 0.0131 |
| `P_open` | P_open | _(unset)_ |
| `O1` | O1 | 0 |
| `O2` | O2 | 0 |
| `C0` | C0 | 1 |
| `C1` | C1 | 0 |
| `C2` | C2 | 0 |
| `C3` | C3 | 0 |
| `C4` | C4 | 0 |
| `C0I` | C0I | 0 |
| `C1I` | C1I | 0 |
| `C2I` | C2I | 0 |
| `C3I` | C3I | 0 |
| `C4I` | C4I | 0 |
| `I` | I | 0 |
| `a` | a | 2.5218 |
| `alpha` | alpha | _(unset)_ |
| `beta` | beta | _(unset)_ |
| `cf` | cf | _(unset)_ |
| `cn` | cn | _(unset)_ |
| `of` | of | _(unset)_ |
| `on` | on | _(unset)_ |
| `eta` | eta | _(unset)_ |
| `gamma` | gamma | _(unset)_ |
| `delta` | delta | _(unset)_ |
| `epsilon` | epsilon | _(unset)_ |
| `omega` | omega | _(unset)_ |
| `v` | v | _(unset)_ |
| `gamma_gamma` | gamma_gamma | _(unset)_ |
| `delta_delta` | delta_delta | _(unset)_ |
| `R` | R | 8.314472 |
| `T` | T | 286 |
| `F` | F | 96500 |
| `k` | k | 1.3806504e-23 |
| `h` | h | 6.62607095e-31 |
| `z_alpha` | z_alpha | 0 |
| `z_beta` | z_beta | -0.9701 |
| `z_gamma` | z_gamma | 1.5703 |
| `z_delta` | z_delta | -1.3266 |
| `z_on` | z_on | 0.6625 |
| `z_of` | z_of | 0 |
| `z_gamma_gamma` | z_gamma_gamma | 0 |
| `z_delta_delta` | z_delta_delta | -3.5596 |
| `z_epsilon` | z_epsilon | 0 |
| `z_omega` | z_omega | 0 |
| `z_eta` | z_eta | 1.5717 |
| `z_v` | z_v | -1.3281 |
| _... 30 more, see SBML file_ | | |

#### SBML Species

Full list of species IDs, for use with `initial_conditions`.

_No species declared in this SBML file._

</details>
