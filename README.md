# Codex Project Pilot (v2.6 Turbo)

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/Tests-116%20Passed-brightgreen.svg)](tests/)
[![Architecture: Federated Thin Kernel](https://img.shields.io/badge/Topology-Federated%20Thin%20Kernel-purple.svg)](references/thread-architecture.md)

An evidence-backed Codex Skill for coordinating multiple projects, repositories, and agent workstreams toward persistent, multi-stage delivery goals.

---

## Key Capabilities

* **Federated Thin Kernel Topology**: Project owners own local implementation, diagnosis, recovery, and Git closeout inside an explicit authority envelope. The thin governance kernel retains only scheduling policy, deterministic runtime supervision, and owner liaison.
* **Dual-Core Asymmetric Compute Tiering**:
  * **GPT-5.6 Sol (`high reasoning`)**: Strategic planning, multi-project dependency arbitration, architectural partitioning, and complex root-cause diagnosis.
  * **GPT-5.6 Terra (`primary worker`)**: High-throughput (100+ t/s) multi-file feature implementation, business logic assembly, and type validation.
  * **GPT-5.6 Luna / Light (`light worker`)**: Boilerplate generation, documentation, changelogs, and receipt drafting.
* **Build-Only Fast Track**: Eliminates micro-test fixation loops during active feature coding. Enforces sub-second syntax/type checks (`tsc --noEmit`, `py_compile`, `cargo check`) during implementation and runs full validation suites in bulk at stage closeout.
* **30-Second Stub & Bypass Protocol**: Prevents rabbit-hole stalls on third-party flakiness or non-core issues. Stubs unresolved blockers into `.agents/BLOCKERS.md` after at most one repair attempt.
* **Elastic Uncapped Concurrency**: Dynamically dispatches all unblocked, active projects in parallel waves with zero artificial concurrency bottlenecks while preserving exclusive single-writer leases per repository.
* **Zero-Progress Circuit Breaker**: Enforces `max_zero_progress_retries = 1`, forbidding repetitive test executions without intervening code diffs.
* **Deterministic Terminal Receipts**: Cryptographically anchored JSON evidence receipts (`TERMINAL_RECEIPT_V2_6`) verify delivery before allowing autonomous goal roll-forward.

---

## Architecture & Topology

```text
               ┌─────────────────────────────────────────────────────────────┐
               │           Strategic Decision Core (GPT-5.6 Sol High)         │
               │   - Scheduler (Capacity, dependency, wave dispatch)         │
               │   - Runtime Supervisor (Hash-chained ledger, single lock)   │
               │   - Owner Liaison (Human escalations & credentials)         │
               └──────────────────────────────┬──────────────────────────────┘
                                              │
                      ┌───────────────────────┼───────────────────────┐
                      │ Elastic Parallel Wave Dispatch (Uncapped)     │
                      ▼                       ▼                       ▼
         ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
         │ Project Owner 1 (Terra) │ │ Project Owner 2 (Terra) │ │ Project Owner N (Terra) │
         │  - Isolated Git Tree    │ │  - Isolated Git Tree    │ │  - Isolated Git Tree    │
         │  - Single Writer Lease  │ │  - Single Writer Lease  │ │  - Single Writer Lease  │
         │  - Build-Only FastTrack │ │  - Build-Only FastTrack │ │  - Build-Only FastTrack │
         └─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
```

### Control vs. Project Role Separation

| Plane | Role | Primary Responsibilities | Strict Anti-Patterns / Forbidden Actions |
| :--- | :--- | :--- | :--- |
| **Control** | `scheduler` | Capacity ranking, dependency ordering, dispatch policy, and efficiency proposals. | Must NOT grant authority, mutate repositories, write ledgers, or act as project writer. |
| **Control** | `runtime_supervisor` | Delta monitoring, hash-chained ledger, task lifecycle, and migration lock. | Must NOT make product decisions or write project code. |
| **Control** | `owner_liaison` | Routing genuine owner-only decisions (credentials, deployment, destructive actions). | Must NOT act as dispatcher or repository writer. |
| **Project** | `project_owner` (Terra) | Local implementation, fast-track build, focused tests, and local Git closeout. | Must NOT mutate other projects or assume control-plane authority. |

---

## Contract Progression (v2.4 $\rightarrow$ v2.6 Turbo)

* **v2.4 (`PROJECT_TASK_CONTRACT_V2_4`)**: Introduced the validation-value gate, explicit `routine_public_network` envelope, and continuous progress across temporary blockers.
* **v2.5 (`PROJECT_TASK_CONTRACT_V2_5`)**: Added proactive heartbeat sweeps, rolling project goal contracts, single canonical request routing (`OWNER_LIAISON_ROUTING_V1`), and bounded admission token fallback.
* **v2.6 Turbo (`PROJECT_TASK_CONTRACT_V2_6_TURBO`)**: Adds dual-core compute tiering, build-only fast track (banning intermediate unit tests), 30-second stub & bypass, elastic uncapped multi-project concurrency, and structured `TERMINAL_RECEIPT_V2_6` schemas.

---

## Quick Start & Installation

Requires **Python 3.10+**.

```powershell
# Clone to local Codex skills directory
git clone https://github.com/RedeatI/codex-project-pilot.git "$env:USERPROFILE\.codex\skills\codex-project-pilot"
```

To invoke in Codex Desktop, type `$codex-project-pilot` or reference the skill directly.

---

## Validation & Audit Suite

Run the deterministic control and test suite:

```powershell
# Display CLI capabilities
python scripts/portfolio_control.py --help

# Run topology and lease audits
python scripts/portfolio_control.py audit-topology portfolio.json topology.json

# Execute full automated test suite (116 tests)
python -m unittest discover -s tests -v

# Run CLI end-to-end simulation
python tests/e2e_cli.py
```

---

## Reference Documentation

* [`references/portfolio-schema.md`](references/portfolio-schema.md): Portfolio manifest schema and field reference.
* [`references/thread-architecture.md`](references/thread-architecture.md): Topology snapshots, control-plane roles, and migration locks.
* [`references/execution-contracts.md`](references/execution-contracts.md): Turbo fast-track, dynamic risk slicing, and stage closeout contracts.
* [`references/project-task-prompt-template.md`](references/project-task-prompt-template.md): High-velocity dispatch prompt contracts and micro-directives.
* [`references/gpt-5p6-sol-risk-calibration.md`](references/gpt-5p6-sol-risk-calibration.md): Dual-core compute tiering and anti-over-verification calibrations.
* [`references/terminal-receipt-schema.json`](references/terminal-receipt-schema.json): Standardized JSON schema for evidence receipts.
* [`references/github-publication.md`](references/github-publication.md): Secret-scanning and safe GitHub publication protocols.

---

## Safety Model

Codex Project Pilot automates evidence-backed routing and deterministic execution, **not blanket authorization**. Credentials, production database mutation, external deployment, destructive cleanup, cross-host migration, and force-push operations remain strict, user-authorized gates.

---

## License

Apache License 2.0.
