# Example 001 â€” methane combustion thermochemistry

This is a sanitized copy of an actually executed ORCA 6.1.1 calculation, not a fabricated example.

Reaction: CH4 + 2 O2 -> CO2 + 2 H2O(g)
Method: gas-phase r2SCAN-3c geometry optimization and harmonic frequencies; triplet O2; 298.15 K thermochemistry.

Contents include starting and optimized geometries, ORCA inputs and raw outputs, command records, wavefunction/property/frequency artifacts, parsed values, conclusion, and plot. The hostname was redacted. Absolute WSL paths in command records document the original execution layout and must be changed on another installation.

Reported result: delta H(298.15 K) = -720.05 kJ/mol at this screening level. No unique overall activation energy is claimed because methane combustion is a multistep radical-chain network.

ORCA is third-party licensed software; no ORCA executable or installer is included.
