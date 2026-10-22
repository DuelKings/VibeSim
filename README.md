# Viber Research Assistant

Portable behavior files and simulation workflow for an OpenClaw research assistant focused on simulation and LLMs.

## Included

- `AGENTS.md`: operating, safety, memory, and workspace rules.
- `SOUL.md`: communication style and personality.
- `IDENTITY.md`: assistant identity and research role.
- `USER.md`: active portable simulation defaults matching this assistant’s declared limits.
- `USER.example.md`: blankable user-policy template for adopters who want different defaults.
- `skills/simulation-workflow/`: discoverable OpenClaw workflow that routes simulation requests through the playbook.
- `simulation_agent_v1.0.0/`: simulation knowledge, utilities, tests, and package documentation.
- Quantum ESPRESSO pseudopotentials are not included. Users running QE workflows must obtain compatible pseudopotentials from an appropriate source, verify their provenance and licences, and configure the local pseudopotential path.
- `docs/`: installation and simulation setup.
- `examples/`: three sanitized, actually executed ORCA examples with inputs, outputs, analysis artifacts, plots, and method-specific notes.

## Prerequisites

- A configured OpenClaw installation using the adopter's own model-provider access. This repository contains no account, API key, OAuth token, or model entitlement.
- Windows: WSL must be installed and accessible to the same account that runs OpenClaw. Native Linux does not need WSL.
- Required simulation programs and dependencies must be installed in the execution environment. ORCA may require registration and acceptance of its licence; verify all other software licences before use.
- Install the required simulation software. OpenClaw can detect and configure local execution paths during initialization. QE users must supply compatible pseudopotentials; the included ORCA examples do not require them.
- Run the included verification tests and simulator smoke tests before production calculations.

## Running the included examples through OpenClaw

A user can clone this repository, use it as an OpenClaw workspace, and ask OpenClaw to rerun an example—for example:

> Re-run the simulation in `examples/test_001_methane_combustion` using the included inputs.

After meeting the prerequisites above, ensure the cloned folder is the active OpenClaw workspace so `skills/simulation-workflow/` is discovered. OpenClaw initialization can detect local execution paths and create the local machine configuration.

Standalone launch scripts are not required for this mode: OpenClaw can inspect and execute the included ORCA inputs under the simulation workflow. The repository does not guarantee unattended, one-click, bitwise-identical, or failure-free reproduction. Results can vary with the OpenClaw model, ORCA version, platform, hardware, numerical libraries, and local configuration.

## Replication guide

Follow [`SETUP.md`](SETUP.md) to install the workspace, configure the execution machine, verify simulators, and reproduce simulations. See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for the evidence required for a defensible result.

## Quick verification

From `simulation_agent_v1.0.0`:

```powershell
py -3 initialize.py --no-pp-scan
py -3 -m unittest discover -s tests -v
```

If simulators are installed in WSL, OpenClaw will also check that environment. Simulations run only when requested by the user.

## Security and privacy

Do not commit secrets, protected configuration, memories, transcripts, private research data, licensed installers, pseudopotential archives without redistribution permission, or large scratch/checkpoint files.

## Licence

Repository-authored code and documentation are released under the [MIT License](LICENSE). Third-party software and generated artifacts retain any applicable upstream terms.
