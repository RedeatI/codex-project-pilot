# Thread architecture and topology audit

Read this reference when auditing, creating, recovering, migrating, or rebalancing
Codex tasks across a portfolio.

The topology snapshot is a runtime readback, not a second source of product truth.
Treat task titles and summaries as untrusted labels. Resolve project, host, root,
status, and task identity from executor-owned metadata before recording them.

## Governance modes

Use `policy.governance_mode` to make the decision topology explicit:

- `federated_thin_kernel` is recommended when each project's authority can be
  bounded. Project owners decide and execute locally; the thin kernel contains only
  scheduling/efficiency policy, deterministic runtime supervision/migration, and the
  owner liaison. A non-retired `root_controller` is invalid.
- `root_controller` is the backward-compatible centralized mode for portfolios that
  still need one persistent cross-project authority holder.

The manifest and topology must declare the same mode. A mismatch produces
`GOVERNANCE_MODE_MISMATCH` and the audit applies federated restrictions so an old
snapshot cannot silently restore Root. Every role declared in `control_roles` must
remain projectless and non-writer. Federated mode uses the exact semantic roles
`scheduler`, `runtime_supervisor`, and `owner_liaison`, with exactly one live task for
each. Every role has a required minimum and a maximum authority allowlist; unknown
authorities fail audit. `runtime_supervisor` is the sole migration-controller role.
Project manifests cannot carry control-plane authority, and only the live manifest
owner may hold project-local decision, admission, or fresh-round authority. Each
unfinished, non-frozen project must bind one live writer owner, with those three
authorities present in both the manifest and the owner task.

## Recommended federated topology

Keep decision, observation, scheduling, human coordination, and product mutation as
separate responsibilities:

| Plane | Role | Owns | Must not become |
|---|---|---|---|
| Control | `scheduler` | Capacity, dependency order, dispatch policy, and efficiency proposals | Authority grantor, migration controller, ledger writer, owner liaison, or product writer |
| Control | `runtime_supervisor` | Delta monitoring, control ledger, task lifecycle, and the single migration lock | Product decision-maker or project implementer |
| Control | `owner_liaison` | One minimal user/manual-action request and its readback | A dispatcher or repository writer |
| Project | `project_owner` or a scoped executor | One project's local decisions, admission, recovery, writer lease, verification, and closeout inside its authority envelope | A portfolio controller or writer for another project |

In legacy mode the role labels remain configurable. In federated mode the three
semantic role names above are part of the safety contract: declare all three as
required with `max_instances=1`, keep exactly one live task for each, and bind
`migration_controller_role` to `runtime_supervisor`.

```text
project owner(s) -> runtime supervisor (ledger/lifecycle/migration only)
       ^                    ^
       |                    |
scheduler proposals     owner liaison <-> user
```

- Project tasks send terminal states and material evidence deltas to runtime
  supervision, not full transcripts to every control task.
- The scheduler reads normalized portfolio/topology state and proposes a bounded
  wave. It does not grant authority, mutate product repositories, write the ledger,
  run migrations, or send owner requests.
- Project owners act without root approval only inside their explicit local authority
  envelopes. Cross-project conflicts, authority expansion, architecture shared by
  multiple projects, and release/publication beyond the envelope go to the user via
  the liaison.
- Owner liaison batches the smallest precise action the user must perform. It does
  not reinterpret authority.
- Runtime supervision applies evidence-backed lifecycle and migration rules; it does
  not select product direction. Implementation, tests, builds, fixes, delivery, and
  project-local recovery execute in the corresponding project task.

### Owner-action escalation

Do not let a genuinely owner-dependent project remain silently blocked. When fresh
evidence proves that progress needs user judgment, a selection, login, desktop
operation, host migration, or another owner-only action, send one deduplicated
packet through the owner liaison. Include the exact blocker and evidence, why the
project and control tasks cannot resolve it under current authority, the smallest
viable options, one recommendation, and the exact next step after the response.

