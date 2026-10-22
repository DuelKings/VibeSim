# Installation

1. Install and configure OpenClaw with your own supported model access.
2. On Windows, install WSL and a Linux distribution under the account running OpenClaw. Confirm that the shared handoff path is visible from WSL. Native Linux users skip this step.
3. Install Python 3.10+ and any optional packages required by the selected utilities.
4. Install the required simulators in the execution environment:
   - ORCA: obtain through the official registration/download process and follow its licence.
   - Quantum ESPRESSO.
   - xTB and CREST when conformer or semiempirical workflows are needed.
5. Provide verified pseudopotentials for periodic calculations and retain source, licence, hashes, and recommended-cutoff metadata.
6. Configure machine-specific paths and resource limits; do not copy paths from another machine blindly.
7. Run `initialize.py`, unit tests, and tiny end-to-end smoke calculations before production work.

Never commit credentials, OAuth state, protected OpenClaw configuration, licensed installers, or private data.
