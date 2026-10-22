# USER.md - Simulation Replication Defaults

<!-- observed: 2026-10-22 | status: active -->

- Prefer concise responses without filler or long preambles.

<!-- observed: 2026-10-22 | status: active -->

- For underspecified simulations, default to vacuum only when the environment is genuinely unspecified and chemically appropriate, and default to 298.15 K. Attempt both an elementary transition-state barrier and an apparent Arrhenius activation energy when scientifically definable. Use AIMD to explore plausible pathways when feasible, warn before computational load becomes excessive, choose defensible values for nonessential omissions, and document every assumption.

<!-- observed: 2026-10-22 | status: active -->

- Limit each simulation question to 120 wall-clock hours, warn at 96 elapsed hours, and preserve checkpoints and partial artifacts.

<!-- observed: 2026-10-22 | status: active -->

- Allow at most 16 concurrent simulator processes system-wide while retaining at least 4 GiB available RAM; reduce concurrency whenever hardware safety requires it.

<!-- observed: 2026-10-22 | status: active -->

- Copy every simulation's inputs, logs, data, plots, and conclusions to the configured user-visible shared artifact directory in a per-job subfolder before reporting completion.
