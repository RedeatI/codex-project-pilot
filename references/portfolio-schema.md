# Portfolio manifest

Read this reference when creating or updating a portfolio manifest.

Store the manifest in a user-selected control directory, normally as
`portfolio.json`. Do not place secrets, tokens, private keys, environment values,
or production data in it.

```json
{
  "schema_version": "codex-project-pilot/1",
  "portfolio_id": "acme-products",
  "goal": "Ship the authorized portfolio outcomes with verified evidence.",
  "policy": {
    "governance_mode": "federated_thin_kernel",
    "max_parallel_projects": 3,
    "default_repo_visibility": "private",
    "external_mutations_require_user_authorization": true,
    "project_owner_autonomy": {
      "contract_version": "PROJECT_TASK_CONTRACT_V2_5",
      "routine_public_network": {
        "authority": "routine_public_network",
        "allowed_categories": [
          "public_dependency_fetch",
          "public_documentation_lookup",
          "read_only_public_api",
          "build_resource_fetch",
          "network_diagnostic"
        ],
        "minimum_envelope_fields": [
          "purpose",
          "domains_or_urls",
          "write_locations",
          "credential_boundary",
          "frequency",
          "expected_evidence",
          "stop_condition"
        ],
        "credentials_allowed": false
      },
      "continuous_progress": {
        "enabled": true,
        "next_stage_long_contract_required": true,
        "fresh_admission_required": true,
        "independent_work_categories": [
          "feature",
          "integration",
          "test",
          "documentation",
          "performance",
          "evidence"
        ],
        "blocked_gate_state_preserved": true,
        "acceptance_inference_forbidden": true,
        "safety_authority_publication_gates_preserved": true,
        "filler_or_duplicate_work_forbidden": true,
        "project_controlled_helpers_allowed": true,
        "helpers_count_toward_capacity": true,
        "helpers_cannot_hold_writer_lease": true
      },
      "heartbeat_project_sweep": {
        "enabled": true,
        "evaluate_every_manifest_project": true,
        "fresh_sources_required": true,
        "existing_action_or_pending_wait_not_required": true,
        "auto_form_minimum_envelope": true,
        "auto_fresh_admit": true,
        "auto_dispatch": true,
        "recompute_after_terminal": true,
        "blocked_project_does_not_pause_portfolio": true,
        "global_wait_only_when_no_safe_action": true,
        "project_goal_contract_required": true,
        "stage_terminal_roll_forward_required": true,
        "missing_goal_cannot_force_global_waiting": true,
        "single_project_blocker_cannot_force_global_waiting": true,
        "classifications": [
          "DISPATCHED",
          "ALREADY_ACTIVE",
          "OWNER_BLOCKED",
          "NO_SAFE_ACTION",
          "COMPLETE_FROZEN"
        ],
        "minimum_envelope_fields": [
          "project_id",
          "action_id",
          "owner_task_id",
          "host_id",
          "root",
          "scope",
          "writer_lease",
          "authorities",
          "expected_evidence",
          "stop_condition",
          "next_handoff"
        ],
        "control_plane_escalation": {
          "enabled": true,
          "trigger_categories": [
            "MULTI_PROJECT_START_FAILURE",
            "HEARTBEAT_NEXT_STAGE_DERIVATION_FAILURE",
            "HEARTBEAT_DISPATCH_FAILURE",
            "PARALLELISM_ANOMALY",
            "TASKS_LONG_IDLE",
            "GOVERNANCE_GOAL_CONFLICT"
          ],
          "notification_fields": [
            "affected_projects",
            "root_cause",
            "architecture_options",
            "recommended_option",
            "user_decision_required",
            "immediate_safe_actions"
          ],
          "continue_other_projects": true,
          "ordinary_single_project_failure_is_project_local": true,
          "major_project_architecture_remains_owner_gate": true
        }
      },
      "owner_gate_categories": [
        "credential_or_private_data",
        "production_or_real_user_impact",
        "destructive_operation",
        "external_publication_or_deployment",
        "cross_host_migration",
        "material_scope_or_dependency_expansion",
        "irreversible_external_write",
        "major_architecture_direction"
      ],
      "first_nonzero_stops_round": true,
      "fresh_round_requires_material_difference": true
    }
  },
  "projects": [
    {
      "id": "service-a",
      "name": "Service A",
      "host_scope": "remote",
      "host_id": "build-host-a",
      "root": "/srv/service-a",
      "owner_task_id": null,
      "authorities": ["control_read", "repo_read"],
      "state": "ready",
      "desired_outcome": "Publish a private GitHub mirror",
      "goal_contract": {
        "final_goal": "Publish the authorized private mirror with remote readback.",
        "current_stage": "implementation",
        "next_deliverable": "verified repository candidate",
        "acceptance_evidence": ["focused-tests", "remote-main-readback"],
        "autonomous_decision_scope": [
          "implementation",
          "test",
          "build",
          "mechanical_recovery",
          "path_recovery",
          "harness_recovery",
          "small_project_architecture",
          "local_git_closeout"
        ],
        "stop_conditions": [
          "first_formal_or_native_nonzero",
          "scope_or_writer_conflict",
          "owner_only_exception",
          "acceptance_complete"
        ],
        "owner_only_exceptions": [
          "cross_project_conflict",
          "major_architecture",
          "authority_escalation",
          "credential_or_private_data",
          "production_release_or_deployment",
          "cross_host_migration",
          "destructive_or_irreversible_external_write"
        ],
        "next_stage_trigger": "STAGE_TERMINAL",
        "roll_forward_required": true,
        "ordinary_recovery_autonomous": true
      },
      "repository": {
        "provider": "github",
        "full_name": null,
        "visibility": "private",
        "uploaded": false
      }
    }
  ]
}
```

