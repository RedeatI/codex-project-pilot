# Project task prompt contract

Contract version: `PROJECT_TASK_CONTRACT_V2_6_TURBO`
Risk calibration: `FIVE_PROJECTS_SOL_RISK_CALIBRATION_V2_TURBO`

Use this high-velocity, risk-tiered contract for multi-project engineering execution.

---

## 1. PROJECT_END_STATE_GOAL_DIRECTIVE (Primary Macro Standard)

```text
[PROJECT_END_STATE_GOAL_DIRECTIVE]
PROJECT: {{PROJECT_NAME}} (ID: {{PROJECT_ID}})
HOST: {{HOST_ID}} | ROOT: {{PROJECT_ROOT}}
CURRENT_GIT_BASELINE: HEAD={{CURRENT_GIT_HEAD}} | STATUS={{CLEAN_OR_DIRTY}}

【CONTROLLER CONTEXT ANALYSIS】
{{CONTROLLER_DETAILED_ANALYSIS_OF_CURRENT_STATE_AND_GAPS}}

【TARGET PRODUCT END-STATE】
{{EXPLICIT_SPECIFICATION_OF_FINISHED_PRODUCT_FORM_AND_CAPABILITIES}}

【AUTONOMOUS MULTI-MODULE EXECUTION DIRECTIVES】
1. Ponytail Anti-Over-Engineering: YAGNI! Reuse existing codebase and stdlib first. Minimal viable diffs.
2. Long-Goal Continuous Execution: Complete one or two cohesive, substantial modules end to end; do not stop after a cosmetic single-file edit or a status summary.
3. Evidence-Driven Verification: Use fast syntax/type/build checks for feedback and run focused tests whenever they materially reduce correctness, compatibility, data-integrity, or security risk. Finish with the decisive focused/full gates required by acceptance.
4. Exception-Only Escalation: Resolve ordinary code, dependency, and harness problems locally without hiding them behind mocks or stubs. Escalate only unrecoverable system faults, architecture deadlocks, or credential/security/owner-only boundaries.
5. Terminal Delivery: On reaching the defined product end-state, run stage closeout verification and produce structured TERMINAL_RECEIPT_V2_6.
```

---

## 2. PROJECT_TASK_CONTRACT_V2_6_TURBO (Detailed Specification)


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
OUTCOME=LONG_GOAL_CONTINUOUS_DELIVERY (Implement, integrate, verify, and locally close out 1-2 cohesive substantial modules)
DELIVERY_PRIORITY=CORE_FUNCTION|INTEGRATION|ACCEPTANCE_CANDIDATE|PRE_RELEASE_SECURITY

TURBO_EXECUTION_CONTROLS
- VERIFICATION_MODE=DECISION_RELEVANT (fast syntax/type/build feedback plus focused tests whenever risk or evidence requires them)
- RETRY_MODE=HYPOTHESIS_DRIVEN (no fixed retry limit; change hypothesis, implementation, harness, environment, or evidence target before repeating)
- REAL_DEPENDENCY_POLICY=NO_CONCEALMENT (never hide real dependency, compatibility, security, identity, authorization, data-integrity, schema, build, or core-logic failures behind mocks/stubs/bypasses)
- WARNING_POLICY=WHITELIST_IGNORE_OR_TRIAGE_ONCE
- BATCH_SLICING_MODE=DYNAMIC_RISK_TIERED (Low: 3-5 files; Medium: 1-2 files; High: 1 file instant check)
- PONYTAIL_ANTI_OVER_ENGINEERING=ENFORCED (1. YAGNI: no speculative abstractions/factories; 2. Codebase reuse & stdlib first; 3. Minimal viable diff; 4. Compact direct implementations over complex wrapper layers)
- CONTINUOUS_LONG_GOAL=ENFORCED (Do not stop after a cosmetic micro-change; complete the 1-2 substantial modules and their decisive evidence)

WARNING_TRIAGE_RULES
- BLOCKING_BLACKLIST=[SecurityLeak, CompilerFatal, TypeCheckError, BrokenBuild, SchemaMismatch]
- NON_BLOCKING_WHITELIST=[DeprecationNotice, StyleWarning, MinorLinterHint, ThirdPartyCosmeticLog]
- UNCLASSIFIED_ACTION=SINGLE_PASS_READONLY_TRIAGE_THEN_PROCEED

FINAL_GOAL=<project goal from live manifest>
CURRENT_STAGE=<current goal stage>
NEXT_DELIVERABLE=<one or two cohesive substantial modules with end-to-end acceptance>
ACCEPTANCE_EVIDENCE=<required evidence IDs/types>
AUTONOMOUS_DECISION_SCOPE=<implementation/test/build/mechanical/path/harness/small-project-architecture/local-git-closeout>
STOP_CONDITIONS=<scope-writer/owner-gate/unrecoverable-safety-boundary>
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
Do NOT conclude the turn after a cosmetic single-file edit or status summary. Continue through implementation, integration, decision-relevant verification, local Git closeout, and evidence for the one or two substantial target modules. Only after the Goal is terminal, emit exactly one structured JSON object conforming to `TERMINAL_RECEIPT_V2_6`.
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
2. Long Goal: Complete one or two cohesive substantial modules; do not stop at a cosmetic micro-change.
3. Evidence Loop: Implement -> quick syntax/type/build feedback -> focused tests when decision-relevant -> integrate -> local closeout.
4. Diagnose and fix real failures; never conceal them with a mock, stub, bypass, or fabricated receipt.
5. After the Goal and its decisive acceptance evidence are complete, emit final TERMINAL_RECEIPT!
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
STOP_CONDITIONS=<scope-writer/owner-gate/unrecoverable-safety/acceptance boundaries>
OWNER_ONLY_EXCEPTIONS=<cross-project/major-architecture/authority/credential/production/migration/destructive gates>
NEXT_STAGE_TRIGGER=STAGE_TERMINAL
ROLL_FORWARD_REQUIRED=TRUE
ORDINARY_RECOVERY_AUTONOMOUS=TRUE
GOAL_DIAGNOSIS_TRIGGER=NONE|goal_stalled|thread_idle|completed_empty_output
GOAL_RECOVERY_ACTION=NONE|RESUME_CURRENT_GOAL|AUTHORIZED_INDEPENDENT_PATH
OWNER_REQUEST_ID=<canonical stable request id or NONE>
```
