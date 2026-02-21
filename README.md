# models-cardiovascular

Curated collection of **cardiovascular** simulation models for the **biosim** platform. This repository contains comprehensive computational models of the cardiovascular system, including cardiac electrophysiology, ion channels, circulation dynamics, blood pressure regulation, and arrhythmogenesis.

## What's Inside

### Models (74 packages)

Each model is a self-contained simulation component with a `model.yaml` manifest.

**Cardiovascular** — cardiac electrophysiology, hemodynamics, and circulatory regulation:

#### Cardiac Action Potential Models
- `cardiovascular-sbml-beeler1977-ventricular-myocardial-fiber-ap` — Reconstruction of ventricular action potential
- `cardiovascular-sbml-courtemanche1998-atrialactionpotential` — Ionic mechanisms underlying human atrial action potential
- `cardiovascular-sbml-difrancesco1985-cardiacelectricalactivity` — Model of cardiac electrical activity
- `cardiovascular-sbml-fink2008-ventricularactionpotential` — HERG K+ current contributions to repolarization
- `cardiovascular-sbml-fox2002-ionicmechanism-cardiacmyocytes` — Ionic mechanism of electrical alternans
- `cardiovascular-sbml-grandi2009-ventricularmyocyte` — Novel computational model of human ventricular myocyte
- `cardiovascular-sbml-bondarenko2004-myocyte-ap-apical` — Computer model of action potential in mouse ventricular myocytes
- `cardiovascular-sbml-luo1991-ventricular-ap` — Dynamic model of ventricular cardiac action potential
- `cardiovascular-sbml-luo1994-ventricularcell-epicardium` — Model of guinea-pig ventricular cells
- `cardiovascular-sbml-ten-tusscher-2004-ventricular-myocyte` — Ten Tusscher-Panfilov human ventricular cell model

#### Ion Channel Models
- `cardiovascular-sbml-clancy2001-kchannel` — Cellular consequences of HERG mutations in K+ channels
- `cardiovascular-sbml-luo1995-iks` — Dynamic model of the cardiac delayed rectifier K+ current
- `cardiovascular-sbml-pandit2003-ikr` — Model of IKr delayed rectifier current in human atrial myocytes

#### Arrhythmogenesis & Cardiac Tissue Models
- `cardiovascular-sbml-aslanidi2009-rightatrialtissue-arrhythmogenesis` — Mechanisms of transition from normal to reentrant electrical activity
- `cardiovascular-sbml-aslanidi2009-caninepvj` — Optimal velocity and safety of discontinuous conduction
- `cardiovascular-sbml-benson2008-arrhythmogenesis-endocardial` — Canine virtual ventricular wall (endocardial)
- `cardiovascular-sbml-benson2008-arrhythmogenesis-epicardial` — Canine virtual ventricular wall (epicardial)
- `cardiovascular-sbml-benson2008-arrhythmogenesis-mcell` — Canine virtual ventricular wall (M-cell)

#### Calcium Dynamics
- `cardiovascular-sbml-cooling2007-ip3transients-cardiacmyocyte` — Modeling hypertrophic IP3 transients in cardiac myocytes
- `cardiovascular-sbml-earm1990-calciumdynamics-cardiac` — Model of single atrial cell calcium dynamics
- `cardiovascular-sbml-hinch2004-carelease-spark` — Mathematical model of calcium release sparks

#### Circulation & Blood Pressure Regulation (Guyton Models)
- `cardiovascular-sbml-guyton1972-aldosterone` — Aldosterone regulation in circulation
- `cardiovascular-sbml-guyton1972-angiotensin` — Angiotensin system modeling
- `cardiovascular-sbml-guyton1972-antidiuretichormone` — Antidiuretic hormone effects
- `cardiovascular-sbml-guyton1972-atrialnatriureticpeptide` — Atrial natriuretic peptide regulation
- `cardiovascular-sbml-guyton1972-autonomics` — Autonomic nervous system control
- `cardiovascular-sbml-guyton1972-capillarydynamics` — Capillary dynamics modeling
- `cardiovascular-sbml-guyton1972-electrolytes` — Electrolyte balance
- `cardiovascular-sbml-guyton1972-hearthypertrophy` — Heart hypertrophy modeling
- `cardiovascular-sbml-guyton1972-heartratestrokevolume` — Heart rate and stroke volume control
- `cardiovascular-sbml-guyton1972-kidneybloodflow` — Renal blood flow regulation
- `cardiovascular-sbml-guyton1972-pulmonary` — Pulmonary circulation
- `cardiovascular-sbml-guyton1972-reninrelease` — Renin release mechanisms
- `cardiovascular-sbml-guyton1972-stress` — Stress response in circulation

#### Vascular & Endothelial Models
- `cardiovascular-sbml-chen2006-nitric-oxide-release-from-endothelial-c` — Nitric oxide release from endothelial cells
- `cardiovascular-sbml-chen2007-neuronalendothelialnos` — Vascular and perivascular nitric oxide release

#### Neural Control & Autonomics
- `cardiovascular-sbml-gee2023-central-and-intrinsic-cardiac-circuits` — Neural control of cardiovascular behavior and homeostasis

#### Pacemaker & SA Node Models
- `cardiovascular-sbml-kurata2002-sinoatrialnode` — Pacemaker activity of sinoatrial node cells
- `cardiovascular-sbml-zhang2000-sinoatrial` — Mathematical models of sinoatrial node pacemaking

