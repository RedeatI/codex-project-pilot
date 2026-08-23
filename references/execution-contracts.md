# Execution contracts and convergence

Read this reference before dispatching multi-project work, renewing tasks, crossing
hosts, or recovering from a failed formal round.

## Contract contents

A useful long contract identifies:

- project and action IDs;
- actual host, canonical root, and selected execution surface;
- role, ownership, and granted authorities;
- the authorized stage boundary, source and target branches, and exact owned paths;
- desired outcome and explicit exclusions;
- input or candidate identity and retained evidence;
- ordered preflight, mutation, verification, and conditional branches;
- first-nonzero stopping behavior;
- final readback fields and the next decision owner.

Do not copy a full transcript. A continuation handoff should retain only current
state and one unambiguous next action.

## Long-stage efficiency and internal recovery

When task, host, root, writer, inputs, and authority are already known, dispatch one
complete stage contract instead of separate preflight, implementation, test, build,
and closeout prompts. The contract may span `preflight -> implementation/diagnosis ->
focused tests -> decision-changing full tests/build -> diff/scope/secret -> readback ->
commit -> non-force push -> fast-forward merge -> remote/target readback`. A long
contract does not expand authority: any unauthorized gate remains `UNEXECUTED`, and
deploy, release, credentials, production data, destructive cleanup, or an alternate
target require their own exact authority.

State exact owned paths, branches, retained and foreign state, stop conditions, the
evidence that permits any `NOT_REQUIRED` gate, and the terminal readback before
dispatch. Project-controlled helpers may perform bounded read-only diagnosis or
evidence aggregation, but the existing project task retains the only writer lease and
all repository mutation.

Do not interrupt a portfolio controller or the user for ordinary path, harness,
parser, missing-tool, or
mechanically decidable failures. The first formal/native nonzero ends that round and
later gates are `UNEXECUTED`; it does not end the project objective. The coordinator
uses retained evidence to derive one materially different action ID and fresh
admission, then resumes the same writer unless authoritative evidence proves it is
stuck. Send compact batched dispatch and terminal deltas. Escalate only genuine login,
desktop or session recovery, credentials, external ownership or branch choices not
derivable from authority, destructive/high-impact work, host migration,
security/architecture direction, publication or release beyond current authority, or
authoritative proof that no safe next action exists.

## Routine public network envelope

`PROJECT_TASK_CONTRACT_V2_4` permits a project owner to use routine public networking
only when its manifest explicitly grants `routine_public_network`. This authority is
project-local and covers public dependency fetches, public documentation lookup,
read-only public APIs, build-resource fetches, and network diagnostics needed by the
already authorized stage. Before each such action, record one compact envelope with
the purpose, exact domains or URLs, exact write locations, credential boundary,
frequency, expected evidence, and stop condition. The credential boundary is `none`
for this authority; redirects or discovered resources outside the recorded scope
require a fresh envelope or the applicable owner gate.

Routine public networking does not authorize credentials or private data, production
or real-user impact, destructive operations, external publication or deployment,
cross-host migration, material scope or dependency expansion, irreversible external
writes, or major architecture direction. Those remain exact owner decisions. The
authority also does not relax host/root identity, frozen task settings, writer and
migration locks, first-nonzero semantics, secret checks, or publication readback.
Projects without the explicit authority record network work as `UNEXECUTED` and route
only the smallest needed authority request.

## Continuous project progress

Under a complete V2.4 autonomy block, stage completion triggers the same project
owner to plan and fresh-admit the next stage-complete long contract; it does not wait
for a portfolio root. If a single acceptance or external gate is temporarily blocked,
the owner preserves that gate as `BLOCKED`, leaves its dependent later gates
`UNEXECUTED`, and chooses only authorized work that does not depend on it: feature,
integration, test, documentation, performance, or evidence work that can materially
change project state.

Continuous progress is not permission to infer acceptance, rerun unchanged evidence,
create filler, duplicate work, bypass safety or authority, publish, deploy, use
credentials, or cross hosts. A project-controlled helper may perform an independent
bounded subtask only when effective capacity permits; it is counted as an execution
unit, stays within the owner's envelope, and cannot hold another writer lease. The
first formal/native nonzero still stops the current round, after which the owner may
fresh-admit only a materially different recovery or independent action.

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
- Before every dispatch wave, count visible active turns plus nested workers and
  subtract the declared control-slot reserve. Project-external tasks still consume
  host capacity. A zero budget forbids new dispatch; an unknown nested-worker count
  is treated conservatively as zero budget until authoritative readback.
- Use one controller and a fenced lock for task migrations or shared portfolio
  state. A successor must accept its compact handoff before the old task is
  archived.
