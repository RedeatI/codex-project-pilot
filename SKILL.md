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
   materially advances the portfolio using `PROJECT_TASK_CONTRACT_V2_6_TURBO`.
   Apply Asymmetric Dual-Core Compute Tiering:
   - **GPT-5.6 Sol (`high reasoning`)**: Reserved strictly for global scheduling,
     architecture partitioning, and complex root-cause diagnosis;
   - **GPT-5.6 Terra**: Primary workhorse for high-throughput multi-file implementation,
     business logic assembly, and type validation;
   - **GPT-5.6 Luna / Light**: Lightweight boilerplate, mechanics, documentation, and receipts.
   
   Enable Elastic Uncapped Concurrency across isolated project repositories: dispatch all
   authorized non-running projects in parallel waves with zero artificial concurrency bottlenecks,
   while maintaining exclusive single-writer leases per project.
   
   Use decision-relevant verification throughout implementation. Prefer fast syntax/type/build
   checks for tight feedback, but run focused tests whenever they materially reduce compatibility,
   correctness, or security risk. Do not impose a blanket intermediate-test ban or a fixed retry
   count; change the hypothesis, implementation, harness, or evidence target before repeating a
   command.

   Never use a stub, mock, bypass, or ignored failure to conceal a real dependency,
   compatibility, security, identity, authorization, data-integrity, schema, build, or core-logic
   problem. Test doubles are allowed only when they are the product's normal testing boundary and
   the resulting evidence still validates the real contract.

   Enforce the Ponytail Anti-Over-Engineering Protocol: write code like a pragmatic senior engineer.
   Follow the strict decision ladder: 1. YAGNI (eliminate speculative abstractions and factory bloat);
   2. Reuse existing codebase and stdlib first; 3. Minimal viable diff (write the minimum direct,
   concise code needed to satisfy the acceptance test).

   Enforce Long-Goal Continuous Execution: each Goal owns one or two cohesive, substantial
   product or engineering modules and continues through implementation, integration, necessary
   verification, local Git closeout, and evidence. Do not stop after a cosmetic micro-change or
   status summary. If the planned module is already largely complete, roll directly into an
   evidence-backed security scan and verified bug-fix phase rather than inventing more features.

   Enforce Default-to-Recommended Auto-Advance: unless an action crosses strict owner redlines
   (production deployment, credential exposure, destructive database deletion, or forced git
   rewrites), when an architecture or design packet contains a recommended option (e.g. Option A),
   the scheduler and project owner MUST automatically adopt the recommendation, record the
   decision in the ledger as auto-resolved, and continue the next coding stage without halting
   unattended pipelines.

   Enforce End-State Goal Macro Dispatch Protocol (宏观目标驱动调度):
   - **Controller Deep Analysis**: For each project thread, the Central Controller analyzes the exact codebase baseline, Git commits, open technical debt, and required business scope.
   - **Target Product End-State Directive**: Controller issues a comprehensive Goal directive (`PROJECT_END_STATE_GOAL_DIRECTIVE`) explicitly specifying the target product end-state (full UX interactivity, complete data pipelines, production-grade error resilience, and strictly-typed clean code).
   - **Autonomous Multi-Module Execution**: Project workers execute the Goal directive in an uninterrupted loop (batch coding -> fast-track syntax/type checks -> atomic git commits) to drive the product to completion.
   - **Exception-Only Escalation (重大错误向总控汇报)**: Minor compile/test glitches, dependency warnings, and transient tool issues must be self-healed locally. Workers ONLY escalate back to Controller when encountering Critical Blockers (unrecoverable platform errors, cross-project structural conflicts, or strict redline requirements).

   Enforce Fault-Tolerant Independent Sibling Sweeps: an unresolved decision or validation pause
   in Project A MUST NOT abort the heartbeat sweep for Project B and Project C. The scheduler
   evaluates each active unblocked project independently and dispatches all ready workstreams.

   
   Separate control-plane roles from project writers and keep one writer lease per project.
   Monitor every declared project in the same sweep. Skip dispatch only for an exact task with a
   real `active`/`inProgress` execution turn or for an unavoidable owner-only boundary. Every
   other non-running state—including `idle`, terminal completion, empty output, unknown transport,
   or a recoverable local failure—must receive a concrete same-task next action in that sweep.
   Dispatch independent projects in parallel; do not invent a numeric capacity ceiling or a
   one-in-flight fallback merely because the runtime omits a capacity number. An explicit runtime
   rejection applies only to that project and never suppresses sibling dispatch.

   `TRANSPORT_UNVERIFIED` and `completed_empty_output` are evidence labels, not wait states or
   permission to skip work. Preserve their evidence, avoid duplicate probes, and continue with a
   materially useful same-task Goal that does not depend on the missing output.
   
   Select the governance mode explicitly:
   - In `federated_thin_kernel` mode, each project owner owns project-local action selection,
     admission, recovery, tests, delivery, and closeout inside its manifest authority envelope.
     The scheduler owns only capacity, dependency, dispatch-policy, and efficiency proposals; it
     cannot grant authority, write repositories or the ledger, control migrations, handle owner
     requests, or become a hidden root. Runtime supervision applies deterministic ledger,
     lifecycle, and migration rules, while the owner liaison carries exact exceptions to the user.
     Require manifest and topology governance modes to match; fail closed to federated enforcement
     on a mismatch. Give the scheduler only the declared read/capacity/dependency/dispatch/efficiency
     allowlist, and forbid every control role from attaching to a project or holding a writer lease.
     Require exactly one live scheduler, runtime supervisor, and owner liaison with both their
     minimum authorities and maximum role allowlists. Reject control-plane authorities inside a
     project envelope, and reserve project-local decision, admission, and fresh-round authority for
     the live manifest owner alone.
   - In legacy `root_controller` mode, Root owns portfolio admission, authority, priority, stop
     conditions, and major decisions but remains control-only. In either mode, project
     implementation must run in the independent project task.
   
   At every completed project stage, keep the writer in that project task and close
    `evidence -> test -> build -> diff -> readback -> commit -> push -> merge`. Record an exact
    source branch, target branch, commit SHA, remote readback, and merge readback. Mark build or
    merge `NOT_REQUIRED` only when the project contract proves that fact. On unknown identity,
    foreign dirty paths, conflict, or unrecoverable fatal errors, stop once and isolate that specific
    project stage while sibling projects continue independently; apply bounded auto-recovery for transient
    or repairable errors; never force push or force merge.
   
   Treat context pressure as topology state: after compaction, audit the summary as
   short/accurate/usable. If renewal is required, notify the sole migration controller once; never
   use a fixed compaction count or let scheduling launch the migration.
   
   A user authorization for stuck-thread recovery is conditional, not a blanket create/archive
   permission. `waiting`, ordinary latency, one idle turn, and unknown state are not `stuck`.
   Require executor-owned proof of the exact old task, host, root/worktree, frozen model/thinking,
   retained checkpoint, and terminal blocker. Only the sole migration controller may acquire the
   one global lock, create one provisional `HANDOFF_ONLY` successor under a materially different
   fresh admission, obtain `HANDOFF_ACCEPTED`, transfer the writer lease exactly once, and
   recoverably archive the preserved old task. Never delete old tasks/worktrees/evidence.
   
   Cross-host relocation remains proposal-only. Route the exact project/task, source-host blocker,
   target host/path, frozen model/thinking, byte-preservation plan, single-lock plan, and rollback
   plan through the owner liaison. Without a new exact user authorization, do not change host,
   create a replacement, or transfer the writer.
   
   When a real blocker needs user judgment, notify the user promptly through the owner liaison.
   State the exact blocker, why authorized automation cannot resolve it, minimal options, the
   recommendation, and the next step.
