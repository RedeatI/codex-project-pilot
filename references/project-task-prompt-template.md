# Project task prompt contract

Contract version: `PROJECT_TASK_CONTRACT_V2_6_TURBO`
Risk calibration: `FIVE_PROJECTS_SOL_RISK_CALIBRATION_V2_TURBO`

Use this high-velocity, risk-tiered contract for multi-project engineering execution.

---

## 1. PROJECT_TASK_CONTRACT_V2_6_TURBO (Active Standard)

```text
PROJECT_TASK_CONTRACT_V2_6_TURBO
PROJECT=<stable project id>
ACTION_ID=<fresh exact action id>
PROJECT_TASK_ID=<existing independent task id>
GOVERNANCE_MODE=FEDERATED_THIN_KERNEL
MODEL_ROLE=SOL_DECISION_CORE|TERRA_PRIMARY_WORKER|LUNA_LIGHT_WORKER
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
OUTCOME=MULTI_MODULE_CONTINUOUS_EPIC_DELIVERY (Sequentially implement, verify, and git-commit 3-5 core modules in this single continuous turn)
DELIVERY_PRIORITY=CORE_FUNCTION|INTEGRATION|ACCEPTANCE_CANDIDATE|PRE_RELEASE_SECURITY

TURBO_EXECUTION_CONTROLS
- FAST_TRACK_MODE=BUILD_ONLY_DURING_IMPL (Prohibit intermediate unit/integration tests during multi-file coding)
- VERIFICATION_AT_IMPL=SUB_SECOND_SYNTAX_TYPECHECK_ONLY (e.g. tsc --noEmit, py_compile, cargo check)
- MAX_ZERO_PROGRESS_RETRIES=1 (Zero-progress command retry limit)
- STUB_AND_BYPASS_TIMEOUT=1_ATTEMPT_MAX (Mock/stub unresolved non-core blockers into .agents/BLOCKERS.md)
- WARNING_POLICY=WHITELIST_IGNORE_OR_TRIAGE_ONCE
- BATCH_SLICING_MODE=DYNAMIC_RISK_TIERED (Low: 3-5 files; Medium: 1-2 files; High: 1 file instant check)
- PONYTAIL_ANTI_OVER_ENGINEERING=ENFORCED (1. YAGNI: no speculative abstractions/factories; 2. Codebase reuse & stdlib first; 3. Minimal viable diff; 4. Compact direct implementations over complex wrapper layers)
- CONTINUOUS_TURN_MARATHON=ENFORCED (Do NOT stop or conclude turn after one single file. Sequentially implement all planned modules in a continuous tool-calling loop)

WARNING_TRIAGE_RULES
- BLOCKING_BLACKLIST=[SecurityLeak, CompilerFatal, TypeCheckError, BrokenBuild, SchemaMismatch]
- NON_BLOCKING_WHITELIST=[DeprecationNotice, StyleWarning, MinorLinterHint, ThirdPartyCosmeticLog]
- UNCLASSIFIED_ACTION=SINGLE_PASS_READONLY_TRIAGE_THEN_PROCEED

FINAL_GOAL=<project goal from live manifest>
CURRENT_STAGE=<current goal stage>
NEXT_DELIVERABLE=<batch multi-module deliverable checklist (3-5 modules)>
ACCEPTANCE_EVIDENCE=<required evidence IDs/types>
AUTONOMOUS_DECISION_SCOPE=<implementation/test/build/mechanical/path/harness/small-project-architecture/local-git-closeout>
STOP_CONDITIONS=<first-nonzero/scope-writer/owner-gate/circuit-breaker>
OWNER_ONLY_EXCEPTIONS=<cross-project/major-architecture/authority/credential/production/migration/destructive>
NEXT_STAGE_TRIGGER=STAGE_TERMINAL_WITH_VALID_RECEIPT
ROLL_FORWARD_REQUIRED=TRUE
ORDINARY_RECOVERY_AUTONOMOUS=TRUE

ROLE_BOUNDARY
- In FEDERATED_THIN_KERNEL mode, this project owner performs project-local action
  selection, admission, recovery, verification, and closeout inside
  AUTHORITY_ENVELOPE. It does not wait for a portfolio root.
- The scheduler manages unblocked elastic multi-project wave dispatch only. It cannot
  grant authority, write this project, write the control ledger, migrate tasks, or
  override this task.
- This existing project task alone performs implementation, focused tests, build,
  repair, commit, non-force push, and fast-forward merge for this project.
- Do not create a substitute controller-owned worker, filler task, or second writer.
  Return material evidence deltas to runtime supervision. Route only authority
  expansion, cross-project conflicts, or owner-only actions through the liaison.

MANDATORY_OUTPUT_REQUIREMENT
Do NOT conclude the turn after editing a single file. Within this single turn, the agent MUST execute a continuous tool loop across all 3-5 target modules (edit -> typecheck -> git commit -> next module). Only after the entire batch is completed and committed, emit exactly one structured JSON object conforming to `TERMINAL_RECEIPT_V2_6`.
```

