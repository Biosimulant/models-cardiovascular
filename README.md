# models-cardiovascular

Curated cardiovascular labs for the Biosimulant platform. The current source tree contains 27 publishable labs under `labs/`; each lab pairs a scientifically sourced SBML simulator with a separate visualization model so the core biology stays clean and presentation logic stays isolated.

## Repository Layout

```text
models-cardiovascular/
├── labs/<lab-slug>/
│   ├── lab.yaml
│   ├── wiring-layout.json
│   ├── README.md
│   └── models/
│       ├── core/            # SBML/tellurium BioModule wrapper and data
│       └── viz/             # Presentation-only BioModule
├── scripts/
│   ├── audit_labs.py
│   ├── check_entrypoints.py
│   └── validate_manifests.py
├── docs/
└── templates/
```

The old `models/<long-slug>/` layout has been superseded by lab-level packages. Do not restore deleted legacy model folders unless a separate migration explicitly asks for that.

## Lab Pattern

Every lab uses the same two-node canvas pattern:

- `*_core`: loads the bundled SBML file, runs it with `tellurium==2.2.11.2`, accepts solver settings plus SBML parameter or initial-condition overrides, and emits raw `state` plus `species_labels` records.
- `*_viz`: consumes the core records, accumulates a short history, renders a user-friendly state-variable timeseries, and emits a `What Happened` Q&A table plus `run_summary`.

The visualization model is intentionally presentation-only. It may parse, summarize, relabel, and format outputs, but it must not change SBML equations, kinetic laws, or simulation state.

## Importing a Lab

Import a lab source folder directly into Biosimulant Desktop:

```bash
biosimulant labs import labs/chen2006-endothelial-no-release
```

Republishing and re-importing are source-release steps handled outside this repository hardening pass.

## Validation

Run the source checks from the repository root:

```bash
PYTHONPATH=../../bsim-active/biosim/src \
../../bsim-active/biosim/.venv/bin/python \
scripts/validate_manifests.py
```

```bash
PYTHONPATH=../../bsim-active/biosim/src \
../../bsim-active/biosim/.venv/bin/python \
scripts/check_entrypoints.py
```

```bash
PYTHONPATH=../../bsim-active/biosim/src \
../../bsim-active/biosim/.venv/bin/python \
scripts/audit_labs.py
```

```bash
PYTHONPATH=../../bsim-active/biosim/src \
../../bsim-active/biosim/.venv/bin/python \
-m pytest
```

## Scientific Scope

These labs wrap upstream cardiovascular SBML models, primarily from BioModels. They are simulation and exploration tools, not clinical decision systems. User-facing summaries should describe what changed in the simulated state, not make diagnostic or treatment claims.

## License

Code is covered by the repository code license. Bundled SBML model/content licensing is documented in each core `model.yaml` under `upstream`.
