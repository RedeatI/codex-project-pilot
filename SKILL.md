---
name: codex-project-pilot
description: Coordinate several software projects or agent-owned workstreams with evidence-backed state, thread-topology controls, host and authority gates, deterministic admissions, progress ledgers, and safe next-action routing. Use for portfolio-wide planning, task-architecture audits, continuous advancement, recovery, or multi-repository GitHub publication; do not use for a single ordinary coding task.
---

# Codex Project Pilot

Advance a portfolio toward the user's actual end state without losing authority,
host identity, or evidence boundaries.

## Operating loop

1. Recover current state from runtime metadata, repositories, task status, retained
   evidence, and external readbacks. Treat summaries as leads, not proof.
2. Maintain one portfolio manifest with stable project IDs, roots, host IDs, owner
   tasks, authorities, desired outcomes, and current states. When tasks are being
   added, resumed, migrated, or rebalanced, also maintain an authoritative thread
   topology snapshot.
3. Select the smallest set of independent next actions that materially advances the
   portfolio. Separate control-plane roles from project writers, keep one writer
   lease per project, count nested workers as execution units, reserve control-plane
   capacity before calculating a new-dispatch budget, and serialize migrations or
   shared-state changes. A worker hidden inside an active Root turn still consumes
   capacity and a writer lease; if its identity or count cannot be read back,
   conservatively set new-dispatch budget to zero.
   Prioritize complete implementation, integration, and acceptance-candidate actions
   for the manifest's declared focus projects. Allocate new valid capacity to them
   first only after effective-capacity, fresh-admission, authority, host/root, and
   unique-writer gates pass. A priority label never justifies filler, duplicate tasks,
   an invalid task/worktree, or an empty heartbeat.
   Treat `max_active_turns` as a configured portfolio ceiling, never as proof of a
   platform guarantee. If runtime provides a smaller authoritative ceiling, calculate
   the effective ceiling as the smaller value. Capacity beyond
   `baseline_max_active_turns` is surge capacity: dispatch it only to a complete,
   effective project action with fresh admission `ZERO`, an exact action ID, and the
   same independent project task holding the writer lease. Never fill surge capacity
   with control roles, nested workers, empty helpers, duplicate work, or migration
   bypasses.
   Root owns admission, authority, priority, stop conditions, major decisions, and
   result aggregation only. Project implementation, tests, builds, fixes, and
   delivery must run in that project's independent task. Root cannot substitute
   itself or a Root-controlled nested worker when the correct project task is
   unavailable.
   At every completed project stage, keep the writer in that project task and close
   `evidence -> test -> build -> diff -> readback -> commit -> push -> merge`. Record
   an exact source branch, target branch, commit SHA, remote readback, and merge
   readback. Mark build or merge `NOT_REQUIRED` only when the project contract proves
   that fact. On unknown identity, foreign dirty paths, conflict, or the first
   nonzero, stop once and mark every later step `UNEXECUTED`; never force push or
   force merge. Root may decide authority or conflicts but cannot perform the closeout.
   Treat context pressure as topology state: after compaction, audit the summary as
   short/accurate/usable. If renewal is required, notify the sole migration
   controller once; never use a fixed compaction count or let scheduling launch the
   migration.
   A user authorization for stuck-thread recovery is conditional, not a blanket
   create/archive permission. `waiting`, ordinary latency, one idle turn, and unknown
   state are not `stuck`. Require executor-owned proof of the exact old task, host,
   root/worktree, frozen model/thinking, retained checkpoint, and terminal blocker.
   Only the sole migration controller may acquire the one global lock, create one
   provisional `HANDOFF_ONLY` successor under a materially different fresh admission,
   obtain `HANDOFF_ACCEPTED`, transfer the writer lease exactly once, and recoverably
   archive the preserved old task. Never delete the old task/worktree/evidence or
   create a duplicate successor for the same target.
   Treat willingness to consider moving a project between hosts as permission to
   propose one exact request, not authority to move it. Prefer same-host recovery.
   A cross-host request is eligible only when executor-owned evidence proves the
   current host blocks the next admitted project action and the proposed target host
   plus exact path can materially remove that blocker. Route the exact project/task,
   source-host blocker, target host/path, frozen model/thinking, writer/candidate,
   retained worktree/evidence, byte-preservation plan, single-lock plan, and rollback
   plan through the owner liaison. Without a new exact user authorization, do not
   change host, create a replacement, transfer the writer, or acquire the lock.
   When a real blocker needs user judgment, a choice, login, desktop action, host
   migration, or another owner-only action, notify the user promptly through the
   owner liaison. State the exact blocker, why authorized automation cannot resolve
   it, the smallest options, the recommendation, and the next step; never wait
   silently. Resolve mechanical, path, harness, and scheduling issues internally
   when existing authority suffices, without sending low-value owner messages.
