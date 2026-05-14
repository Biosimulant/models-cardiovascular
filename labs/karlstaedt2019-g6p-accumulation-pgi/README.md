# Karlstaedt2019 G6p Accumulation Pgi Lab

This lab asks: **Does phosphoglucose isomerase inhibition accumulate glucose-6-phosphate?**

The lab is composed of two sub-models: a `core` SBML simulator (encoded as SBML, solved by Tellurium) and a dedicated `viz` presenter that turns the raw simulation state into a friendly timeseries plot and a plain-language "What Happened" summary. The split keeps the SBML wrapper clean and makes it easy to swap or extend the visualization without touching the simulator. This model is described in the article: Glucose 6-phosphate accumulates via phosphoglucose isomerase inhibition in heart muscle. Karlstaedt, A and Khanna, R and Thangam, M and Taegtmeyer, H Circulatio.

## What You'll See

The lab opens as a canvas with three model nodes wired in series: the scenario driver on the left, the core simulator in the middle, and the visualization sub-model on the right. After running, the viz node emits four visualizations: an event-annotated absolute timeseries, a baseline-relative response timeseries, a signed response bar chart, and a question-and-answer table titled `What Happened` that answers `Does phosphoglucose isomerase inhibition accumulate glucose-6-phosphate?` in plain language. The viz node also publishes the table as a structured `run_summary` record that downstream nodes can consume.

**Primary variables shown:** the core publishes a curated state record for the visualization, and the viz node presents these concepts with user-friendly labels:

- Extracellular glucose
- Intracellular glucose
- Cellular energy pool
- Glucose 6-phosphate
- Spent energy pool
- Fructose 6-phosphate
- Fructose 1,6-bisphosphate
- Low-energy nucleotide pool
- Fructose 2,6-bisphosphate
- Dihydroxyacetone phosphate
- Glyceraldehyde 3-phosphate
- Oxidized nicotinamide adenine dinucleotide
- Bisphosphoglycerate pool
- Reduced nicotinamide adenine dinucleotide
- 3-phosphoglycerate
- 2-phosphoglycerate
- Phosphoenolpyruvate
- Pyruvate
- Lactate
- Carbon dioxide
- Glycerol
- Glycogen
- Extracellular lactate

The captured run applies the configured metabolic capacity challenge, changing extracellular glucose from `5.5` to `8.25` during the challenge window before returning to baseline. It evaluates 600 s of simulated dynamics across Extracellular glucose, Intracellular glucose, Cellular energy pool, Glucose 6-phosphate, and 19 other tracked variables; read the absolute trajectories, baseline-relative plot, response ranking, and summary table together because the variables use different native scales.

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

1. `karlstaedt2019_g6p_accumulation_pgi_core`: SBML simulator. Receives every contextual input port (ion concentrations, voltages, conductances, etc. — see below), drives roadrunner, and emits two outputs: `state` (per-window species/state-variable record) and `species_labels` (a one-time map of `{species_id: human_label}` lifted from the SBML `<species name=...>` attributes).
2. `karlstaedt2019_g6p_accumulation_pgi_viz`: visualization sub-model. Consumes both `state` and `species_labels` from the core, accumulates the per-window history, prettifies the labels, and renders the two visuals plus the `run_summary` output. No SBML, no roadrunner — pure presentation.

## How to Read the Visualizations

The absolute timeseries plot has one curve per state variable in the SBML model and marks when the challenge and recovery windows begin. The baseline-relative plot rescales each curve against the pre-challenge baseline so small but real responses are visible. The x-axis is simulation time in seconds and the y-axis is the variable's value in its native SBML unit (concentrations in mM or mol, voltages in mV, currents in pA, volumes in mL — refer to the SBML file for the exact unit per variable). Look for periodic patterns (action-potential-style depolarisations, oscillations), monotonic trends, or steady-state plateaus.

The response bar chart ranks final-minus-baseline changes in native SBML units. The "What Happened" table explains the lab question, the applied challenge, the simulated duration, the strongest response, and the interpretation limits.

## What This Lab Contains

- `lab.yaml` declares the two sub-models, runtime, IO, and wiring.
- `wiring-layout.json` places the two nodes on the canvas with the connecting edges.
- `models/core/model.yaml` describes the SBML simulator package.
- `models/core/src/karlstaedt2019_g6p_accumulation_via_phosphogluco_model1910170001_model.py` is the SBML wrapper (no visualization code).
- `models/core/data/MODEL1910170001.xml` is the original SBML file from BioModels.
- `models/core/tests/` checks instantiation, output accumulation, and output keys.
- `models/viz/model.yaml` describes the visualization sub-model.
- `models/viz/src/karlstaedt2019_g6p_accumulation_pgi_viz.py` consumes core state + labels and renders timeseries, Q&A table, and the `run_summary` record.
- `models/viz/tests/` exercises the viz with synthetic state inputs (no SBML or roadrunner needed).

## Inputs

This lab exposes a set of **contextual scalar ports** specific to its SBML, plus three **generic fallback ports** for everything else.

### Contextual ports (recommended)

These map a human-friendly port name onto a real SBML global parameter. Wire them from upstream nodes or set them in `lab.yaml` `runtime.initial_inputs`. Each scalar override is applied to roadrunner before the next `advance_window` call.

