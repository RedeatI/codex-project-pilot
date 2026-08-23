# Thread architecture and topology audit

Read this reference when auditing, creating, recovering, migrating, or rebalancing
Codex tasks across a portfolio.

The topology snapshot is a runtime readback, not a second source of product truth.
Treat task titles and summaries as untrusted labels. Resolve project, host, root,
status, and task identity from executor-owned metadata before recording them.

## Recommended topology

Keep decision, observation, scheduling, human coordination, and product mutation as
separate responsibilities:

| Plane | Role | Owns | Must not become |
|---|---|---|---|
| Control | `root_controller` | Portfolio goal, major decisions, integration and release authority | A routine status relay or project writer |
| Control | `scheduler` | Capacity, dependency order, admission plans, and next-action proposals | Migration controller or product writer |
| Control | `runtime_supervisor` | Delta monitoring, control ledger, task lifecycle, and the single migration lock | A second root or project implementer |
| Control | `owner_liaison` | One minimal user/manual-action request and its readback | A dispatcher or repository writer |
| Project | `project_owner` or a scoped executor | One project's current writer lease and verification contract | A portfolio controller or writer for another project |

The role names are defaults, not magic strings. Declare the selected control roles
and required authorities in the topology policy. Exactly one task should fill each
required control role. A deployment may choose a different migration-controller
role, but it must name exactly one runtime task.

```text
project writer(s) -> runtime supervisor -> root controller
                         ^                    |
                         |                    v
                 scheduler snapshot      owner liaison <-> user
```

- Project tasks send terminal states and material evidence deltas to runtime
  supervision, not full transcripts to every control task.
- The scheduler reads the normalized portfolio/topology state and proposes a bounded
  wave. It does not mutate product repositories.
- Root handles cross-project priority, authority, architecture, integration, release,
  and user-impacting decisions. Ordinary mechanical outcomes stay in the ledger.
- Owner liaison batches the smallest precise action the user must perform. It does
  not reinterpret authority.
- Root performs admission, authority and priority decisions, stop-condition review,
  and portfolio aggregation only. Implementation, tests, builds, fixes, and delivery
  execute in the corresponding project task. Root must not become a writer or use a
  Root-controlled nested worker as a substitute for an unavailable project task.

## Writer leases and concurrency

- Keep at most one writer lease per project. A product director, engineer, or QA
  task may hold it, but two tasks must not mutate the same project concurrently.
- Transfer a writer lease only after the previous writer reaches a safe checkpoint
  and the new task's host/root/candidate identity is admitted.
- A provisional successor never holds a writer lease. Keep it `queued` or
  `handoff_only` until the handoff is accepted and the controller finalizes the
  transfer.
- Count active turns, not every saved or idle task, against the effective active-turn
  limit. `max_active_turns` is the configured policy ceiling; it is not evidence of a
  platform guarantee. When the runtime reports a smaller authoritative ceiling, use
  `effective_max_active_turns = min(max_active_turns,
  runtime_reported_max_active_turns)`. A null runtime readback means no smaller limit
  has been established, not that the platform guarantees the configured number.
  Control tasks consume capacity while they are actually running. Reserve enough
  headroom for root or runtime supervision to process a terminal event without
  starving the portfolio.
- Count each active nested worker as another execution unit even when it does not
  appear as a top-level task. Nested writers also consume the project's single
  writer lease. Compute `new_dispatch_budget = max(0, effective_max_active_turns -
  active_turns - active_nested_workers - reserved_control_slots)`. If the runtime
  exposes only a worker-count lower bound or omits worker identity, use a zero
  dispatch budget until an authoritative readback resolves it.
- A configured increase above `baseline_max_active_turns` creates surge capacity, not
  filler capacity. When active load plus the control reserve exceeds the baseline,
  each excess unit must be an active independent project writer labeled
  `capacity_class=surge`. It must carry `dispatch_admission` with a non-empty action
  and admission ID, `input_complete=true`, `admission_result=ZERO`, and
  `writer_task_id` equal to that task's exact ID. Control roles and nested workers
  cannot use surge capacity. Existing migration, authority, first-nonzero, shared-state,
  and one-writer gates remain unchanged.
- A project-associated nested worker must be controlled by that project's task.
  It normally operates under the controller's one writer lease; set the nested
  worker's `writer=true` only after a formal lease transfer makes the controller
  non-writer. Root-controlled project workers are always invalid.