4. Before dispatch or mutation, evaluate the action against runtime readback. Use
   `scripts/portfolio_control.py admit` when the action crosses hosts, writes a
   repository, changes external state, or resumes after uncertain context.
   Before every validation, name the blocker it removes or decision it changes and
   the new evidence expected. If the result cannot change the next action, only
   repeats still-valid evidence, or produces no new evidence, mark it `NOT_REQUIRED`
   and do not run it. Keep mandatory safety, authority, publication, merge, release,
   and first-time final readbacks. Prefer one high-information check over repeated
   inspection. Treat model claims, plans, queues, static checks, local output, and
   historical output as non-authoritative for remote, GitHub, merge, deployment, or
   release state.
5. Dispatch long contracts that cover safe preflight through verification. Include
   explicit stopping conditions and require final readback rather than frequent
   status chatter. Use `PROJECT_TASK_CONTRACT_V2_2`; do not interpret permission to
   continue as deploy, release, credential, production-data, or destructive authority.
   Default to delivery-first staging: finish core functionality, integration, and
   acceptance evidence before non-blocking deep security research. Record deferred
   research as an explicit pre-release gate. Never defer known critical/high defects,
   authentication or permission fail-closed checks, credential or destructive-data
   risks, necessary dependency/supply-chain checks, or publication controls.
6. Monitor deltas, not full transcripts. Classify approval, missing authority,
   host mismatch, harness failure, product failure, and external-state waiting as
   different outcomes. Deduplicate context-renewal notifications by target and
   notification ID. Treat runtime idle as turn completion, not portfolio completion.
   Require each active `running` monitor to renew an evidence-backed work lease by
   admitting, dispatching, advancing ledger evidence, or recording a terminal result.
   A plan, timestamp, topology snapshot, or no-change counter is not work. One empty
   running check routes to attention; one empty waiting check prepares a pause.
   Before any pause, including `waiting`, deliver one deduplicated result or decision
   notice through the declared owner liaison, wait for its matching closure and
   delivery-turn readback, persist that delivery preceded the pause, and keep success
   notifications user-visible. A Root final alone is not delivery proof. If delivery
   fails, pausing is forbidden and the next run may retry only that same closure.
7. Append material decisions and terminal results to the hash-chained portfolio
   ledger. Recompute the next action from current evidence and continue while safe.
8. Claim completion only after every requirement has authoritative evidence. Keep
   the user's full goal active when any requirement remains unproved.

A heartbeat is a bounded control trigger, not progress by itself. It must perform or
dispatch one admitted action and emit a `WORK_LEASE_READBACK`, or enter the
owner-liaison delivery gate before stopping automation renewal in that same run.

Automatic advancement never implies automatic permission. Obtain explicit user
authorization before external writes, repository publication, release, credential
use, destructive cleanup, or owner-only actions.

## Modes and references

- When creating or changing the portfolio manifest, read
  [references/portfolio-schema.md](references/portfolio-schema.md).
- When auditing, creating, recovering, migrating, or rebalancing tasks, read
  [references/thread-architecture.md](references/thread-architecture.md).
- When dispatching, recovering, migrating, or converging tasks, read
  [references/execution-contracts.md](references/execution-contracts.md).
- When preparing a project execution prompt, read
  [references/project-task-prompt-template.md](references/project-task-prompt-template.md)
  and its linked Sol risk-calibration evidence.
- When uploading or publishing repositories, read
  [references/github-publication.md](references/github-publication.md).

## Deterministic controls

Use `scripts/portfolio_control.py` for mechanics that should not be improvised:

```text
python scripts/portfolio_control.py validate-manifest PORTFOLIO.json
python scripts/portfolio_control.py status PORTFOLIO.json --ledger EVENTS.jsonl
python scripts/portfolio_control.py audit-topology PORTFOLIO.json TOPOLOGY.json
python scripts/portfolio_control.py admit PLAN.json READBACK.json
python scripts/portfolio_control.py append-event EVENTS.jsonl EVENT.json --expected-seq N --expected-prev-hash HASH
python scripts/portfolio_control.py verify-ledger EVENTS.jsonl
```

An admission `NONZERO` stops that formal round. Do not repair, retry, change entry
points, or reinterpret it inside the same round. A later attempt needs a new action
or round ID and a material difference recorded in the ledger.

The ledger lock is fail-closed. Never delete a stale lock directory automatically;
inspect the writer and retained evidence before an explicitly authorized recovery.
