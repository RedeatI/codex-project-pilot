---
name: codex-project-pilot
description: Coordinate several software projects or agent-owned workstreams with evidence-backed state, host and authority gates, deterministic admissions, progress ledgers, and safe automatic next-action routing. Use for portfolio-wide planning, continuous advancement, task recovery, or multi-repository GitHub publication; do not use for a single ordinary coding task.
---

# Codex Project Pilot

Advance a portfolio toward the user's actual end state without losing authority,
host identity, or evidence boundaries.

## Operating loop

1. Recover current state from runtime metadata, repositories, task status, retained
   evidence, and external readbacks. Treat summaries as leads, not proof.
2. Maintain one portfolio manifest with stable project IDs, roots, host IDs, owner
   tasks, authorities, desired outcomes, and current states.
3. Select the smallest set of independent next actions that materially advances the
   portfolio. Keep one writer per project and serialize migrations or shared-state
   changes.
4. Before dispatch or mutation, evaluate the action against runtime readback. Use
   `scripts/portfolio_control.py admit` when the action crosses hosts, writes a
   repository, changes external state, or resumes after uncertain context.
5. Dispatch long contracts that cover safe preflight through verification. Include
   explicit stopping conditions and require final readback rather than frequent
   status chatter.
6. Monitor deltas, not full transcripts. Classify approval, missing authority,
   host mismatch, harness failure, product failure, and external-state waiting as
   different outcomes.
7. Append material decisions and terminal results to the hash-chained portfolio
   ledger. Recompute the next action from current evidence and continue while safe.
8. Claim completion only after every requirement has authoritative evidence. Keep
   the user's full goal active when any requirement remains unproved.

Automatic advancement never implies automatic permission. Obtain explicit user
authorization before external writes, repository publication, release, credential
use, destructive cleanup, or owner-only actions.

## Modes and references

- When creating or changing the portfolio manifest, read
  [references/portfolio-schema.md](references/portfolio-schema.md).
- When dispatching, recovering, migrating, or converging tasks, read
  [references/execution-contracts.md](references/execution-contracts.md).
- When uploading or publishing repositories, read
  [references/github-publication.md](references/github-publication.md).

## Deterministic controls

Use `scripts/portfolio_control.py` for mechanics that should not be improvised:

```text
python scripts/portfolio_control.py validate-manifest PORTFOLIO.json
python scripts/portfolio_control.py status PORTFOLIO.json --ledger EVENTS.jsonl
python scripts/portfolio_control.py admit PLAN.json READBACK.json
python scripts/portfolio_control.py append-event EVENTS.jsonl EVENT.json --expected-seq N --expected-prev-hash HASH
python scripts/portfolio_control.py verify-ledger EVENTS.jsonl
```

An admission `NONZERO` stops that formal round. Do not repair, retry, change entry
points, or reinterpret it inside the same round. A later attempt needs a new action
or round ID and a material difference recorded in the ledger.

The ledger lock is fail-closed. Never delete a stale lock directory automatically;
inspect the writer and retained evidence before an explicitly authorized recovery.