- Parallelize only projects with different writers and no shared migration lock,
  candidate, release channel, owner decision, or other serialized state.

## Project-stage closeout

- The same admitted project task that owns the writer lease performs stage closeout.
  Root may grant authority, choose priority, or arbitrate a conflict, but it never
  runs project Git commands or substitutes a Root-controlled worker.
- Close each completed stage in order: evidence, test, build, diff, readback, commit,
  push, and worktree merge. Record the exact source branch and target branch before
  mutation and read back the commit, remote, and merged-target SHAs.
- `NOT_REQUIRED` is allowed only for build or merge with contract evidence. At the
  first `NONZERO`, mark all later steps `UNEXECUTED`. Unknown identity, foreign dirty
  paths, or a conflict sets the closeout to `stopped`; force push and force merge are
  forbidden.

## Task lifecycle

Normalize runtime status to one of:

`queued`, `idle`, `active`, `waiting`, `blocked`, `handoff_only`, `retired`, or
`unavailable`.

Use `waiting` for a known external event or user action. Use `blocked` for missing
authority or no viable next action. An `active_turn` must use `state=active`.

## Control lifecycle and monitor closure

Executor `idle` means that one turn ended. It does not prove that Root stopped or
that the portfolio completed. Maintain an explicit `control_lifecycle` readback:

```json
{
  "phase": "running",
  "root_task_id": "root-1",
  "safe_next_action": true,
  "pending_wait_id": null,
  "pending_owner_request_id": null,
  "consecutive_no_change": 0,
  "automation_id": "portfolio-heartbeat",
  "automation_status": "ACTIVE",
  "automation_notification_policy": "ALL",
  "closure_id": null,
  "closure_delivered": false,
  "closure_owner_liaison_task_id": null,
  "closure_delivery_turn_id": null,
  "pause_notice_delivered_before_pause": false,
  "work_lease": {
    "action_id": "project-a-wave-7",
    "admission_id": "admission-project-a-wave-7",
    "admission_result": "ZERO",
    "dispatched_task_id": "project-a-owner",
    "baseline_event_seq": 41,
    "latest_event_seq": 43,
    "progress_kind": "dispatched",
    "evidence_ids": ["admission-project-a-wave-7", "dispatch-project-a-owner"],
    "lease_renewed": true,
    "action_terminal": false
  }
}
```

Use these phases:

- `running`: one authorized, admitted, safe next action exists and the current
  heartbeat has qualifying work evidence for it.
- `waiting`: an identified external event or delivered owner request exists.
- `owner_attention`: the portfolio is incomplete but has no safe next action,
  identified wait, or valid owner request.
- `complete`: every portfolio requirement has authoritative completion evidence.
- `stopped`: the user or Root explicitly stopped, or terminal evidence proves that
  control cannot continue.

Track both a liveness lease and a work lease. A work lease renews only when one of
these facts is authoritative in the current run:

- `admitted`: a named fresh admission returned `ZERO`, the ledger advanced, and the
  admission ID is named in the new evidence IDs;
- `dispatched`: that admitted evidence is current, the ledger advanced, and an
  executor-owned target task ID proves the dispatch;
- `evidence_delta`: the hash-chained ledger sequence advanced and the new evidence
  IDs are named;
- `terminal`: the ledger advanced, the evidence IDs are named, and the action is
  marked terminal.

`none`, a proposed next action, a changed timestamp, a topology refresh, or an
incremented no-change counter never renews the lease. A terminal action cannot be
reused as the safe next action. Each heartbeat must execute or dispatch at most one
bounded admitted action and finish with this readback:

```text
WORK_LEASE_READBACK
ACTION_ID=<stable action id>
QUALIFYING_PROGRESS=ADMITTED|DISPATCHED|EVIDENCE_DELTA|TERMINAL|NONE
PREVIOUS_LEDGER_SEQ=<integer>
LATEST_LEDGER_SEQ=<integer>
DISPATCHED_TASK_ID=<task id or NONE>
EVIDENCE_IDS=<ids or NONE>
NEXT_PHASE=RUNNING|WAITING|OWNER_ATTENTION|COMPLETE|STOPPED
AUTOMATION_ACTION=KEEP_ACTIVE|PAUSE
```