## Required invariants

- `schema_version` is exactly `codex-project-pilot/1`.
- `governance_mode` is `federated_thin_kernel` for project autonomy with no
  persistent root, or `root_controller` for the legacy centralized control model.
  If omitted by an older manifest/topology, audit behavior remains
  `root_controller` for compatibility. The manifest and authoritative topology must
  declare the same mode. A mismatch is an audit failure and is enforced as
  `federated_thin_kernel` so a stale topology cannot restore Root authority.
- `portfolio_id`, `goal`, project `id`, `name`, `host_id`, `root`, and
  `desired_outcome` are non-empty strings.
- Project IDs are unique and stable across task renewal or repository relocation.
- `host_scope` is `local` or `remote`; `host_id` identifies the actual executor,
  not a display label inferred from a path.
- `state` is one of `frozen`, `ready`, `active`, `waiting`, `blocked`, or
  `complete`.
- Authorities are explicit strings. Absence means no authority.
- `project_owner_autonomy` is optional so manifests written before V2.4 remain
  valid. A project that uses routine public networking must explicitly include
  `routine_public_network` in its own `authorities`; that grant is invalid unless
  the policy contains a valid V2.4 or V2.5 autonomy block.
  Each network action also records the minimum envelope fields. The portfolio-level
  policy never grants the authority to every project implicitly.
- Routine public networking is limited to public dependency retrieval, public
  documentation lookup, read-only public APIs, build-resource retrieval, and network
  diagnosis inside the project's existing scope. Its envelope names purpose, exact
  domains or URLs, write locations, the no-credential boundary, frequency, expected
  evidence, and stop condition. Credentials or private data, production or real-user
  impact, destructive operations, publication/deployment, cross-host migration,
  material scope or dependency expansion, irreversible external writes, and major
  architecture direction remain owner gates.
- The V2.4/V2.5 `continuous_progress` block requires the same project owner to plan and
  fresh-admit the next long-stage contract after a stage completes. When one
  acceptance or external gate is blocked, it selects authorized work that does not
  depend on that gate from the exact feature, integration, test, documentation,
  performance, and evidence categories. The blocked gate remains `BLOCKED` and its
  later gates remain `UNEXECUTED`; continuous progress never fabricates acceptance
  or bypasses safety, authority, publication, host, root, writer, or migration gates.
  Repeated no-value work and filler are forbidden. Project-controlled helpers are
  allowed only inside effective capacity and cannot hold a second writer lease.
