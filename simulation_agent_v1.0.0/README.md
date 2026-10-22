# Agentic Simulation Project — v1.0.0

A cautious, local, **initializable** Python utility project for planning and preparing Quantum ESPRESSO (QE), ORCA and xTB/CREST calculations. The `knowledge/` directory contains the original ten v1.0.0 TXT reference files; `utils/` supplies 26 runnable CLI utilities. **Initialization only discovers resources. It never installs software, launches simulations, downloads pseudopotentials or changes the user's configuration.**

## Quick start

### Windows PowerShell
```powershell
py -3 initialize.py
py -3 -m unittest discover -s tests -v
py -3 utils\structure_parser.py --input examples\h2_parse.json --output examples\h2_structure.json
```

If QE runs inside WSL, open the WSL distribution (e.g. `wsl -d Ubuntu`), change into a **Linux filesystem copy** of the project when performing heavy calculations, and run:
```bash
python3 initialize.py --pseudo-root /path/to/verified/pseudopotentials
python3 -m unittest discover -s tests -v
python3 utils/structure_parser.py --input examples/h2_parse.json --output examples/h2_structure.json
```
The path above is an **example from the supplied listing** and must be checked locally. The WSL distribution name, mount availability and permissions are not guaranteed. Initialization run on Windows detects Windows executables; run it separately **inside WSL** to discover Linux executables. Never pass native Windows paths to Linux executables.

Optional packages: `pip install -r requirements-optional.txt` (some packages, especially pymatgen/RDKit, may need platform-specific installers). Core initialization, math, parsing, QE and ORCA input generation require only Python 3.10+.

## First-time setup
1. Run `python initialize.py` for machine, RAM, CPU, installed Python libraries, executables, WSL availability (Windows only) and pseudopotentials that genuinely exist on the current host.
2. Inspect `config/detected/detected_environment.json`; any missing executable remains **unverified**. For explicit pseudopotential locations supply `--pseudo-root PATH` (repeatable). SHA-256 and available UPF header properties are recorded in separate JSON catalogs.
3. Open `knowledge/07_MACHINE_AND_UTILS_METADATA.txt`; fill in **user-controlled** CPU/RAM/disk usage limits, permissions, exact workspace and software paths. This TXT is authoritative for user preferences; the detected JSON is evidence of local observations. Don't overwrite user settings with detection.
4. Manually decide whether calculations are permitted. The initializer deliberately sets `execution_ready=false` and `allow_unattended=false`. Detection cannot determine power, thermal safety, billing, cluster quotas or allowable job duration.
5. The agent reads `knowledge/00`, `05`, `06`, `07` first, then problem and software manuals; it uses verified JSON metadata to plan resource estimates, validates inputs and asks approval before expensive execution.

## Layout
- `initialize.py`: non-destructive machine/software/WSL discovery and pseudopotential scan.
- `knowledge/*.txt`: scientific and operational playbooks, **version remains 1.0.0**.
- `config/detected/`: generated JSON artifacts (host-specific, do not blindly share).
- `utils/core.py`: shared stdlib implementation. Every other `utils/*.py` has CLI interface `--input INPUT.json --output OUTPUT.json` and `--help`.
- `examples/`: sample JSON, NOT authorization to execute calculations.
- `tests/`: executable unit tests.

## Implemented utilities (name | expected JSON input | output)
| Utility | Input schema (main fields) | Output |
|---|---|---|
| structure_parser.py | `path`: XYZ; CIF/POSCAR with ASE | normalized `atoms`, `cell_angstrom`, `pbc` JSON |
| structure_validator.py | `structure` | heuristic geometry issues, validity |
| conformer_generator.py | `smiles`, `n_conformers`, `seed` (requires RDKit) | ETKDG 3D conformer candidates |
| surface_builder.py | `structure_path`, `miller`, `layers`, `vacuum_angstrom` (ASE) | unvalidated slab candidate |
| adsorption_builder.py | `slab`, `adsorbate`, `translation_angstrom` | merged candidate and collision check |
| pp_catalog_auditor.py | `root` | UPF path, hash, header fields, warnings |
| qe_input_generator.py | `structure`, `settings`, `pseudopotentials`, `pseudo_dir`, `atomic_masses_amu` | QE input text (not executed) |
| orca_input_generator.py | `structure`, `charge`, `multiplicity`, `method`, `basis`, `tasks` | ORCA input text (not executed) |
| xtb_crest_runner.py | `xyz_file`, `charge`, `uhf`, `method` | proposed xTB optimization command, not executed |
| resource_estimator.py | `jobs`, `cores_per_job`, `estimated_hours_per_job`, `ram_gb_per_job`, `available_cores`, `available_ram_gb` | concurrency estimate, core-hours, feasibility |
| job_executor.py | `argv`, `cwd`, `allow_executable_paths`, `explicit_execution_approval`, `timeout_seconds`, optional `stdin_file` | bounded local subprocess log and exit status |
| simulation_monitor.py | `path` | output-file snapshot, warnings, recent lines |
| qe_output_parser.py | `path` | terminal SCF energy, selected force marker, completion |
| orca_output_parser.py | `path` | terminal energy and convergence markers |
| xtb_crest_parser.py | `path` | xTB energy, selected completion marker |
| convergence_validator.py | `parsed` | limited pass/fail and diagnostic messages |
| checkpoint_manager.py | `working_directory`, `restart_files` | restart-file existence checks |
| energy_calculator.py | `terms`: labelled energies and signed coefficients, `input_unit` | eV, kJ/mol, term provenance |
| bandgap_analyzer.py | `states`: `energy_ev`, `occupation` | sampled eigenvalue VBM, CBM, gap |
| orbital_analyzer.py | `orbitals`: `energy_ev`, `occupation` | orbital energy gap; not excitation energy |
| bond_scan_generator.py | `structure`, `atom_i`, `atom_j`, `distances_angstrom` | rigid atom-displacement structures |
| reaction_path_builder.py | `reactant`, `product`, `images` | simple interpolation guesses, **not NEB** |
| trajectory_analyzer.py | `frames`: `temperature_k` | temperature descriptive statistics only |
| conformer_ranker.py | `conformers`: `energy_ev`, optional `fingerprint` | sorting/exact fingerprint dedup only |
| statistics_aggregator.py | `values` | mean, SD, SEM and approximate normal 95% interval |
| simulation_reporter.py | `results`, `assumptions`, `software`, `validation` | timestamped JSON report |

