# Execution contracts and convergence

Read this reference before dispatching multi-project work, renewing tasks, crossing
hosts, or recovering from a failed formal round.

## Contract contents

A useful long contract identifies:

- project and action IDs;
- actual host, canonical root, and selected execution surface;
- role, ownership, and granted authorities;
- desired outcome and explicit exclusions;
- input or candidate identity and retained evidence;
- ordered preflight, mutation, verification, and conditional branches;
- first-nonzero stopping behavior;
- final readback fields and the next decision owner.

Do not copy a full transcript. A continuation handoff should retain only current
state and one unambiguous next action.

## Admission

Create a plan and runtime readback before risky work. The bundled `admit` command
checks these fields in order:

1. required input shape;
2. authoritative runtime readback;
3. project identity;
4. host scope and identity;
5. canonical root identity;
6. required authorities;
7. frozen-lane compatibility;
8. explicit authorization for external mutation;
9. continuation transport without model or effort overrides;
10. migration fence when required.

The first failed check is `NONZERO`; later checks are `UNEXECUTED`.

The plan and authoritative readback are JSON objects. A minimal admission pair is:

```json
{
  "project_id": "service-a",
  "action_id": "publish-1",
  "action_class": "repo_write",
  "expected_host_scope": "remote",
  "expected_host_id": "build-host-a",
  "expected_root": "/srv/service-a",
  "required_authorities": ["repo_write"],
  "portfolio_lane_state": "ready",
  "external_mutation": true,
  "user_authorized": true,
  "continuation": false,
  "transport_model_override_present": false,
  "transport_effort_override_present": false,
  "migration_fence_required": false
}
```

```json
{
  "project_id": "service-a",
  "authoritative": true,
  "observed_host_scope": "remote",
  "observed_host_id": "build-host-a",
  "observed_root": "/srv/service-a",
  "granted_authorities": ["repo_write"]
}
```

Set `authoritative` only from executor-owned runtime evidence. When
`migration_fence_required` is true, the readback also needs a
`migration_fence` object with non-empty `controller_task_id` and `fence_token`.

## Progress routing

- Audit the current runtime topology before a dispatch wave that creates, resumes,
  migrates, or changes a task's writer role. Use the topology audit described in
  [thread-architecture.md](thread-architecture.md).
- Parallelize only independent projects with separate writers and no shared lock,
  candidate, release channel, or owner decision.
- Use one controller and a fenced lock for task migrations or shared portfolio
  state. A successor must accept its compact handoff before the old task is
  archived.
- Monitor context pressure from authoritative runtime signals and the
  short/accurate/usable summary gate. When renewal is required, the scheduler sends
  one deduplicated recommendation to the sole migration controller; it does not
  create a successor or acquire the migration lock itself.
- Prefer bounded waits and delta snapshots. Do not wake tasks merely to ask for
  unchanged status.
- Give long-running monitors an explicit lifecycle and liveness lease. `idle` is not
  terminal. Repeated no-change without an identified wait or owner request routes
  once to the owner liaison, then pauses the monitor after delivery. Completion or
  an explicit stop follows the same closure handshake.
- Batch major questions. Ordinary command failures, harness defects, missing tools,
  and mechanically decidable outcomes should remain terminal task records.
- Distinguish `waiting` from `blocked`. Waiting has a known external event or user
  action; blocked lacks authority or a viable next action.
- A harness-only failure cannot invalidate already verified product bytes. Preserve
  the candidate identity and repair the harness in a new round.

Control-plane threads should exchange compact state, not act as parallel project
writers. Project tasks report evidence deltas to runtime supervision; scheduling
uses that snapshot to propose admissions; root decides only portfolio-level matters;
owner liaison carries the minimal human action request.

## Completion audit

Translate the portfolio goal into explicit requirements. For each requirement,
name the authoritative source that would prove it and inspect that source. Missing,
indirect, stale, or self-reported evidence is not completion.

Append material changes to the ledger: dispatch, admission result, external write,
candidate seal, terminal outcome, task renewal, and final completion decision.

A new event file uses `codex-project-pilot-event/1` and includes non-empty
`event_id`, `event_time_utc`, `portfolio_id`, `project_id`, `action_id`,
`event_type`, and `actor` strings plus a JSON-object `payload`. The append command
adds `seq`, `prev_event_hash`, and `event_hash`. For an empty ledger, pass
`--expected-seq -1` and 64 lowercase zeroes as `--expected-prev-hash`; for later
events, use the previous verified ledger readback.