- V2.5 adds `heartbeat_project_sweep`. Every automation wake derives current task,
  ledger, and topology evidence for every manifest project, then classifies each
  exactly once as `DISPATCHED`, `ALREADY_ACTIVE`, `OWNER_BLOCKED`, `NO_SAFE_ACTION`,
  or `COMPLETE_FROZEN`. An existing fresh admission or pending wait is not a
  prerequisite: when current authority permits a state-changing next stage, the
  scheduler forms the minimum envelope, fresh-admits it, and dispatches the unique
  owner/writer within effective capacity. A terminal stage triggers immediate
  recomputation. One blocked or waiting project never pauses the others. Global
  `WAITING` is valid only when the complete sweep proves no safe action; when a true
  owner-only blocker is the last remaining route, use `OWNER_ATTENTION`. V2.4
  manifests remain valid but do not claim V2.5 sweep evidence.
- V2.5 control-plane architecture escalation is distinct from a project-local
  implementation failure. Multiple projects unable to start, heartbeat next-stage
  derivation or dispatch failure, a parallelism anomaly, long-idle tasks, or a
  governance/user-goal conflict requires a timely owner-liaison packet with exactly
  `affected_projects`, `root_cause`, `architecture_options`, `recommended_option`,
  `user_decision_required`, and `immediate_safe_actions`. Safe projects continue.
  One project's ordinary implementation architecture remains with that owner unless
  it crosses the existing major-architecture owner gate.
- Every V2.5 project has a `goal_contract`. `final_goal`, `current_stage`,
  `next_deliverable`, and non-empty `acceptance_evidence` make progress concrete.
  `autonomous_decision_scope` must cover ordinary implementation, tests, builds,
  mechanical/path/harness recovery, small project-local architecture, and local Git
  closeout. `stop_conditions` retain first-nonzero, scope/writer, owner-gate, and
  acceptance boundaries. `owner_only_exceptions` are exactly cross-project conflict,
  major architecture, authority escalation, credentials/private data, production
  release/deploy, cross-host migration, and destructive or irreversible external
  writes. `next_stage_trigger=STAGE_TERMINAL`, `roll_forward_required=true`, and
  `ordinary_recovery_autonomous=true` require a terminal stage to update the current
  stage and next deliverable before the next action is dispatched. A missing goal is
  a governance defect and cannot become silent global waiting; one project blocker
  cannot pause independent projects. V2.4 projects do not require this block.
- In federated mode, grant each owner only its project-local envelope, such as
  `project_local_decide`, `project_local_admission`, `project_execute`, and the
  exact repository/test/delivery authorities it needs. These never imply external
  publication, release, credentials, destructive cleanup, cross-project authority,
  migration control, ledger/lifecycle control, liaison authority, or authority to
  rewrite the envelope itself. Control-plane authorities in a federated project's
  manifest are invalid. Only `owner_task_id` may hold `project_local_decide`,
  `project_local_admission`, or `project_fresh_round_derive`; scoped executors remain
  inside narrower implementation or QA subsets.
- Repository visibility is `private`, `public`, or `internal`. `uploaded` is a
  readback fact, not an intention.
- Paths identify canonical roots for their host. Never treat a path from one host
  as evidence about another host.
- `max_parallel_projects` limits independent project work, not writers within one
  project. Keep one writer per project unless the user explicitly defines safe,
  non-overlapping ownership.

Update state from evidence. Do not mark a project complete because its task says it
is complete; record the evidence that proves the desired outcome.

Run `validate-manifest` after every manifest edit.

A first formal/native nonzero still stops the current round. It does not revoke the
project objective or its V2.4/V2.5 autonomy: the same project owner may derive a fresh
round only when the new action is materially different and retained evidence is
preserved. Host, root, writer, frozen-lane, migration, publication, and credential
gates are unchanged.

## Thread identity boundary

`owner_task_id` names the intended current writer for a project. It is not proof
that the task still exists, is on the correct host/root, or holds the writer lease.
Keep volatile task state out of the portfolio manifest and capture it in a separate
authoritative topology snapshot described in
[thread-architecture.md](thread-architecture.md).
In federated mode the owner must also be live; `retired`, `unavailable`, provisional,
or `handoff_only` tasks cannot exercise project autonomy. Every project not in
`frozen` or `complete` state must name one such writer owner, and both its manifest
envelope and owner task must include `project_local_decide`,
`project_local_admission`, and `project_fresh_round_derive`.

Run `audit-topology` after task creation, owner transfer, recovery, migration, or a
material concurrency change. Update `owner_task_id` only from runtime readback; do
not preserve a stale task ID merely because it appears in an earlier report.
