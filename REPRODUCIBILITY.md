# Reproducibility contract

A reproduced run is acceptable only when it preserves:

- Original question and immutable input structures.
- Chemical composition, charge, multiplicity, periodicity, environment, temperature, and standard state.
- Software names, versions, build/MPI details, and executed commands.
- Method, basis or cutoffs, dispersion, grids, k-points, smearing, pseudopotentials, constraints, and convergence thresholds.
- Pseudopotential provenance and SHA-256 hashes.
- Machine/resource configuration, concurrency, elapsed time, retries, and stop conditions.
- Raw logs plus parsed values with units and sign conventions.
- Geometry/SCF/frequency/force validation appropriate to the claim.
- Assumptions, uncertainties, failed attempts, and unresolved dependencies.
- User-visible artifact handoff.

## Status vocabulary

Use explicit states such as `PLANNED`, `RUNNING`, `INPUTS_READY`, `BLOCKED_NEEDS_USER_INFO`, `BLOCKED_METHOD`, `FAILED`, `SKIPPED_RESOURCE_LIMIT`, `COMPLETED_SCREENING`, and `COMPLETED_VALIDATED`.

A screening result is nonterminal unless screening was the requested endpoint. A process exit is not proof of scientific convergence. Static energies are not rates. Molecular orbital gaps are not automatically optical gaps. Adsorption energies require consistent slab, adsorbate, and interface references.
