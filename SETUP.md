# Replicate the Viber simulation assistant

This repository reproduces the **workspace behavior and simulation workflow**, not a credentialed clone of another installation. Results can still vary with model, OpenClaw version, simulator versions, hardware, pseudopotentials, numerical settings, and scientific inputs.

## 1. Install prerequisites

1. Install OpenClaw and configure it with your own supported model access.
2. On Windows, install WSL2 and a Linux distribution under the same Windows account that runs OpenClaw. Native Linux does not require WSL.
3. Install Python 3.10+.
4. Install the simulators needed by your work:
   - Quantum ESPRESSO for periodic solids, surfaces, DOS, and periodic relaxations.
   - ORCA for isolated molecular electronic-structure calculations. Obtain ORCA through its official registration and licence process; it is not distributed here.
   - xTB and CREST for low-cost molecular optimization and conformer screening.
5. Install MPI compatible with each simulator build where required.
6. Quantum ESPRESSO pseudopotentials are not included. Obtain compatible files from an appropriate source, verify their provenance and licence, record their hashes, and configure the local pseudopotential path.

## 2. Install the workspace

Copy the repository contents into the intended OpenClaw agent workspace. The default is:

- Windows: the workspace configured for the Gateway account, commonly under that account's `.openclaw\workspace`.
- Linux: `~/.openclaw/workspace`.

Alternatively, configure the agent's workspace path to this cloned folder using OpenClaw's Control UI. Do not copy another installation's `~/.openclaw` state, credentials, OAuth data, databases, or transcripts.

The active workspace root must contain:

- `AGENTS.md`
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `skills/simulation-workflow/SKILL.md`
- `simulation_agent_v1.0.0/`

## 3. Configure the local machine

1. Copy `config/machine.example.json` to a local untracked file such as `config/machine.local.json` and fill verified paths and limits.
2. In `simulation_agent_v1.0.0`, run `initialize.py` separately on every execution side:
   - Windows for Windows utilities.
   - WSL/Linux for Linux simulators.
3. Inspect the generated detection report. Detection proves availability, not permission or scientific suitability.
4. Configure a user-visible artifact directory. On Windows+WSL, verify its WSL mapping.
5. Configure exact executable allowlists if using the package's bounded executor.

## 4. Verify

Run the deterministic package tests:

```powershell
cd simulation_agent_v1.0.0
py -3 -m unittest discover -s tests -v
```

Then run `scripts/verify_environment.py --config config/machine.local.json`. Finally perform tiny end-to-end smoke jobs:

- ORCA: H2 HF/STO-3G; require SCF convergence and normal termination.
- QE: minimal H2 SCF with verified pseudopotentials; require convergence and `JOB DONE`.
- xTB: tiny molecule single point; require normal termination.

Do not start production work until the relevant smoke test passes.

## 5. Reproduce a simulation

1. Place the prompt and all input structures in a new per-job artifact directory.
2. Record charge, spin, periodicity, environment, temperature, observable, method, software versions, pseudopotential hashes, resource limits, and assumptions.
3. Build a dependency graph and checkpoint after every stage.
4. Run small pilots first; update cost estimates from measured timing and memory.
5. Validate scientific convergence, not merely process exit.
6. Preserve exact commands, inputs, raw outputs, parsers, plots, conclusions, errors, and retry history.

## Limits

This package cannot reproduce proprietary model weights, hosted service behavior, hidden OpenClaw system policies, credentials, or bitwise-identical floating-point results across machines. It is designed to reproduce the assistant's declared behavior and an auditable simulation process.
