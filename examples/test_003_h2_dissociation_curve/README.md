# Example 003 â€” H2 dissociation curve

This is a sanitized copy of actually executed ORCA 6.1.1 calculations.

The example follows the electronic energy of neutral singlet H2 as its bond is stretched. It contains a 15-point full-CI/cc-pVDZ curve, matching isolated-H references, selected cc-pVTZ basis checks, raw inputs and outputs, resource records, parsed analysis, and PNG/SVG plots.

Key reported values:
- Grid minimum: R = 0.76 Angstrom, E = -1.163672458226 Eh
- Electronic dissociation energy on the cc-pVDZ grid: 4.49303 eV (433.511 kJ/mol)
- cc-pVTZ check at 0.74 Angstrom: De = 4.69975 eV

This reports electronic De, not D0, an activation energy, or a reaction rate. Limitations include finite Gaussian bases, basis-set superposition effects, a coarse distance grid, and omission of zero-point, thermal, relativistic, and nonadiabatic corrections. Hostname and original execution paths were redacted. ORCA is third-party licensed software; no executable or installer is included.