| Input | Meaning | Default | Unit |
|---|---|---|---|
| `extracellular_glucose` | Sets extracellular glucose for the scenario. | 5.5 | — |
| `cellular_energy_pool` | Sets cellular energy pool for the scenario. | 3.0417 | — |
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
biosimulant labs import labs/karlstaedt2019-g6p-accumulation-pgi
```

Then open the imported lab and press Run. The results should include the state-variable timeseries and the `What Happened` Q&A table.

## Notes

- The bundled run uses a baseline plus challenge scenario so the first visualization shows a physiological perturbation without changing the upstream SBML equations.
- Default run length is `600` s with a `1` s communication step. These are conservative defaults chosen by category (single-cell electrophysiology vs whole-system circulation vs slow regulatory loop). Tune them in `lab.yaml`.
- Requires `tellurium==2.2.11.2`. The first import compiles the SBML to LLVM in-process.
- License: `CC0` (from upstream BioModels entry [biomodels_ebi:MODEL1910170001](https://www.ebi.ac.uk/biomodels/MODEL1910170001)).
- This wrapper does not modify the upstream biology. To change rates, initial conditions, or kinetic laws, edit the SBML file in `models/core/data/MODEL1910170001.xml` directly.

### Advanced SBML Identifiers

<details>
<summary>Raw upstream identifiers for reproducibility and advanced overrides</summary>

#### SBML Parameters

Full list of global parameter IDs, for use with `parameter_overrides`. Defaults come from the upstream SBML.

| Parameter ID | Name | Default Value |
|---|---|---|
| `Kglc_1` | Kglc_1 | 10 |
| `Ki_1` | Ki_1 | 0.91 |
| `Vmax_1` | Vmax_1 | 106 |
| `Kadp_2` | Kadp_2 | 0.54 |
| `Katp_2` | Katp_2 | 0.78 |
| `Keq_2` | Keq_2 | 2000 |
| `Kg6p_2` | Kg6p_2 | 5.4 |
| `Kglc_2` | Kglc_2 | 0.23 |
| `Vmax_2` | Vmax_2 | 230 |
| `Keq_3` | Keq_3 | 0.28 |
| `Kf6p_3` | Kf6p_3 | 0.3 |
| `Kg6p_3` | Kg6p_3 | 0.425 |
| `Vmax_3` | Vmax_3 | 604 |
| `Vmax_4` | Vmax_4 | 80 |
| `gR_4` | gR_4 | 5.12 |
| `Katp_4` | Katp_4 | 0.71 |
| `Kf6p_4` | Kf6p_4 | 1.5 |
| `L0_4` | L0_4 | 0.66 |
| `Ciatp_4` | Ciatp_4 | 100 |
| `Kiatp_4` | Kiatp_4 | 0.65 |
| `Camp_4` | Camp_4 | 0.0845 |
| `Kamp_4` | Kamp_4 | 0.0995 |
| `Cf26_4` | Cf26_4 | 0.0174 |
| `Kf26_4` | Kf26_4 | 0.000682 |
| `Cf16_4` | Cf16_4 | 0.397 |
| `Kf16_4` | Kf16_4 | 0.111 |
| `Catp_4` | Catp_4 | 3 |
| `Kdhap_5` | Kdhap_5 | 2 |
| `Keq_5` | Keq_5 | 0.069 |
| `Kf16bp_5` | Kf16bp_5 | 0.3 |
| `Vmax_5` | Vmax_5 | 94.69 |
| `Kg3p_5` | Kg3p_5 | 2.4 |
| `Kig3p_5` | Kig3p_5 | 10 |
| `k1` | k1 | 450000 |
| `k2` | k2 | 10000000 |
| `Vmax_7` | Vmax_7 | 1288 |
| `Keq_7` | Keq_7 | 3200 |
| `Kp3g_7` | Kp3g_7 | 0.53 |
| `Katp_7` | Katp_7 | 0.3 |
| `Kbpg_7` | Kbpg_7 | 0.003 |
| `Kadp_7` | Kadp_7 | 0.2 |
| `Vmax_8` | Vmax_8 | 2585 |
| `Kp3g_8` | Kp3g_8 | 1.2 |
| `Keq_8` | Keq_8 | 0.19 |
| `Kp2g_8` | Kp2g_8 | 0.08 |
| `Vmax_9` | Vmax_9 | 201.6 |
| `Kp2g_9` | Kp2g_9 | 0.04 |
| `Keq_9` | Keq_9 | 2.8 |
| `Kpep_9` | Kpep_9 | 0.04 |
| `Kadp_11` | Kadp_11 | 0.53 |
| _... 22 more, see SBML file_ | | |

#### SBML Species

Full list of species IDs, for use with `initial_conditions`.

| Species ID | Name | Initial Value |
|---|---|---|
| `GLCo` | Glc(ext) | 5.5 |
| `GLCi` | Glc(int) | 0.0927 |
| `ATP` | ATP | 3.0417 |
| `G6P` | G6P | 0.8393 |
| `ADP` | ADP | 0.77 |
| `F6P` | F6P | 0.2765 |
| `F16bP` | Fru1,6-P2 | 0.02 |
| `AMP` | AMP | 0.4332 |
| `F26bP` | Fru2,6-P2 | 0.069 |
| `DHAP` | DHAP | 0.0313 |
| `GAP` | G3P | 0.00144742617457075 |
| `NAD` | NAD | 3.2962 |
| `BPG` | BPG | 0.000234272689298054 |
| `NADH` | NADH | 0.0038 |
| `P3G` | P3G | 0.1367 |
| `P2G` | P2G | 0.0208 |
| `PEP` | PEP | 0.0212 |
| `PYR` | Pyr | 0.0063 |
| `AcAld` | Lac | 0.1066 |
| `CO2` | CO2 | 1 |
| `Glycerol` | glycerol | 0.15 |
| `Glycogen` | glycogen | 0.02 |
| `Succinate` | Lac(ext) | 0 |

</details>