---

## 2. Ultra-Lean Micro-Directive (Turn-Level Dispatch)

For rapid turn execution without redundant token overhead:

```text
[TURBO_EPIC_CONTINUOUS_DIRECTIVE]
PROJECT: {{PROJECT_NAME}} | STAGE: {{STAGE_ID}} | RISK: {{RISK_LEVEL}}
TARGET: {{STAGE_DELIVERABLE_SUMMARY}}
PATHS: {{OWNED_PATHS}}
1. Ponytail Minimalist Rule: YAGNI! Reuse existing codebase & stdlib first. Zero redundant wrapper/factory bloat.
2. Continuous Marathon: Do NOT stop after 1 file. Sequentially implement all 3-5 planned modules in this single turn.
3. Fast Loop: For each module -> implement directly -> quick syntax/typecheck -> git commit -> proceed immediately to next module.
4. On non-core failure after 1 attempt, apply Stub & Bypass into .agents/BLOCKERS.md.
5. After all planned modules in the batch are committed, emit final TERMINAL_RECEIPT!
```

---

## 3. PROJECT_TASK_CONTRACT_V2_5 (Legacy Compatibility)

```text
PROJECT_TASK_CONTRACT_V2_5
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
CONTINUOUS_PROGRESS=AUTHORIZED|NOT_REQUIRED
INDEPENDENT_WHILE_BLOCKED=<feature|integration|test|documentation|performance|evidence|NONE>
NEXT_STAGE_SEED=<next authorized state-changing stage or evidence needed to derive it>
HEARTBEAT_HANDOFF=<terminal evidence IDs; blocker class; independent safe routes; next recompute trigger>
FINAL_GOAL=<project goal from live manifest>
CURRENT_STAGE=<current goal stage>
NEXT_DELIVERABLE=<smallest stage-complete deliverable>
ACCEPTANCE_EVIDENCE=<required evidence IDs/types>
AUTONOMOUS_DECISION_SCOPE=<implementation/test/build/mechanical/path/harness/small-project-architecture/local-git-closeout boundaries>
STOP_CONDITIONS=<first-nonzero/scope-writer/owner-gate/acceptance boundaries>
OWNER_ONLY_EXCEPTIONS=<cross-project/major-architecture/authority/credential/production/migration/destructive gates>
NEXT_STAGE_TRIGGER=STAGE_TERMINAL
ROLL_FORWARD_REQUIRED=TRUE
ORDINARY_RECOVERY_AUTONOMOUS=TRUE
GOAL_DIAGNOSIS_TRIGGER=NONE|goal_stalled|thread_idle|completed_empty_output
GOAL_RECOVERY_ACTION=NONE|RESUME_CURRENT_GOAL|AUTHORIZED_INDEPENDENT_PATH
OWNER_REQUEST_ID=<canonical stable request id or NONE>
```