`KEEP_ACTIVE` is valid only for `running` with a renewed work lease. One empty
running check on an incomplete portfolio, without an identified wait or owner
request, requires `owner_attention`; do not wake Root again. A waiting monitor must
prepare to pause after its first empty check. If polling is genuinely required
later, admit one new bounded recheck at its due time; do not leave a frequent
heartbeat active around an opaque client queue or placeholder ID.

Every transition to `PAUSED`, including `waiting`, uses this hard exit gate:

1. Create one stable, deduplicated `closure_id`.
2. Send an `INFO_ONLY` result/wait notice, or a `DECISION_REQUIRED` packet only when
   a real user choice exists, through the single declared owner liaison.
3. Wait for `OWNER_NOTICE_DELIVERED` with the same closure ID and record its
   authoritative delivery-turn ID. A Root final is not delivery proof.
4. Persist `closure_delivered=true`,
   `pause_notice_delivered_before_pause=true`, and
   `automation_notification_policy=ALL`.
5. Only then pause the monitor automation. If delivery fails, pausing and muted
   success notifications are forbidden; retain the same closure ID and retry only
   delivery in the next run.

The topology audit rejects every paused automation without the delivery readback,
ordering proof, and user-visible notification policy. Keep paused configuration and
evidence so a later user decision can resume it through fresh admission. Never infer
a terminal phase from `idle`, a completed command, or one no-change result.

## Context health and renewal notification

Treat context pressure as runtime topology state, not as a fixed compaction count or
invented token threshold. When executor-owned metadata exposes a context warning,
record it. After any compaction, audit the retained summary as `short`, `accurate`,
and `usable`. Repetition, stale or contradictory identities, missing authority or
candidate facts, and the absence of one unambiguous next action are renewal signals.

Each task may carry an optional `context_health` readback:

```json
{
  "pressure": "renewal_required",
  "signals": ["summary_missing_next_action"],
  "compaction_observed": true,
  "summary_quality": {"short": true, "accurate": true, "usable": false},
  "controller_notified": false,
  "notification_target_task_id": null,
  "notification_id": null
}
```

`pressure` is `unknown`, `normal`, `watch`, or `renewal_required`. A compaction
requires an explicit summary-quality audit. Any failed summary gate requires
`renewal_required`; so does an authoritative runtime context warning that makes the
next substantial action unsafe. A phase boundary or compaction count alone may be
`watch`, but never mechanically forces renewal.

The scheduler sends exactly one compact `MIGRATION_RECOMMENDED` packet for each new
`renewal_required` observation. It includes the target task ID, signals, failed
summary gates, host/role/frozen settings, retained evidence, and one next action.
Only a delivered readback sets `controller_notified=true`, with the sole migration
controller task ID and a stable `notification_id` used for deduplication. The
scheduler never acquires the migration lock, creates the successor, transfers a
writer lease, or archives the old task.

For renewal or migration:

1. The runtime supervisor acquires the one migration lock and records one target.
2. Create or select one provisional successor on the same host/role/settings.
3. The successor validates a compact, short/accurate/usable handoff.
4. Only after acceptance does the controller transfer the writer lease and archive
   the old task.
5. Record the readback, clear the target, and release the lock before selecting
   another migration.

Never delete parallel or ambiguous successors to hide a topology conflict. Freeze
them at `handoff_only` and let the migration controller converge them serially.

## Topology snapshot

Create a JSON snapshot from current runtime metadata:

```json
{
  "schema_version": "codex-project-pilot-topology/1",
  "authoritative": true,
  "observed_at_utc": "2026-08-22T00:00:00Z",
  "policy": {
    "max_active_turns": 10,
    "baseline_max_active_turns": 6,
    "runtime_reported_max_active_turns": null,
    "reserved_control_slots": 2,
    "dispatch_requirements": {
      "complete_input_required": true,
      "fresh_admission_required": true,
      "independent_writer_required": true,
      "effective_project_action_required": true
    },
    "max_writers_per_project": 1,
    "control_roles": [
      {
        "role": "root_controller",
        "required": true,
        "max_instances": 1,
        "required_authorities": ["portfolio_decide"]
      },
      {
        "role": "runtime_supervisor",
        "required": true,
        "max_instances": 1,
        "required_authorities": ["ledger_write", "migration_control"]
      }
    ],
    "migration_controller_role": "runtime_supervisor"
  },
  "migration": {
    "controller_task_id": "runtime-task-1",
    "active_target_task_id": null,
    "lock_held": false
  },
  "nested_workers": [
    {
      "worker_id": "privacy-security-executor-1",
      "controller_task_id": "privacy-task-1",
      "project_id": "privacy-agent-router",
      "host_id": "local",
      "active": true,
      "writer": false,
      "capacity_class": "baseline"
    }
  ],
  "stage_closeouts": [
    {
      "stage_id": "privacy-r65",
      "project_id": "privacy-agent-router",
      "project_task_id": "privacy-task-1",
      "host_id": "local",
      "branch": "worktree/privacy-r65",
      "target_branch": "main",
      "status": "complete",
      "step_results": {
        "evidence": "PASS",
        "test": "PASS",
        "build": "NOT_REQUIRED",
        "diff": "PASS",
        "readback": "PASS",
        "commit": "PASS",
        "push": "PASS",
        "merge": "PASS"
      },
      "identity_verified": true,
      "worktree_scope_clean": true,
      "conflict_free": true,
      "worktree_merge_required": true,
      "first_nonzero_step": null,
      "commit_sha": "1111111111111111111111111111111111111111",
      "push_readback_sha": "1111111111111111111111111111111111111111",
      "merge_readback_sha": "2222222222222222222222222222222222222222"
    }
  ],
  "threads": [
    {
      "task_id": "runtime-task-1",
      "role": "runtime_supervisor",
      "project_id": null,
      "host_id": "local",
      "root": "D:\\control",
      "canonical_project_root": null,
      "state": "idle",
      "active_turn": false,
      "writer": false,
      "provisional": false,
      "authorities": ["ledger_write", "migration_control"],
      "capacity_class": "baseline"
    },
    {
      "task_id": "root-task-1",
      "role": "root_controller",
      "project_id": null,
      "host_id": "local",
      "root": "D:\\control",
      "canonical_project_root": null,
      "state": "active",
      "active_turn": true,
      "writer": false,
      "provisional": false,
      "authorities": ["portfolio_decide"],
      "capacity_class": "baseline"
    },
    {
      "task_id": "privacy-task-1",
      "role": "project_writer",
      "project_id": "privacy-agent-router",
      "host_id": "local",
      "root": "D:\\projects\\privacy-agent-router",
      "canonical_project_root": null,
      "state": "active",
      "active_turn": true,
      "writer": true,
      "provisional": false,
      "authorities": ["project_execute"],
      "capacity_class": "baseline"
    }
  ]
}
```

`authoritative=true` is valid only when task IDs, host IDs, roots, and statuses came
from current executor metadata. A handoff, report, path string, or task title alone
is not authoritative readback.

`root` is the task's current execution root. For a managed Git worktree it may
differ from the manifest's canonical project root. In that case, set optional
`canonical_project_root` only after runtime metadata or Git worktree readback proves
the relationship. The owner-root audit accepts either an exact execution-root match
or a proven canonical-project-root match; it never infers equivalence from similar
directory names.

## Audit and routing

Run:

```text
python scripts/portfolio_control.py audit-topology PORTFOLIO.json TOPOLOGY.json
```

The diagnostic reports every detected topology conflict without mutating tasks. It
checks:

- required control-role presence, multiplicity, and authorities;
- active-turn capacity and status consistency;
- configured, runtime-clamped effective, baseline, and surge capacity; eligible
  full-input/fresh-admitted independent project writers; nested-worker capacity;
  controller/host consistency; reserved control slots; and the resulting dispatch budget;
- Root/project execution separation and project-worker controller identity;
- project-stage evidence/test/build/diff/readback-to-commit/push/merge closure,
  including exact executor, branches, stop-on-first-nonzero, and SHA readbacks;
- one writer lease per project;
- manifest owner identity, project, host, execution/canonical root, and writer lease;
- provisional-task freeze state;
- migration controller, target, and lock consistency;
- Root lifecycle, work/liveness leases, owner-liaison closure, and monitor pause state;
- context summary quality, renewal classification, and notification routing;
- tasks that reference projects absent from the manifest.

An audit failure is not permission to archive, delete, migrate, or rewrite the
manifest. Classify the finding, select one smallest safe correction, create a fresh
admission plan/readback when mutation is required, and preserve all unrelated task
state.