- Monitor context pressure from authoritative runtime signals and the
  short/accurate/usable summary gate. When renewal is required, the scheduler sends
  one deduplicated recommendation to the sole migration controller; it does not
  create a successor or acquire the migration lock itself.
- Prefer bounded waits and delta snapshots. Do not wake tasks merely to ask for
  unchanged status.
- Give long-running monitors an explicit lifecycle, liveness lease, and work lease.
  `idle` is not terminal, but an active monitor must prove a current ledger delta
  tied to admission, dispatch, other evidence, or a terminal action in every
  running check. Plans,
  timestamps, topology refreshes, and no-change counters do not renew it. The first
  empty running check routes once to the owner liaison and pauses after delivery;
  the first empty waiting check also delivers an `INFO_ONLY` notice and obtains its
  matching delivery-turn readback before pausing. Any pause, completion, or explicit
  stop requires the same closure handshake and user-visible success notifications.
  A delivery failure forbids pausing; a later poll needs a fresh, bounded admission.
- Batch major questions. Ordinary command failures, harness defects, missing tools,
  and mechanically decidable outcomes remain terminal task records and feed the next
  materially different internal recovery round; do not emit half-step Root/user
  reports, empty heartbeats, unchanged queue reminders, or repeated readbacks.
- If fresh evidence proves progress needs user judgment, a choice, login, desktop
  action, host migration, or another owner-only action, send one timely packet
  through the owner liaison. Name the exact blocker, why current authority cannot
  resolve it, the smallest options, the recommendation, and the post-answer next
  step. Do not silently wait. Do not escalate mechanical, path, harness, or
  scheduling issues that the current tasks are authorized to resolve.
- Distinguish `waiting` from `blocked`. Waiting has a known external event or user
  action; blocked lacks authority or a viable next action.
- A harness-only failure cannot invalidate already verified product bytes. Preserve
  the candidate identity and repair the harness in a new round.

Control-plane threads should exchange compact state, not act as parallel project
writers. Project tasks report evidence deltas to runtime supervision; scheduling
uses that snapshot only to propose ordering, dependency, and capacity improvements;
the owner liaison carries the minimal human action request.

In `federated_thin_kernel` mode, the existing project owner selects, admits, recovers,
and closes project-local rounds inside its explicit manifest authority envelope.
There is no persistent root and the scheduler cannot expand that envelope. Authority
expansion, cross-project conflicts, and owner-only actions go through the liaison for
an exact user decision. Manifest and topology modes must match; any mismatch fails
closed to federated enforcement. A declared control role cannot attach to a project
or hold its writer lease. Federated mode requires exactly one live scheduler, runtime
supervisor, and owner liaison, each bounded by a minimum capability set and maximum
allowlist; runtime supervision is the sole migration-controller role. Project
envelopes cannot contain control-plane authority, and owner-only local governance
authorities cannot be delegated to a scoped executor. Every unfinished, non-frozen
project requires one live writer owner plus the three local-governance authorities
in both manifest and owner task. This authority-subset hard gate is federated-only;
legacy `root_controller` mode retains its previous compatibility behavior. In legacy
`root_controller` mode, Root contracts stop at
portfolio admission, authority, priority, stop conditions, and summary. In both
modes, every implementation, test, build, fix, or delivery contract targets the
existing project task that owns the admitted host/root/candidate and writer lease.
If that task is unavailable or identity cannot be proved, stop and route the blocker;
never move execution into a control task or controller-owned nested worker.

## Stuck-thread recovery contract

Recovery authorization applies only after executor-owned evidence classifies the
exact task as `stuck`. A known pending event is `waiting`; ordinary latency, a recent
active turn, one idle result, a transient tool error, or unreadable/unknown state is
not `stuck`. Unknown identity routes to `THREAD_RENEWAL_REQUIRED` without acquiring
the lock, creating a successor, or archiving anything.

The stuck readback names the canonical old task ID, host, root/worktree, frozen
model/thinking, writer and candidate identities, retained evidence checkpoint,
blocking condition, why the current task cannot safely execute its next admitted
action, and why the condition is not waiting or transient. The proposed successor
action must be materially different and obtain fresh admission `ZERO` with a valid
migration fence.

Only the sole migration controller performs the migration under the one global lock:

1. bind the lock to one exact old-task target and fence;
2. reuse an existing matching provisional successor or create exactly one on the
   same host/role/model/thinking, initially `HANDOFF_ONLY` and non-writer;
3. preserve the old task, worktree, candidate, and retained evidence while the
   successor checks a short/accurate/usable handoff;
4. after `HANDOFF_ACCEPTED`, transfer the single writer lease exactly once;
5. recoverably archive, never delete, the old task and record archive readback;
6. require fresh project-action admission for the successor, report
   `MIGRATION_COMPLETE`, then clear the target and release the lock.

