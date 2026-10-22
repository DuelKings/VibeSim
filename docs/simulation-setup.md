# Simulation setup

## Required local configuration

Record and verify:

- OS and execution target (native Linux, Windows, or WSL).
- CPU threads, available RAM, required system headroom, disk and scratch limits.
- Exact ORCA, Quantum ESPRESSO, xTB, CREST, Python, and MPI versions/paths.
- Pseudopotential collection, exchange-correlation consistency, hashes, and cutoff guidance.
- Workspace, scratch, checkpoint, and artifact-handoff paths.
- Concurrency, wall-time, retry, warning, and stop policies.

## Verification

1. Run package unit tests.
2. Run an ORCA H2 smoke calculation and require normal termination and SCF convergence.
3. Run a minimal Quantum ESPRESSO SCF using verified pseudopotentials and require `JOB DONE`.
4. Run a tiny xTB calculation when xTB workflows are enabled.
5. Confirm outputs are copied to the configured user-visible artifact directory.

## Scientific rules

Use consistent reference states, methods, pseudopotentials, cells, charge/spin states, and units. Treat screening as nonterminal unless screening was explicitly requested. Never infer rates from static energies or claim convergence from process exit alone.