**Limitations:** These are practical baseline tools, not complete scientific workflows. In particular, automated TS/NEB optimization, true adsorption *rates*, reaction kinetics, AIMD MSD/RDF/diffusion (requiring periodic unwrapping), surface termination enumeration, spin-state searches, robust conformer RMSD clustering, version-specific QE/ORCA parameter schemas, MPI scheduling, distributed queues and automatic recovery are **not implemented**. Do not claim they are available. Script names reflecting a broader scope (e.g. `trajectory_analyzer`) currently offer only the explicitly documented subset. ORCA inputs must be checked against the installed version. QE inputs require validated PP basenames that all exist in a single staged `pseudo_dir`; use a staging folder or adapt the generator if they come from several directories. Pseudopotential *presence* or an UPF header does not certify physics, XC consistency or recommended cutoffs.

## Input templates and examples
For XYZ parsing:
```json
{"path":"examples/h2.xyz"}
```
For numerical energy differences (`E_complex - E_slab - E_adsorbate`, **illustrative only**):
```json
{"input_unit":"eV","definition":"E_ads=E_complex-E_slab-E_gas","terms":[{"label":"complex","energy":-9,"coefficient":1},{"label":"slab","energy":-6,"coefficient":-1},{"label":"molecule","energy":-2,"coefficient":-1}]}
```
For bounded resource estimation:
```json
{"jobs":24,"cores_per_job":4,"estimated_hours_per_job":2,"ram_gb_per_job":8,"available_cores":16,"available_ram_gb":32,"user_concurrency_cap":2}
```
Run with `python utils/energy_calculator.py --input examples/energy.json` etc. Numerical estimators cannot guarantee actual resource use.

## User question → scientific jobs
The agent must count **structures/configurations × parameter studies × independent replicas × required reference calculations**. For adsorption, distinct sites and orientations are *different structural cases*, not independent stochastic replicas. Adsorption **rate** additionally requires an explicit kinetics model, energy barriers and/or statistically adequate dynamical data. Never equate average adsorption energy with a rate. Run only cheap pilots before applying calibrated timing estimates; request user approval for full AIMD, large NEB studies or extensive enumerations.

On SCF/relaxation failure, parse logs, diagnose likely cause, and propose bounded changes in mixing, diagonalization, initial magnetization, occupations, constraints, timestep or optimizer **as relevant**; do not blindly vary everything. Every retry must have a separate input/record and budget. Switching XC, spin model, pseudopotential or chemical state is a **scientific model change** requiring explicit disclosure. Current project does *not* automatically perform this retry loop.

## Security and reproducibility
- CLI tools use explicit JSON; no arbitrary Python code execution or dynamic imports from user inputs.
- `job_executor.py` is OFF by default. It requires an exact resolved executable allowlist, `explicit_execution_approval=true`, bounded timeout, and verified working directory. It does not provide full process sandboxing or OS-level CPU/RAM restrictions—use external OS/scheduler limits for untrusted or costly jobs.
- WSL paths must be verified; on Windows run `initialize.py` natively **and** in WSL when both targets are relevant.
- For reproducibility, preserve software versions, UPF SHA-256 hashes, scientific assumptions, input files, job logs, energy units, convergence evidence and retry history.
- The environment probe tests installation/path **availability**, not scientific correctness; no external tools are launched during initialization.

## Testing
```bash
python -m unittest discover -s tests -v
python initialize.py --no-pp-scan
```
Optional performance calibration: run a user-approved small pilot with the actual method/pseudopotentials, record measured timing/memory, then feed these measurements into `resource_estimator.py`.
