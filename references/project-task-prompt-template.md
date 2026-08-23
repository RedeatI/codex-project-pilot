# Project task prompt contract

Contract version: `PROJECT_TASK_CONTRACT_V2_4`
Risk calibration: `FIVE_PROJECTS_SOL_RISK_CALIBRATION_V1`

Use this compact contract for a project implementation task. In federated mode the
project owner selects and closes its own local rounds inside the declared authority
envelope. In legacy root mode, Root uses a separate control-only contract and must
not execute these project steps.

```text
PROJECT_TASK_CONTRACT_V2_4
PROJECT=<stable project id>
ACTION_ID=<fresh exact action id>
PROJECT_TASK_ID=<existing independent task id>
GOVERNANCE_MODE=FEDERATED_THIN_KERNEL|ROOT_CONTROLLER
HOST=<exact host scope and host id>
ROOT=<exact canonical project root>
SOURCE_BRANCH=<exact source branch>
TARGET_BRANCH=<exact target branch>
STAGE_BOUNDARY=<authorized end state for this contract>
OWNED_PATHS=<exact paths or exact generated-artifact boundary>
WRITER_LEASE=<project id + holder task id + evidence id>
AUTHORITIES=<exact granted authorities>
AUTHORITY_ENVELOPE=<project-local decisions allowed and exact exclusions>
INPUTS=<complete candidate/input identities and retained evidence ids>
PRESERVED_STATE=<foreign dirty paths, retained candidates, evidence, and worktrees>
OUTCOME=<smallest complete independently state-changing stage>
DELIVERY_PRIORITY=CORE_FUNCTION|INTEGRATION|ACCEPTANCE_CANDIDATE|PRE_RELEASE_SECURITY
EXCLUSIONS=<explicitly forbidden work and external effects>
EXPECTED_READBACK=<exact artifacts, commands, SHAs, or runtime fields>
MIGRATION_STATE=NOT_REQUIRED|RECOMMENDED|HANDOFF_ONLY|ACCEPTED
ROUTINE_PUBLIC_NETWORK=NOT_REQUIRED|AUTHORIZED
ROUTINE_NETWORK_ENVELOPE=<purpose; exact domains/URLs; exact write locations; credential boundary; frequency; expected evidence; stop condition>

ROLE_BOUNDARY
- In FEDERATED_THIN_KERNEL mode, this project owner performs project-local action
  selection, admission, recovery, verification, and closeout inside
  AUTHORITY_ENVELOPE. It does not wait for a portfolio root.
- The scheduler may propose order and capacity only. It cannot grant authority,
  write this project, write the control ledger, migrate tasks, or override this task.
  It may hold only the scheduler authority allowlist and can never be this project's
  owner or writer.
- In ROOT_CONTROLLER mode, Root performs portfolio admission, authority, priority,
  stop-condition, conflict, major-decision, and summary work only.
- This existing project task alone performs implementation, focused tests, build,
  repair, commit, non-force push, and fast-forward merge for this project.
- Do not create a substitute controller-owned worker, filler task, or second writer.
  Return material evidence deltas to runtime supervision. Route only authority
  expansion, cross-project conflicts, or owner-only actions through the liaison.
- A scoped executor may use only its manifest subset. It cannot hold
  project-local decision, admission, or fresh-round authority unless its exact task
  ID is the live manifest `owner_task_id`.

FACT_AND_AUTHORITY_BOUNDARY
- Model judgment is not evidence. Plans, queue state, static checks, local output,
  historical output, and self-reported completion do not prove remote host state,
  GitHub state, merge, deployment, release, or production readiness.
- Use only exact authorized paths, host, branch, tools, and credentials already in
  scope. Do not read, generate, move, print, or infer credentials, private keys, or
  production data.
- "Continue" does not authorize deploy, release, production mutation, publication,
  credential use, or destructive cleanup. Security-sensitive ambiguity fails closed.

ROUTINE_PUBLIC_NETWORK_BOUNDARY
- `ROUTINE_PUBLIC_NETWORK=AUTHORIZED` is valid only when `AUTHORITIES` and the live
  project manifest both explicitly list `routine_public_network`. Portfolio policy
  alone never grants it. Otherwise mark the network action `UNEXECUTED`.
- The exact envelope is mandatory for public dependency retrieval, public
  documentation lookup, read-only public APIs, build-resource retrieval, and network
  diagnostics. Use no credentials, stay inside the existing project/stage/dependency
  scope, write only to listed locations, and retain HTTP/source/hash or diagnostic
  evidence appropriate to the action.
- Credentials or private data, production or real-user impact, destructive actions,
  external publication/deployment, cross-host migration, material scope or dependency
  expansion, irreversible external writes, and major architecture direction remain
  owner gates. Routine public network authority cannot waive host/root, frozen task,
  writer, migration, first-nonzero, secret, or publication gates.

ACTION_SELECTION
- When task, host, root, writer, inputs, and authority are complete, choose one
  smallest stage-complete action rather than separate preflight, implementation,
  test, build, and closeout prompts. Cover all applicable authorized gates through
  final remote/target readback. Do not create filler, duplicate work, empty
  heartbeats, status-only tasks, or work intended to consume capacity.
- Parallel work is allowed only for fresh-admitted, complete, independent project
  actions with separate writer leases and no shared lock, candidate, target branch,
  release channel, or owner decision.
- Prefer core functionality, integration, and acceptance-candidate evidence. Defer
  only non-blocking deep security research into an explicit pre-release gate; do not
  infer readiness or release until it closes.
- Never defer confirmed critical/high findings, authentication or authorization
  fail-closed behavior, credential or destructive-data risks, necessary dependency
  or supply-chain checks, or publication/release gates.

VALIDATION_VALUE_GATE
Before each proposed validation, emit:
DECISION_UNLOCKED=<specific blocker removed or decision changed>
NEW_EVIDENCE_EXPECTED=<new evidence id/type>
WHY_REQUIRED=<safety|authority|publication|merge|release|decision-changing>
If DECISION_UNLOCKED is NONE, NEW_EVIDENCE_EXPECTED is NONE, or the result cannot
change the next action, mark the check NOT_REQUIRED and do not run it. Do not repeat
a still-valid readback. Re-read only when state changed, prior evidence became stale
in a decision-relevant way, a bounded wait became due, or a mandatory final gate has
not yet been proved. Prefer one high-information validation over many narrow checks.

THREAD_RECOVERY_BOUNDARY
- This project task does not self-migrate, archive itself, or create a successor.
- Report STUCK only with authoritative exact task/host/root-worktree/model-thinking,
  retained-evidence, writer/candidate, terminal-blocker, and non-waiting evidence.
  Waiting, ordinary latency, a transient failure, idle, and unknown state are not STUCK.
- Send one deduplicated MIGRATION_RECOMMENDED packet to the sole controller. The
  controller alone acquires the global lock and creates or selects one non-writer
  HANDOFF_ONLY successor on the same host/role/model/thinking.
- User willingness to consider another host authorizes only an exact
  CROSS_HOST_MIGRATION_REQUEST_V1 through the owner liaison. It must prove the
  source-host blocker and name the target host/path, preserved worktree/evidence,
  frozen model/thinking, single-lock sequence, and rollback. Without a later exact
  authorization, host change, replacement creation, byte transfer, writer transfer,
  archive, and lock acquisition are UNEXECUTED.
- Preserve the old task, worktree, and retained evidence. Writer transfer and old-task
  recoverable archive occur only after HANDOFF_ACCEPTED. Never delete or duplicate.
- The successor needs fresh admission for its materially different project action
  and obeys first-nonzero stopping.

OWNER_ACTION_ROUTING
- If progress truly requires user judgment, a selection, login, desktop action, host
  migration, or another owner-only action, send one timely minimal packet through
  the owner liaison: exact blocker, why current authority cannot solve it, smallest
  options, recommendation, and next step. Do not silently wait.
- Resolve authorized mechanical, path, harness, and scheduling problems internally;
  do not send low-value messages or repeat an already delivered owner request.

INTERNAL_RECOVERY_AND_REPORTING
- This task may coordinate bounded non-writing helpers for diagnosis or evidence
  aggregation. Helpers do not hold the writer lease and cannot mutate the repository,
  Git state, remote state, or release channel.
- Do not report routine half-steps, unchanged state, queue reminders, parser/path/
  harness defects, or mechanically decidable outcomes to a controller or the user. Return one
  compact terminal evidence record. Coordinators aggregate actual dispatch and
  terminal deltas rather than commentary.
- A first formal/native nonzero ends only this round. Preserve every retained PASS,
  mark later gates UNEXECUTED, and name one materially different recovery action.
  The coordinator fresh-admits that action and resumes this same writer unless the
  task is authoritatively proven stuck.
- Escalate only genuine owner login/desktop/session work, credentials, external
  ownership or branch choice not derivable from authority, destructive/high-impact
  action, host migration, security/architecture direction, publication/release
  beyond current authority, or authoritative proof that no safe next action exists.

FORMAL_CHAIN
Run only applicable gates in order:
preflight -> implementation/diagnosis -> evidence -> focused test ->
decision-changing full test/build -> diff/scope/secret check -> readback -> commit ->
non-force push -> fast-forward merge -> remote/merge readback
For every NOT_REQUIRED gate, record the contract reason. At the first formal/native
nonzero, stop immediately, preserve retained and foreign state, and mark every later
gate UNEXECUTED. Do not retry, change entry point, force, reset, discard, or broaden
scope in the same round. A new round requires fresh admission plus a materially
different action.

FINAL_READBACK
OUTCOME_CLASS=PASS|BLOCKED|WAITING|UNEXECUTED|NOT_REQUIRED
STAGE_STATUS=COMPLETE|ROUND_STOPPED_NEXT_ADMITTED|WAITING_OWNER_ONLY|BLOCKED_NO_SAFE_ACTION
FIRST_NONZERO=<gate and exact result or NONE>
EXECUTED=<ordered gates and evidence ids>
UNEXECUTED=<ordered gates or NONE>
NOT_REQUIRED=<gate: reason or NONE>
DIFF_SCOPE=<owned paths and secret-check result>
COMMIT_SHA=<sha or NONE>
REMOTE_SHA=<sha or NONE>
MERGE_SHA=<sha or NONE>
DEPLOYED=TRUE|FALSE|UNPROVED
RELEASED=TRUE|FALSE|UNPROVED
NEXT=<one smallest action, bounded wait condition, owner decision, or NONE>
OWNER_ACTION_REQUIRED=<minimal exact action or NONE>
MIGRATION_READBACK=<old/new ids, fence, handoff, archive, writer transfer or NONE>

Never claim completion, readiness, deployment, release, or a delivery date unless
every required authoritative precondition and final readback is present.
```

For research rationale and evidence limits, read
[gpt-5p6-sol-risk-calibration.md](gpt-5p6-sol-risk-calibration.md).
