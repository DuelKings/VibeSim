---
name: simulation-workflow
description: Plan, execute, validate, checkpoint, and hand off molecular or periodic computational simulations using the repository's simulation_agent_v1.0.0 playbook; use for ORCA, Quantum ESPRESSO, xTB/CREST, adsorption, bond dissociation, reaction energetics, DOS, charge transfer, and related reproducible simulation tasks.
---

# Simulation workflow

1. Read `simulation_agent_v1.0.0/README.md` and knowledge files `00_ROUTER_AND_WORKFLOW.txt`, `06_SCOPE_GUARDRAILS.txt`, and `07_MACHINE_AND_UTILS_METADATA.txt`; read the relevant simulator/property file. **Done when:** objective, observable, chemical state, periodicity, and applicable limits are recorded.
2. Load the local machine configuration and verify executable versions, available RAM/storage, scratch, artifact destination, and pseudopotential provenance. Treat detection as evidence, not execution permission. **Done when:** every required executable and input asset is verified or the task has an explicit blocker.
3. Build a bounded dependency graph with immutable inputs, per-stage directories, retry limits, validation criteria, checkpoint points, and resource estimates. Use vacuum and 298.15 K defaults only when appropriate and disclose them. **Done when:** each job has dependencies, exact command, timeout, expected outputs, and pass/fail criteria.
4. Generate and lint inputs. Preserve charge/spin, stoichiometry, cell, units, and reference-state consistency. Use verified pseudopotential basenames and compatible exchange-correlation settings. **Done when:** inputs pass structural and program-syntax checks.
5. Run the smallest scientifically meaningful pilot through bounded execution. Maintain at least the configured RAM headroom and global process cap; log exact commands and outputs. **Done when:** pilot timing/memory and convergence behavior are measured or a diagnosed failure is recorded.
6. Continue only through validated dependencies. Retry at most the configured number with one justified parameter change at a time. Never infer rates from static energies or label unconverged work complete. **Done when:** the requested observable is validated, or a precise terminal blocker/status is recorded.
7. Copy inputs, logs, raw/parsed data, structures, plots, manifests, assumptions, errors, and `[question number]_conclusion.txt` to the configured user-visible artifact directory. **Done when:** the destination exists and contains the complete evidence required to audit the claim.
8. Report status, method, numerical result with units, validation, assumptions, uncertainty, retry history, paths, and remaining work. Screening remains nonterminal unless requested. **Done when:** the report matches the preserved artifacts and makes no unrun claim.