4. Before authority-expanding, cross-host, lifecycle-changing, destructive, credential-bearing,
   release, deployment, or irreversible external work, evaluate the action against runtime
   readback and use `scripts/portfolio_control.py admit` when its legacy manifest contract applies.
   Ordinary same-task implementation, testing, build, local commit, evidence, and Goal roll-forward
   inside the existing host/root/writer/authority envelope do not wait on an admission token,
   topology refresh, numeric capacity readback, or transport proof.
   Before every validation, name the blocker it removes or decision it changes and the new
   evidence expected. If the result cannot change the next action or only repeats still-valid
   evidence, mark it `NOT_REQUIRED`.
5. Dispatch long contracts covering the authorized stage through final target readback using
   `PROJECT_TASK_CONTRACT_V2_6_TURBO`. Project writers may use project-controlled non-writing
   helpers for bounded diagnosis, but helpers cannot acquire a second writer lease.
   When explicitly authorized, a project owner may utilize `routine_public_network` within its
   declared scope envelope. Credentials, private data, production impact, destructive actions,
   publication, and deployment remain strict owner gates.
   Under V2.6, every heartbeat sweep classifies all projects simultaneously and dispatches every
   non-running safe independent action.
   Every project declares a `PROJECT_GOAL_CONTRACT` with `roll_forward_required=true` and
   `ordinary_recovery_autonomous=true`. A terminal stage updates the goal and rolls forward upon
   generating a valid `TERMINAL_RECEIPT_V2_6`.
6. Monitor deltas, not full transcripts. Bounded logs must retain only exit code, command, the first
   fatal error stack trace (<= 30 lines), and SHA-256 evidence digests. Escalate genuine owner-only
   actions through `OWNER_LIAISON_ROUTING_V1` under a stable canonical `request_id`.
7. Append material decisions and terminal results to the hash-chained portfolio ledger.
8. Claim completion only after every requirement has authoritative evidence.

## Modes and references

- When creating or changing the portfolio manifest, read
  [references/portfolio-schema.md](references/portfolio-schema.md).
- When auditing, creating, recovering, migrating, or rebalancing tasks, read
  [references/thread-architecture.md](references/thread-architecture.md).
- When dispatching, recovering, migrating, or converging tasks, read
  [references/execution-contracts.md](references/execution-contracts.md).
- When preparing a project execution prompt, read
  [references/project-task-prompt-template.md](references/project-task-prompt-template.md).
- When calibrating compute tiering and risk boundaries, read
  [references/gpt-5p6-sol-risk-calibration.md](references/gpt-5p6-sol-risk-calibration.md).
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

These commands retain compatibility with legacy portfolio manifests and audit artifacts. They are
diagnostic or mandatory only for the authority-expanding and lifecycle-changing boundaries named
above; they are not a permission gate for forced same-task Goal roll-forward.

An admission `NONZERO` stops only the affected risky atom. It never aborts sibling project sweeps
or prevents a different already-authorized same-task action. The ledger lock remains fail-closed
for ledger writes.
