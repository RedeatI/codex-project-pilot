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

## Writer leases and concurrency

- Keep at most one writer lease per project. A product director, engineer, or QA
  task may hold it, but two tasks must not mutate the same project concurrently.
- Transfer a writer lease only after the previous writer reaches a safe checkpoint
  and the new task's host/root/candidate identity is admitted.
- A provisional successor never holds a writer lease. Keep it `queued` or
  `handoff_only` until the handoff is accepted and the controller finalizes the
  transfer.
- Count active turns, not every saved or idle task, against `max_active_turns`.
  Control tasks consume capacity while they are actually running. Reserve enough
  headroom for root or runtime supervision to process a terminal event without
  starving the portfolio.
- Parallelize only projects with different writers and no shared migration lock,
  candidate, release channel, owner decision, or other serialized state.

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
  "phase": "owner_attention",
  "root_task_id": "root-1",
  "safe_next_action": false,
  "pending_wait_id": null,
  "pending_owner_request_id": "closure-1",
  "consecutive_no_change": 3,
  "automation_id": "portfolio-heartbeat",
  "automation_status": "PAUSED",
  "closure_id": "closure-1",
  "closure_delivered": true,
  "closure_owner_liaison_task_id": "liaison-1"
}
```

Use these phases:

- `running`: one authorized, admitted, safe next action exists.
- `waiting`: an identified external event or delivered owner request exists.
- `owner_attention`: the portfolio is incomplete but has no safe next action,
  identified wait, or valid owner request.
- `complete`: every portfolio requirement has authoritative completion evidence.
- `stopped`: the user or Root explicitly stopped, or terminal evidence proves that
  control cannot continue.

Track a liveness lease with the no-change streak and pending IDs. Two consecutive
no-change runs on an incomplete portfolio, without an identified wait or owner
request, require `owner_attention`; do not wake Root forever. For
`owner_attention`, `complete`, or `stopped`, send exactly one deduplicated closure
packet to the declared owner liaison. After delivery, pause the monitor automation.
Keep its configuration and evidence so a later user decision can resume it through
fresh admission. Never infer a terminal phase from `idle`, a completed command, or
one no-change result.

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
    "max_active_turns": 6,
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
      "authorities": ["ledger_write", "migration_control"]
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
- one writer lease per project;
- manifest owner identity, project, host, execution/canonical root, and writer lease;
- provisional-task freeze state;
- migration controller, target, and lock consistency;
- Root lifecycle, liveness lease, owner-liaison closure, and monitor pause state;
- context summary quality, renewal classification, and notification routing;
- tasks that reference projects absent from the manifest.

An audit failure is not permission to archive, delete, migrate, or rewrite the
manifest. Classify the finding, select one smallest safe correction, create a fresh
admission plan/readback when mutation is required, and preserve all unrelated task
state.
