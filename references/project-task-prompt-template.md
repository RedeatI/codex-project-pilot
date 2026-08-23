# Project task prompt contract

Contract version: `PROJECT_TASK_CONTRACT_V2_1`
Risk calibration: `FIVE_PROJECTS_SOL_RISK_CALIBRATION_V1`

Use this compact contract for a project implementation task. Root uses a separate
control-only contract and must not execute these project steps.

```text
PROJECT_TASK_CONTRACT_V2_1
PROJECT=<stable project id>
ACTION_ID=<fresh exact action id>
PROJECT_TASK_ID=<existing independent task id>
HOST=<exact host scope and host id>
ROOT=<exact canonical project root>
SOURCE_BRANCH=<exact source branch>
TARGET_BRANCH=<exact target branch>
WRITER_LEASE=<project id + holder task id + evidence id>
AUTHORITIES=<exact granted authorities>
INPUTS=<complete candidate/input identities and retained evidence ids>
OUTCOME=<smallest independently state-changing result>
DELIVERY_PRIORITY=CORE_FUNCTION|INTEGRATION|ACCEPTANCE_CANDIDATE|PRE_RELEASE_SECURITY
EXCLUSIONS=<explicitly forbidden work and external effects>
EXPECTED_READBACK=<exact artifacts, commands, SHAs, or runtime fields>

ROLE_BOUNDARY
- Root performs admission, authority, priority, stop-condition, conflict, major
  decision, and summary work only.
- This existing project task alone performs implementation, focused tests, build,
  repair, commit, non-force push, and fast-forward merge for this project.
- Do not create a substitute task, Root-controlled worker, filler task, or second
  writer. Return evidence deltas and genuine major decisions to Root.

FACT_AND_AUTHORITY_BOUNDARY
- Model judgment is not evidence. Plans, queue state, static checks, local output,
  historical output, and self-reported completion do not prove remote host state,
  GitHub state, merge, deployment, release, or production readiness.
- Use only exact authorized paths, host, branch, tools, and credentials already in
  scope. Do not read, generate, move, print, or infer credentials, private keys, or
  production data.
- "Continue" does not authorize deploy, release, production mutation, publication,
  credential use, or destructive cleanup. Security-sensitive ambiguity fails closed.

ACTION_SELECTION
- Choose one smallest action that can change project state. Do not create filler,
  duplicate work, empty heartbeats, status-only tasks, or work intended to consume
  capacity.
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

FORMAL_CHAIN
Run only applicable gates in order:
evidence -> focused test -> build -> diff/scope/secret check -> readback -> commit ->
non-force push -> fast-forward merge -> remote/merge readback
For every NOT_REQUIRED gate, record the contract reason. At the first formal/native
nonzero, stop immediately, preserve retained and foreign state, and mark every later
gate UNEXECUTED. Do not retry, change entry point, force, reset, discard, or broaden
scope in the same round. A new round requires fresh admission plus a materially
different action.

FINAL_READBACK
OUTCOME_CLASS=PASS|BLOCKED|WAITING|UNEXECUTED|NOT_REQUIRED
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

Never claim completion, readiness, deployment, release, or a delivery date unless
every required authoritative precondition and final readback is present.
```

For research rationale and evidence limits, read
[gpt-5p6-sol-risk-calibration.md](gpt-5p6-sol-risk-calibration.md).
