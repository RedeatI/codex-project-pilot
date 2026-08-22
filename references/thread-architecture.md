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
- manifest owner identity, project, host, root, and writer lease;
- provisional-task freeze state;
- migration controller, target, and lock consistency;
- tasks that reference projects absent from the manifest.

An audit failure is not permission to archive, delete, migrate, or rewrite the
manifest. Classify the finding, select one smallest safe correction, create a fresh
admission plan/readback when mutation is required, and preserve all unrelated task
state.