Parallel, duplicate, or ambiguous successors remain frozen at `HANDOFF_ONLY` and are
converged serially. A first formal/native nonzero stops later migration gates as
`UNEXECUTED`; a new attempt requires a new round and materially different action.

### Cross-host migration request contract

Willingness to consider a named source-to-target host move permits only an exact
`CROSS_HOST_MIGRATION_REQUEST_V1`; it does not authorize execution. Same-host
continuation remains the default. The scheduler may propose the request only when
fresh executor evidence proves that the source-host blocker prevents the next
admitted project action, same-host recovery cannot remove it, and an authoritative
target host plus exact target path would materially change the decision.

The packet includes exact project/task, source host/root/worktree and blocker,
target host/path, frozen model/thinking and role, writer/candidate identities,
retained worktree/evidence and hashes, cross-host byte-carrier requirements, the sole
controller and single-lock sequence, HANDOFF_ONLY boundary, stop conditions, and a
rollback plan that preserves the source until target acceptance. Send it through the
owner liaison. Missing or speculative fields stop the request; they are not inferred.
Only a later exact user authorization may admit controller execution. Until then,
host change, replacement creation, byte transfer, archive, writer transfer, and lock
acquisition are `UNEXECUTED`.

## Validation-value gate

Before any validation, state the exact blocker it will remove or decision it will
change, the new evidence expected, and why that evidence is required. If the result
cannot alter the next action, merely repeats still-valid proof, or has no new evidence
target, record `NOT_REQUIRED` and skip it. Re-read only after a decision-relevant
state change, when evidence is stale in a way that affects routing, when a bounded
wait becomes due, or when a mandatory safety, authority, publication, merge, release,
or final readback remains unproved. Prefer one high-information validation to several
low-information checks. The dispatch-ready form is in
[project-task-prompt-template.md](project-task-prompt-template.md).

Model statements, plans, queue entries, static checks, local results, and historical
results are not proof of remote task state, GitHub state, merge, deployment, release,
or production readiness. Record only `PASS`, `BLOCKED`, `WAITING`, `UNEXECUTED`, or
`NOT_REQUIRED`, and never infer a launch date from incomplete evidence.

## Delivery-first security staging

When selecting among admitted project actions, prioritize core feature completion,
integration, and acceptance-candidate evidence. Non-blocking deep security research
may be scheduled as one explicit pre-release gate after the candidate exists; it is
deferred, not waived, and readiness remains unproved until that gate closes.

Do not defer a confirmed critical/high defect, authentication or authorization
fail-closed behavior, credential exposure, destructive-data risk, a dependency or
supply-chain check required to build or trust the candidate, or any publication and
release authority gate. A focus-project priority applies only inside the effective
dispatch budget and never bypasses fresh admission, exact host/root/task-worktree
identity, unique writer lease, shared-state serialization, or first-nonzero stopping.

## Capacity expansion contract

A request to raise portfolio concurrency changes only the configured policy ceiling.
It cannot override a smaller runtime hard limit. Persist both values and compute the
effective ceiling as their minimum; when no authoritative runtime number exists,
record it as unknown rather than inventing a guarantee.

Capacity beyond the previous baseline is admitted one effective project action at a
time. Before dispatch, prove complete input, a non-empty action ID, fresh admission
`ZERO`, the exact independent project task, and its writer lease. Then apply the same
host, migration, authority, shared-state, and first-nonzero gates used at baseline.
Control work, nested helpers, duplicate actions, empty tasks, and synthetic capacity
tests are not valid surge work. Do not create filler tasks merely to demonstrate that
the configured number is reachable.

## Stage closeout contract

When the necessary authorities are complete, include closeout in the original stage
contract rather than waiting for a separate series of half-step prompts. The project
task runs one formal chain: `preflight -> implementation/diagnosis -> evidence ->
focused test -> decision-changing full test/build -> diff/scope/secret check ->
readback -> commit -> non-force push -> fast-forward merge -> remote/merge readback`.
Declare the exact project task, host, root, source branch, target branch, owned paths,
writer lease, preserved foreign/retained state, and whether a worktree merge is
required before mutation. Any gate may be `NOT_REQUIRED` only when the contract names
the still-valid evidence and explains why the result cannot change the decision.

At the first nonzero, stop immediately and mark later steps `UNEXECUTED`. Unknown
task/host/branch identity, foreign or unowned dirty paths, and merge conflicts are
stop conditions. Do not change entry points, force push, force merge, discard retained
  state, or let a control task complete the chain. A successful closeout records the commit SHA,
remote SHA readback, and target-branch merge SHA; only then may the stage be reported
complete and its writer lease released.

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