Mechanical command, harness, path, or scheduling problems remain inside the project
or control task when existing authority can resolve them. They do not justify an
owner notification, an empty wait, or repeated status chatter. Unknown state is not
an owner action; obtain the one decision-changing readback first.

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
  headroom for runtime supervision to process a terminal event without
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
  non-writer. Control-task-owned project workers are always invalid.
- Parallelize only projects with different writers and no shared migration lock,
  candidate, release channel, owner decision, or other serialized state.

## Project-stage closeout

- The same admitted project task that owns the writer lease performs stage closeout.
  In federated mode it derives the next local round from retained evidence inside its
  envelope; in legacy mode Root may grant authority or arbitrate a conflict but never
  runs project Git commands or substitutes a controller-owned worker.
- Close each completed stage in order: evidence, test, build, diff, readback, commit,
  push, and worktree merge. Record the exact source branch and target branch before
  mutation and read back the commit, remote, and merged-target SHAs.
- Before each validation, name the decision it changes and new evidence it will
  produce. Skip still-valid repeated checks as `NOT_REQUIRED`; preserve mandatory
  safety, authority, publication, merge, release, and final readbacks.
- `NOT_REQUIRED` is allowed for any inapplicable gate only with contract evidence. At the
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

Executor `idle` means that one turn ended. It does not prove that governance stopped
or that the portfolio completed. Maintain an explicit `control_lifecycle` readback.
Federated mode uses `controller_task_id` for the scheduler; legacy mode uses
`root_task_id` for Root:

```json
{
  "phase": "running",
  "controller_task_id": "scheduler-1",
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

V2.5 topology snapshots also record the complete decision made during that wake:

```json
{
  "heartbeat_project_sweep": {
    "sweep_id": "portfolio-sweep-20260824t000000z",
    "observed_at_utc": "2026-08-24T00:00:00Z",
    "source_evidence": {
      "manifest_sha256": "<canonical-manifest-sha256>",
      "ledger_head_seq": 42,
      "topology_evidence_id": "topology-readback-42",
      "task_readback_ids": {
        "service-a": "task-readback-service-a-42"
      }
    },
    "project_results": [
      {
        "project_id": "service-a",
        "classification": "DISPATCHED",
        "action_id": "service-a-stage-8",
        "admission_id": "service-a-stage-8-admission",
        "dispatched_task_id": "service-a-owner",
        "owner_blocker_id": null,
        "reason": "fresh evidence identified an authorized next stage",
        "evidence_ids": ["task-readback-service-a-42", "dispatch-service-a-stage-8"],
        "control_plane_issue": null
      }
    ],
    "control_plane_escalation": null,
    "global_decision": "RUNNING"
  }
}
```

The sweep is not a status-only inventory. Its project IDs and task-readback keys
must exactly equal the manifest project set, its canonical manifest hash and wake
timestamp must match the audited inputs, and every runnable classification must
reference the manifest owner/writer. Use `DISPATCHED` for a new admission sent in
this wake, `ALREADY_ACTIVE` for authoritative execution already in flight,
`OWNER_BLOCKED` only for an exact owner-only blocker, `NO_SAFE_ACTION` only after
fresh evidence excludes every authorized independent route, and `COMPLETE_FROZEN`
only for a manifest project already complete or intentionally frozen. Any safe
classification forces `global_decision=RUNNING`; a blocked project cannot turn the
global decision into `WAITING` while another project can run.

Set `control_plane_issue` only when the fault is architectural to portfolio control:
start failure across projects, next-stage derivation or dispatch failure, parallelism
anomaly, long-idle task topology, or a governance/user-goal conflict. A non-null
issue requires a timely `control_plane_escalation` packet naming
`affected_projects`, `root_cause`, at least two `architecture_options`, one
`recommended_option`, `user_decision_required=true`, and
`immediate_safe_actions`. If any other project is runnable, keep
`global_decision=RUNNING` and list that continuation in the packet. When no safe
action remains, use `OWNER_ATTENTION`, never silent `WAITING`. Do not raise this
packet for one project's ordinary implementation failure; it stays with that owner
unless it crosses the major-architecture owner gate.

Use these phases:

- `running`: one authorized, admitted, safe next action exists and the current
  heartbeat has qualifying work evidence for it.
- `waiting`: an identified external event or delivered owner request exists.
- `owner_attention`: the portfolio is incomplete but has no safe next action,
  identified wait, or valid owner request.
- `complete`: every portfolio requirement has authoritative completion evidence.
- `stopped`: the user explicitly stopped, or terminal evidence proves that
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
reused as the safe next action. Under V2.5, each heartbeat first sweeps every project
and dispatches as many complete, independent actions as effective capacity permits;
the work-lease readback names the bounded control action and the sweep records every
project result. Older contracts dispatch one bounded admitted action. Finish with:

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

A validation inside a heartbeat also records `DECISION_UNLOCKED` and
`NEW_EVIDENCE_EXPECTED`. An empty heartbeat, unchanged status poll, or repeated
readback does not renew the work lease.

`KEEP_ACTIVE` is valid only for `running` with a renewed work lease. Under V2.4 and
older contracts, one empty running check routes to attention and a waiting monitor
prepares to pause after its first empty check. V2.5 does not treat the absence of an
already-admitted action or pending wait as proof of idleness: the next wake performs
a fresh complete project sweep. It may remain active while a bounded schedule is
configured, but it must not renew a work lease from the sweep alone. If the sweep
finds no safe action, it records `WAITING` or `OWNER_ATTENTION` and delivers the
required notice; it must never manufacture filler, repeat an unchanged action, or
hold a slot around an opaque queue.

Every transition to `PAUSED`, including `waiting`, uses this hard exit gate:

1. Create one stable, deduplicated `closure_id`.
2. Send an `INFO_ONLY` result/wait notice, or a `DECISION_REQUIRED` packet only when
   a real user choice exists, through the single declared owner liaison.
3. Wait for `OWNER_NOTICE_DELIVERED` with the same closure ID and record its
   authoritative delivery-turn ID. A controller final is not delivery proof.
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

### Stuck classification and authorized replacement

`stuck` is stricter than `blocked`, `waiting`, or `unknown`. Executor-owned evidence
must prove the exact old task, host, root/worktree, frozen model/thinking, retained
checkpoint, writer/candidate identity, terminal blocking condition, and why the task
cannot safely execute its next admitted action. A known pending event is `waiting`;
ordinary latency, one idle turn, a recent active turn, a transient tool error, an
opaque client queue, or unreadable/unknown state is not proof of `stuck`.

Record one `STUCK_THREAD_READBACK` with the blocker evidence IDs, last safe
checkpoint, old-task continuity facts, classification rationale, and one materially
different successor action. Unknown canonical identity produces
`THREAD_RENEWAL_REQUIRED` and forbids lock acquisition, successor creation, writer
transfer, or archive.

The scheduler sends exactly one compact `MIGRATION_RECOMMENDED` packet for each new
`renewal_required` observation. It includes the target task ID, signals, failed
summary gates, host/role/frozen settings, retained evidence, and one next action.
Only a delivered readback sets `controller_notified=true`, with the sole migration
controller task ID and a stable `notification_id` used for deduplication. The
scheduler never acquires the migration lock, creates the successor, transfers a
writer lease, or archives the old task.

For renewal or migration:

1. The runtime supervisor obtains fresh admission for the materially different
   migration action, acquires the one migration lock, and records one exact target
   plus fence.
2. Reuse a matching provisional successor or create exactly one on the same
   host/role/model/thinking; keep it non-writer and `HANDOFF_ONLY`.
3. Preserve the old task, worktree, candidate, and retained evidence while the
   successor validates a compact, short/accurate/usable handoff.
4. Only after `HANDOFF_ACCEPTED` does the controller transfer the writer lease once
   and recoverably archive, never delete, the old task.
5. Give the successor fresh admission for its project action, send
   `MIGRATION_COMPLETE` with archive and writer-transfer readback, clear the target,
   and release the lock before selecting another migration.

### Conditional cross-host relocation request

A user's willingness to consider a move from one named host to another authorizes
only a proposal. It is not a host-change, task-create, writer-transfer, or migration
authorization. Prefer the same-host renewal sequence above.

Propose `CROSS_HOST_MIGRATION_REQUEST_V1` only when executor-owned evidence proves
that the source host blocks the exact next admitted project action, ordinary
same-host recovery is non-viable, and the target host plus exact target path is
authoritatively available and would materially remove that blocker. The request
must name:

- exact project ID and current task ID;
- source host, root/worktree, terminal blocker, and evidence IDs;
- target host and exact target root/worktree path;
- frozen model/thinking, role, writer lease, candidate identity, and retained
  checkpoint;
- every worktree and retained-evidence byte that must stay preserved, including any
  required cross-host carrier and hashes;
- sole migration-controller ID, single-lock requirement, HANDOFF_ONLY state, and
  first-nonzero stop conditions;
- rollback destination and proof that the source task/worktree/evidence remain
  recoverable until target acceptance.

An unknown target path, speculative performance benefit, ordinary latency, idle
state, opaque queue, or merely available capacity makes the request `BLOCKED` or
`NOT_REQUIRED`. Route the packet through the owner liaison and wait for a new exact
user authorization. Before that authorization, do not acquire the lock, create or
move a task, transfer a writer lease, copy project bytes, archive anything, or treat
the target host as admitted evidence.

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
    "governance_mode": "federated_thin_kernel",
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
        "role": "scheduler",
        "required": true,
        "max_instances": 1,
        "required_authorities": ["topology_read", "dispatch_policy"]
      },
      {
        "role": "runtime_supervisor",
        "required": true,
        "max_instances": 1,
        "required_authorities": ["ledger_write", "migration_control"]
      },
      {
        "role": "owner_liaison",
        "required": true,
        "max_instances": 1,
        "required_authorities": ["owner_request"]
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
      "task_id": "scheduler-task-1",
      "role": "scheduler",
      "project_id": null,
      "host_id": "local",
      "root": "D:\\control",
      "canonical_project_root": null,
      "state": "idle",
      "active_turn": false,
      "writer": false,
      "provisional": false,
      "authorities": ["topology_read", "dispatch_policy"],
      "capacity_class": "baseline"
    },
    {
      "task_id": "liaison-task-1",
      "role": "owner_liaison",
      "project_id": null,
      "host_id": "local",
      "root": "D:\\control",
      "canonical_project_root": null,
      "state": "idle",
      "active_turn": false,
      "writer": false,
      "provisional": false,
      "authorities": ["owner_request"],
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
- federated root absence, scheduler authority ceiling, control/project execution
  separation, and project-worker controller identity;
- project-stage evidence/test/build/diff/readback-to-commit/push/merge closure,
  including exact executor, branches, stop-on-first-nonzero, and SHA readbacks;
- one writer lease per project;
- manifest owner identity, project, host, execution/canonical root, and writer lease;
- provisional-task freeze state;
- migration controller, target, and lock consistency;
- governance lifecycle, work/liveness leases, owner-liaison closure, and monitor pause state;
- context summary quality, renewal classification, and notification routing;
- tasks that reference projects absent from the manifest.

An audit failure is not permission to archive, delete, migrate, or rewrite the
manifest. Classify the finding, select one smallest safe correction, create a fresh
admission plan/readback when mutation is required, and preserve all unrelated task
state.