**Note:** This repository contains 74 models total. The above represents key categories and examples. For a complete list, see the `models/` directory.

## Layout

```
models-cardiovascular/
├── models/<model-slug>/     # One model package per folder, each with model.yaml
├── libs/                    # Shared helper code for curated models
├── templates/model-pack/    # Starter template for new model packs
├── scripts/                 # Manifest and entrypoint validation scripts
├── docs/                    # Governance documentation
└── .github/workflows/       # CI/CD pipeline
```

## How It Works

### Model Interface

Every model implements the `biosim.BioModule` interface:

- **`inputs()`** — declares named input signals the module consumes
- **`outputs()`** — declares named output signals the module produces
- **`advance_to(t)`** — advances the model's internal state to time `t`

Most curated models include Python source under `src/` and are wired together via `space.yaml` in composed simulations without additional code.

### Model Standards

All models in this repository:
- Use SBML (Systems Biology Markup Language) format
- Are sourced from CellML, BioModels, and other curated electrophysiology repositories
- Include tellurium runtime for SBML execution
- Provide `state` output for monitoring simulation results
- Support configurable timesteps via `min_dt` parameter

### Running Models

Models are loaded and executed by the `biosim-platform`. The platform reads `model.yaml`, instantiates the model from its entrypoint, and runs the simulation loop at the configured timestep for the specified duration.

Individual models can be integrated into larger composed simulations (spaces) by wiring their outputs to other models' inputs, enabling multi-scale cardiac modeling.

## Getting Started

### Prerequisites

- Python 3.11+
- `biosim` framework

### Install biosim

```bash
pip install "biosim @ git+https://github.com/BioSimulant/biosim.git@main"
```

### Create a New Model

1. Copy `templates/model-pack/` to `models/<your-model-slug>/`
2. Edit `model.yaml` with metadata, entrypoint, and pinned dependencies
3. Implement your module (subclass `biosim.BioModule` or use a built-in pack)
4. Add cardiovascular-specific tags and categorization
5. Validate: `python scripts/validate_manifests.py && python scripts/check_entrypoints.py`

### Using Models in Spaces

To integrate cardiovascular models into larger simulations:

1. Reference models by `manifest_path` (e.g., `models/cardiovascular-sbml-luo1991-ventricular-ap/model.yaml`)
2. Wire model outputs to inputs of other models in your space configuration
3. Compose multi-scale simulations combining ion channels, cells, tissues, and circulation
4. Configure runtime parameters and simulation duration

## Linking in biosim-platform

- Models can be linked with explicit paths:
  - `models/cardiovascular-sbml-courtemanche1998-atrialactionpotential/model.yaml`
- Models can be composed with other domain models (metabolism, signaling, etc.) in multi-scale simulations

## External Repos

External authors can keep models in independent repositories and link them directly in `biosim-platform`. This repository is curated, not exclusive.

## Validation & CI

Three scripts enforce repository integrity on every push:

| Script | Purpose |
|--------|---------|
| `scripts/validate_manifests.py` | Schema validation for all model.yaml files |
| `scripts/check_entrypoints.py` | Verifies Python entrypoints are importable and callable |
| `scripts/check_public_boundary.sh` | Prevents business-sensitive content in this public repo |

The CI pipeline (`.github/workflows/ci.yml`) runs: **secret scan** → **manifest validation** → **smoke sandbox** (Docker).

## Contributing

- All dependencies must use exact version pinning (`==`)
- Model slugs use kebab-case with domain prefix (`cardiovascular-sbml-`)
- Models must follow the `biosim.BioModule` interface
- SBML/CellML models use tellurium runtime for execution
- Pre-commit hooks enforce trailing whitespace, EOF newlines, YAML syntax, and secret detection
- See [docs/PUBLIC_INTERNAL_BOUNDARY.md](docs/PUBLIC_INTERNAL_BOUNDARY.md) for content policy

## Domain-Specific Notes

**Cardiovascular Focus Areas:**
- **Cardiac Electrophysiology**: Action potential models for ventricular, atrial, SA node, and Purkinje cells
- **Ion Channels**: Models of Na+, K+, Ca2+, and other cardiac ion currents
- **Arrhythmogenesis**: Models of reentrant circuits, conduction velocity, and cardiac arrhythmias
- **Calcium Dynamics**: Intracellular calcium handling, sparks, and excitation-contraction coupling
- **Circulation Control**: Guyton models of long-term blood pressure regulation, hormonal control, and autonomics
- **Vascular Function**: Endothelial function, nitric oxide signaling, and hemodynamics
- **Multi-Scale Integration**: From ion channels → cells → tissue → organ → whole-body circulation

**Common Model Types:**
- Ordinary differential equation (ODE) models of cellular electrophysiology
- Hodgkin-Huxley formalism for ion channel gating
- Markov models of channel state transitions
- Systems-level circulation and regulation models

## License

This repository is dual-licensed:

- **Code** (scripts, templates, Python modules): Apache-2.0 (`LICENSE-CODE.txt`)
- **Model/content** (manifests, docs, wiring/config): CC BY 4.0 (`LICENSE-CONTENT.txt`)

Attribution guidance: `ATTRIBUTION.md`
