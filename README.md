# Codex Project Pilot

An evidence-backed Codex Skill for coordinating several projects, repositories,
and agent-owned workstreams toward one persistent goal.

It provides a portable portfolio manifest, runtime admissions, deterministic
thread-topology audits, first-nonzero formal-round semantics, a hash-chained
decision ledger, long-contract routing, and privacy-gated GitHub publication
guidance.

The recommended topology separates four control-plane responsibilities (root
decisions, scheduling, runtime supervision/migrations, and owner liaison) from
project execution. Runtime snapshots make duplicate control roles, stale owners,
unfenced migrations, excess active turns, and multiple project writers visible
before they become coordination failures.

Optional per-task context-health readbacks make summary degradation and runtime
context warnings auditable. Scheduling emits one deduplicated renewal recommendation
to the sole migration controller; it never migrates a task based on a fixed number
of compactions or an invented token threshold.

Control-lifecycle readbacks distinguish a finished turn from a finished portfolio.
An active running monitor must renew a machine-auditable work lease with admission,
dispatch, ledger delta, or terminal evidence. Plans and timestamp-only snapshots do
not count. The first empty check cannot create a silent stop: every pause must first
send one deduplicated result or decision notice through the owner liaison, read back
its matching delivery turn, and remain visible for successful as well as failed
runs. Only then may the recurring automation pause.

## Install

Requires Python 3.10 or newer for the deterministic control script.

```powershell
git clone https://github.com/RedeatI/codex-project-pilot.git "$env:USERPROFILE\.codex\skills\codex-project-pilot"
```

Then invoke `$codex-project-pilot` or describe a multi-project portfolio task.

## Validate

```powershell
python scripts/portfolio_control.py --help
python scripts/portfolio_control.py audit-topology portfolio.json topology.json
python -m unittest discover -s tests -v
python tests/e2e_cli.py
python path\to\skill-creator\scripts\quick_validate.py .
```

See `references/portfolio-schema.md` for the manifest and
`references/thread-architecture.md` for control-plane and project-task topology.
See `references/execution-contracts.md` for admission and convergence behavior.
Read `references/github-publication.md` before any GitHub upload or visibility
change.

## Safety model

The Skill automates routing and evidence handling, not permission. External writes,
publication, releases, destructive cleanup, and credential use remain explicitly
authorized actions. Real secrets stop a publication candidate and are never printed
into reports or ledgers.

## License

Apache License 2.0.
