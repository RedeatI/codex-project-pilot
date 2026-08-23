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
3. Select the smallest set of independent, stage-complete next actions that
   materially advances the portfolio. Prefer one complete project contract over a
   sequence of half-step contracts when host, authority, input, and writer identity
   are already known. Separate control-plane roles from project writers, keep one writer
   lease per project, count nested workers as execution units, reserve control-plane
   capacity before calculating a new-dispatch budget, and serialize migrations or
   shared-state changes. A worker hidden inside an active controller turn still consumes
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
   Select the governance mode explicitly. In `federated_thin_kernel` mode, each
   project owner owns project-local action selection, admission, recovery, tests,
   delivery, and closeout inside its manifest authority envelope. The scheduler owns
   only capacity, dependency, dispatch-policy, and efficiency proposals; it cannot
   grant authority, write repositories or the ledger, control migrations, handle
   owner requests, or become a hidden root. Runtime supervision applies deterministic
   ledger, lifecycle, and migration rules, while the owner liaison carries exact
   exceptions to the user. Require manifest and topology governance modes to match;
   fail closed to federated enforcement on a mismatch. Give the scheduler only the
   declared read/capacity/dependency/dispatch/efficiency allowlist, and forbid every
   control role from attaching to a project or holding a writer lease. Require
   exactly one live scheduler, runtime supervisor, and owner liaison with both their
   minimum authorities and maximum role allowlists. Reject control-plane authorities
   inside a project envelope, and reserve project-local decision, admission, and
   fresh-round authority for the live manifest owner alone. Every unfinished,
   non-frozen federated project requires that live writer owner and all three
   autonomy authorities in both manifest and owner task. Keep the stricter project
   authority-subset gate federated-only so legacy root mode remains compatible. Do
   not retain a persistent root controller. In legacy
   `root_controller` mode, Root owns portfolio admission, authority, priority, stop
   conditions, and major decisions but remains control-only. In either mode, project
   implementation must run in the independent project task.
   At every completed project stage, keep the writer in that project task and close
   `evidence -> test -> build -> diff -> readback -> commit -> push -> merge`. Record
   an exact source branch, target branch, commit SHA, remote readback, and merge
   readback. Mark build or merge `NOT_REQUIRED` only when the project contract proves
   that fact. On unknown identity, foreign dirty paths, conflict, or the first
   nonzero, stop once and mark every later step `UNEXECUTED`; never force push or
   force merge. A legacy Root may decide authority or conflicts but cannot perform
   the closeout; a federated project owner escalates only authority expansion or a
   real cross-project conflict through the owner liaison.
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
5. Dispatch long contracts that cover the authorized stage from preflight through
   implementation or diagnosis, decision-changing tests and build, diff/scope/secret
   checks, readback, commit, non-force push, fast-forward merge, and remote/target
   readback. Include exact task, host, root, branches, owned paths, authorities,
   preserved state, explicit stopping conditions, `NOT_REQUIRED` evidence, and final
   readback. Prefer this complete stage contract to serial half-step prompts. Use
   `PROJECT_TASK_CONTRACT_V2_4`; do not interpret permission to continue as deploy,
   release, credential, production-data, or destructive authority.
   Project writers may use project-controlled non-writing helpers for bounded
   diagnosis or evidence aggregation, but helpers cannot acquire a second writer
   lease or mutate the repository. Authorized mechanical, path, harness, and evidence
   issues stay inside the project/coordinator recovery loop. A first nonzero still
   ends the current formal round; the coordinator derives one materially different
   fresh round from retained evidence instead of abandoning the project or escalating
   routine failures.
   When a project's manifest and action contract both explicitly grant
   `routine_public_network`, its owner may autonomously retrieve public dependencies,
   consult public documentation, call read-only public APIs, fetch build resources,
   and run network diagnostics inside the existing project scope. Record one minimum
   envelope naming purpose, exact domains or URLs, write locations, no-credential
   boundary, frequency, expected evidence, and stop condition. Credentials or private
   data, production or real-user impact, destructive operations, publication or
   deployment, cross-host migration, material scope/dependency expansion,
   irreversible external writes, and major architecture direction remain owner gates.
   Routine network authority never relaxes host/root identity, frozen settings,
   writer or migration locks, first-nonzero behavior, secret checks, or publication
   controls. Older manifests remain valid but have no routine network authority unless
   they adopt the V2.4 policy and grant it per project.
   Default to delivery-first staging: finish core functionality, integration, and
   acceptance evidence before non-blocking deep security research. Record deferred
   research as an explicit pre-release gate. Never defer known critical/high defects,
   authentication or permission fail-closed checks, credential or destructive-data
   risks, necessary dependency/supply-chain checks, or publication controls.
6. Monitor deltas, not full transcripts. Classify approval, missing authority,
   host mismatch, harness failure, product failure, and external-state waiting as
   different outcomes. Project idle, a completed turn, or a first-nonzero terminal
   ends only that round, not the project objective. Promptly derive the next safe
   authorized action; use `WAITING` or `BLOCKED` only after authoritative proof that
   no safe action exists or a named external/manual event is required. Suppress
   half-step reports, unchanged status, queue reminders, and routine mechanical
   failures; send compact batched dispatch/terminal deltas instead. Escalate only
   genuine owner login/desktop/session work, credentials, external ownership choices,
   destructive or high-impact action, host migration, security/architecture direction,
   publication/release beyond current authority, or proven absence of a safe next
   action. Deduplicate context-renewal notifications by target and
   notification ID. Treat runtime idle as turn completion, not portfolio completion.
   Require each active `running` monitor to renew an evidence-backed work lease by
   admitting, dispatching, advancing ledger evidence, or recording a terminal result.
   A plan, timestamp, topology snapshot, or no-change counter is not work. One empty
   running check routes to attention; one empty waiting check prepares a pause.
   Before any pause, including `waiting`, deliver one deduplicated result or decision
   notice through the declared owner liaison, wait for its matching closure and
   delivery-turn readback, persist that delivery preceded the pause, and keep success
   notifications user-visible. A controller final alone is not delivery proof. If delivery
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
