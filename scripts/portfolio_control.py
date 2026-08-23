#!/usr/bin/env python3
"""Deterministic controls for Codex Project Pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA = "codex-project-pilot/1"
EVENT_SCHEMA = "codex-project-pilot-event/1"
TOPOLOGY_SCHEMA = "codex-project-pilot-topology/1"
TOPOLOGY_AUDIT_SCHEMA = "codex-project-pilot-topology-audit/1"
ZERO_HASH = "0" * 64
PROJECT_STATES = {"frozen", "ready", "active", "waiting", "blocked", "complete"}
HOST_SCOPES = {"local", "remote"}
VISIBILITIES = {"private", "public", "internal"}
THREAD_STATES = {
    "queued",
    "idle",
    "active",
    "waiting",
    "blocked",
    "handoff_only",
    "retired",
    "unavailable",
}
CONTEXT_PRESSURE_STATES = {"unknown", "normal", "watch", "renewal_required"}
SUMMARY_QUALITY_FIELDS = ("short", "accurate", "usable")
CONTROL_LIFECYCLE_PHASES = {
    "running",
    "waiting",
    "owner_attention",
    "complete",
    "stopped",
}
AUTOMATION_STATUSES = {"ACTIVE", "PAUSED", "MISSING"}
AUTOMATION_NOTIFICATION_POLICIES = {"ALL", "FAILED_RUNS_ONLY", "UNKNOWN"}
WORK_PROGRESS_KINDS = {
    "none",
    "admitted",
    "dispatched",
    "evidence_delta",
    "terminal",
}
WORK_ADMISSION_RESULTS = {"ZERO", "NONZERO", "UNEXECUTED"}
STAGE_CLOSEOUT_STATUSES = {"in_progress", "complete", "stopped"}
STAGE_STEP_RESULTS = {"PASS", "NOT_REQUIRED", "PENDING", "NONZERO", "UNEXECUTED"}
STAGE_CLOSEOUT_STEPS = (
    "evidence",
    "test",
    "build",
    "diff",
    "readback",
    "commit",
    "push",
    "merge",
)
CAPACITY_CLASSES = {"baseline", "surge"}
GOVERNANCE_MODES = {"root_controller", "federated_thin_kernel"}
PROJECT_TASK_CONTRACT_V2_4 = "PROJECT_TASK_CONTRACT_V2_4"
PROJECT_TASK_CONTRACT_V2_5 = "PROJECT_TASK_CONTRACT_V2_5"
PROJECT_TASK_CONTRACT_VERSIONS = {
    PROJECT_TASK_CONTRACT_V2_4,
    PROJECT_TASK_CONTRACT_V2_5,
}
ROUTINE_PUBLIC_NETWORK_AUTHORITY = "routine_public_network"
ROUTINE_PUBLIC_NETWORK_CATEGORIES = {
    "public_dependency_fetch",
    "public_documentation_lookup",
    "read_only_public_api",
    "build_resource_fetch",
    "network_diagnostic",
}
ROUTINE_PUBLIC_NETWORK_ENVELOPE_FIELDS = {
    "purpose",
    "domains_or_urls",
    "write_locations",
    "credential_boundary",
    "frequency",
    "expected_evidence",
    "stop_condition",
}
PROJECT_OWNER_GATE_CATEGORIES = {
    "credential_or_private_data",
    "production_or_real_user_impact",
    "destructive_operation",
    "external_publication_or_deployment",
    "cross_host_migration",
    "material_scope_or_dependency_expansion",
    "irreversible_external_write",
    "major_architecture_direction",
}
CONTINUOUS_PROGRESS_INDEPENDENT_WORK_CATEGORIES = {
    "feature",
    "integration",
    "test",
    "documentation",
    "performance",
    "evidence",
}
CONTINUOUS_PROGRESS_TRUE_FIELDS = (
    "enabled",
    "next_stage_long_contract_required",
    "fresh_admission_required",
    "blocked_gate_state_preserved",
    "acceptance_inference_forbidden",
    "safety_authority_publication_gates_preserved",
    "filler_or_duplicate_work_forbidden",
    "project_controlled_helpers_allowed",
    "helpers_count_toward_capacity",
    "helpers_cannot_hold_writer_lease",
)
HEARTBEAT_PROJECT_SWEEP_TRUE_FIELDS = (
    "enabled",
    "evaluate_every_manifest_project",
    "fresh_sources_required",
    "existing_action_or_pending_wait_not_required",
    "auto_form_minimum_envelope",
    "auto_fresh_admit",
    "auto_dispatch",
    "recompute_after_terminal",
    "blocked_project_does_not_pause_portfolio",
    "global_wait_only_when_no_safe_action",
    "project_goal_contract_required",
    "stage_terminal_roll_forward_required",
    "missing_goal_cannot_force_global_waiting",
    "single_project_blocker_cannot_force_global_waiting",
)
HEARTBEAT_PROJECT_SWEEP_CLASSIFICATIONS = {
    "DISPATCHED",
    "ALREADY_ACTIVE",
    "OWNER_BLOCKED",
    "NO_SAFE_ACTION",
    "COMPLETE_FROZEN",
}
HEARTBEAT_PROJECT_SWEEP_SAFE_CLASSIFICATIONS = {
    "DISPATCHED",
    "ALREADY_ACTIVE",
}
HEARTBEAT_PROJECT_SWEEP_GLOBAL_DECISIONS = {
    "RUNNING",
    "WAITING",
    "OWNER_ATTENTION",
}
HEARTBEAT_PROJECT_SWEEP_ENVELOPE_FIELDS = {
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
    "next_handoff",
}
CONTROL_PLANE_ESCALATION_TRIGGERS = {
    "MULTI_PROJECT_START_FAILURE",
    "HEARTBEAT_NEXT_STAGE_DERIVATION_FAILURE",
    "HEARTBEAT_DISPATCH_FAILURE",
    "PARALLELISM_ANOMALY",
    "TASKS_LONG_IDLE",
    "GOVERNANCE_GOAL_CONFLICT",
}
CONTROL_PLANE_PROJECT_ISSUES = {
    "START_FAILURE",
    "NEXT_STAGE_DERIVATION_FAILURE",
    "DISPATCH_FAILURE",
    "PARALLELISM_ANOMALY",
    "LONG_IDLE",
    "GOVERNANCE_GOAL_CONFLICT",
}
CONTROL_PLANE_ESCALATION_PACKET_FIELDS = {
    "affected_projects",
    "root_cause",
    "architecture_options",
    "recommended_option",
    "user_decision_required",
    "immediate_safe_actions",
}
PROJECT_GOAL_CONTRACT_FIELDS = (
    "final_goal",
    "current_stage",
    "next_deliverable",
    "acceptance_evidence",
    "autonomous_decision_scope",
    "stop_conditions",
    "owner_only_exceptions",
    "next_stage_trigger",
    "roll_forward_required",
    "ordinary_recovery_autonomous",
)
PROJECT_GOAL_AUTONOMOUS_SCOPE_REQUIRED = {
    "implementation",
    "test",
    "build",
    "mechanical_recovery",
    "path_recovery",
    "harness_recovery",
    "small_project_architecture",
    "local_git_closeout",
}
PROJECT_GOAL_STOP_CONDITIONS_REQUIRED = {
    "first_formal_or_native_nonzero",
    "scope_or_writer_conflict",
    "owner_only_exception",
    "acceptance_complete",
}
PROJECT_GOAL_OWNER_ONLY_EXCEPTIONS_REQUIRED = {
    "cross_project_conflict",
    "major_architecture",
    "authority_escalation",
    "credential_or_private_data",
    "production_release_or_deployment",
    "cross_host_migration",
    "destructive_or_irreversible_external_write",
}
PROJECT_GOAL_NEXT_STAGE_TRIGGER = "STAGE_TERMINAL"
FEDERATED_SCHEDULER_ALLOWED_AUTHORITIES = {
    "control_read",
    "manifest_read",
    "topology_read",
    "ledger_read",
    "capacity_plan",
    "capacity_calculation",
    "dispatch_budget_calculation",
    "dependency_order",
    "dependency_ordering",
    "dispatch_policy",
    "existing_project_wake",
    "bounded_dispatch_wake_recommendation",
    "deduplication",
    "batching",
    "efficiency_optimize",
    "efficiency_optimization",
}
FEDERATED_RUNTIME_ALLOWED_AUTHORITIES = {
    "control_read",
    "topology_read",
    "ledger_read",
    "ledger_write",
    "work_lease_audit",
    "task_lifecycle",
    "migration_control",
    "migration_lock",
    "handoff_control",
    "successor_create",
    "writer_transfer",
    "recoverable_thread_archive",
    "automation_read",
    "automation_lifecycle",
}
FEDERATED_LIAISON_ALLOWED_AUTHORITIES = {
    "control_read",
    "owner_request",
    "owner_response_read",
    "user_delivery",
    "notification_delivery",
    "closure_delivery",
    "manual_action_route",
}
FEDERATED_CONTROL_ROLE_AUTHORITIES = {
    "scheduler": FEDERATED_SCHEDULER_ALLOWED_AUTHORITIES,
    "runtime_supervisor": FEDERATED_RUNTIME_ALLOWED_AUTHORITIES,
    "owner_liaison": FEDERATED_LIAISON_ALLOWED_AUTHORITIES,
}
FEDERATED_CONTROL_ROLES = set(FEDERATED_CONTROL_ROLE_AUTHORITIES)
FEDERATED_CONTROL_ROLE_MINIMUM_AUTHORITIES = {
    "scheduler": {"topology_read", "dispatch_policy"},
    "runtime_supervisor": {"ledger_write", "migration_control"},
    "owner_liaison": {"owner_request"},
}
FEDERATED_PROJECT_FORBIDDEN_AUTHORITIES = (
    set().union(*FEDERATED_CONTROL_ROLE_AUTHORITIES.values())
    - {"control_read", "manifest_read", "topology_read", "ledger_read"}
) | {
    "portfolio_decide",
    "authority_grant",
    "authority_expand",
    "authority_envelope_write",
    "authority_envelope_rewrite",
    "cross_project_decide",
    "cross_project_write",
    "control_policy_write",
    "topology_snapshot_write",
}
FEDERATED_PROJECT_FORBIDDEN_AUTHORITY_PREFIXES = (
    "portfolio_",
    "cross_project_",
    "authority_envelope_",
    "control_policy_",
    "migration_",
)
FEDERATED_PROJECT_OWNER_ONLY_AUTHORITIES = {
    "project_local_decide",
    "project_local_admission",
    "project_fresh_round_derive",
}
LIVE_CONTROL_STATES = {"idle", "active", "waiting", "blocked"}
FEDERATED_SCHEDULER_FORBIDDEN_AUTHORITIES = {
    "portfolio_decide",
    "project_local_decide",
    "project_execute",
    "repo_write",
    "repo_write_local",
    "ledger_write",
    "migration_control",
    "owner_request",
}
DISPATCH_REQUIREMENT_FIELDS = (
    "complete_input_required",
    "fresh_admission_required",
    "independent_writer_required",
    "effective_project_action_required",
)
ADMISSION_BOOLEAN_FIELDS = {
    "external_mutation",
    "user_authorized",
    "continuation",
    "transport_model_override_present",
    "transport_effort_override_present",
    "migration_fence_required",
}


class ControlError(RuntimeError):
    """A fail-closed control error."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ControlError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ControlError(f"JSON root must be an object: {path}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def require_fields(value: dict[str, Any], fields: list[str], context: str) -> list[str]:
    return [f"{context}: missing {field}" for field in fields if field not in value]


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(is_non_empty_string(item) for item in value)


def is_lower_hex(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(char in "0123456789abcdef" for char in value)
    )


def is_enum_value(value: Any, choices: set[str]) -> bool:
    return isinstance(value, str) and value in choices


def is_federated_project_control_authority(authority: str) -> bool:
    return authority in FEDERATED_PROJECT_FORBIDDEN_AUTHORITIES or authority.startswith(
        FEDERATED_PROJECT_FORBIDDEN_AUTHORITY_PREFIXES
    )


def effective_max_active_turns(policy: dict[str, Any]) -> int:
    configured = policy["max_active_turns"]
    runtime_reported = policy["runtime_reported_max_active_turns"]
    return configured if runtime_reported is None else min(configured, runtime_reported)


def validate_project_owner_autonomy(value: Any) -> list[str]:
    context = "policy.project_owner_autonomy"
    if not isinstance(value, dict):
        return [f"{context}: must be an object"]
    errors = require_fields(
        value,
        [
            "contract_version",
            "routine_public_network",
            "continuous_progress",
            "owner_gate_categories",
            "first_nonzero_stops_round",
            "fresh_round_requires_material_difference",
        ],
        context,
    )
    if errors:
        return errors
    contract_version = value["contract_version"]
    if contract_version not in PROJECT_TASK_CONTRACT_VERSIONS:
        errors.append(
            f"{context}: contract_version must be {PROJECT_TASK_CONTRACT_V2_4} or {PROJECT_TASK_CONTRACT_V2_5}"
        )
    network = value["routine_public_network"]
    network_context = f"{context}.routine_public_network"
    if not isinstance(network, dict):
        errors.append(f"{network_context}: must be an object")
    else:
        errors.extend(
            require_fields(
                network,
                [
                    "authority",
                    "allowed_categories",
                    "minimum_envelope_fields",
                    "credentials_allowed",
                ],
                network_context,
            )
        )
        if network.get("authority") != ROUTINE_PUBLIC_NETWORK_AUTHORITY:
            errors.append(
                f"{network_context}: authority must be {ROUTINE_PUBLIC_NETWORK_AUTHORITY}"
            )
        allowed_categories = network.get("allowed_categories")
        if (
            not is_string_list(allowed_categories)
            or set(allowed_categories) != ROUTINE_PUBLIC_NETWORK_CATEGORIES
        ):
            errors.append(
                f"{network_context}: allowed_categories must list the exact routine public network categories"
            )
        minimum_envelope_fields = network.get("minimum_envelope_fields")
        if (
            not is_string_list(minimum_envelope_fields)
            or set(minimum_envelope_fields) != ROUTINE_PUBLIC_NETWORK_ENVELOPE_FIELDS
        ):
            errors.append(
                f"{network_context}: minimum_envelope_fields must list the exact routine public network envelope"
            )
        if network.get("credentials_allowed") is not False:
            errors.append(f"{network_context}: credentials_allowed must be false")
    continuous_progress = value["continuous_progress"]
    continuous_context = f"{context}.continuous_progress"
    if not isinstance(continuous_progress, dict):
        errors.append(f"{continuous_context}: must be an object")
    else:
        errors.extend(
            require_fields(
                continuous_progress,
                [
                    *CONTINUOUS_PROGRESS_TRUE_FIELDS,
                    "independent_work_categories",
                ],
                continuous_context,
            )
        )
        for field in CONTINUOUS_PROGRESS_TRUE_FIELDS:
            if field in continuous_progress and continuous_progress[field] is not True:
                errors.append(f"{continuous_context}: {field} must be true")
        independent_work_categories = continuous_progress.get(
            "independent_work_categories"
        )
        if (
            not is_string_list(independent_work_categories)
            or len(independent_work_categories)
            != len(set(independent_work_categories or []))
            or set(independent_work_categories)
            != CONTINUOUS_PROGRESS_INDEPENDENT_WORK_CATEGORIES
        ):
            errors.append(
                f"{continuous_context}: independent_work_categories must list the exact continuous-progress categories"
            )
    owner_gate_categories = value["owner_gate_categories"]
    if (
        not is_string_list(owner_gate_categories)
        or set(owner_gate_categories) != PROJECT_OWNER_GATE_CATEGORIES
    ):
        errors.append(
            f"{context}: owner_gate_categories must list the exact owner gates"
        )
    if value["first_nonzero_stops_round"] is not True:
        errors.append(f"{context}: first_nonzero_stops_round must be true")
    if value["fresh_round_requires_material_difference"] is not True:
        errors.append(
            f"{context}: fresh_round_requires_material_difference must be true"
        )
    heartbeat_sweep = value.get("heartbeat_project_sweep")
    if contract_version == PROJECT_TASK_CONTRACT_V2_5 and heartbeat_sweep is None:
        errors.append(
            f"{context}: {PROJECT_TASK_CONTRACT_V2_5} requires heartbeat_project_sweep"
        )
    if heartbeat_sweep is not None:
        sweep_context = f"{context}.heartbeat_project_sweep"
        if not isinstance(heartbeat_sweep, dict):
            errors.append(f"{sweep_context}: must be an object")
        else:
            errors.extend(
                require_fields(
                    heartbeat_sweep,
                    [
                        *HEARTBEAT_PROJECT_SWEEP_TRUE_FIELDS,
                        "classifications",
                        "minimum_envelope_fields",
                        "control_plane_escalation",
                    ],
                    sweep_context,
                )
            )
            for field in HEARTBEAT_PROJECT_SWEEP_TRUE_FIELDS:
                if field in heartbeat_sweep and heartbeat_sweep[field] is not True:
                    errors.append(f"{sweep_context}: {field} must be true")
            classifications = heartbeat_sweep.get("classifications")
            if (
                not is_string_list(classifications)
                or len(classifications) != len(set(classifications or []))
                or set(classifications) != HEARTBEAT_PROJECT_SWEEP_CLASSIFICATIONS
            ):
                errors.append(
                    f"{sweep_context}: classifications must list the exact V2_5 project sweep classifications"
                )
            minimum_envelope_fields = heartbeat_sweep.get(
                "minimum_envelope_fields"
            )
            if (
                not is_string_list(minimum_envelope_fields)
                or len(minimum_envelope_fields)
                != len(set(minimum_envelope_fields or []))
                or set(minimum_envelope_fields)
                != HEARTBEAT_PROJECT_SWEEP_ENVELOPE_FIELDS
            ):
                errors.append(
                    f"{sweep_context}: minimum_envelope_fields must list the exact V2_5 dispatch envelope"
                )
            escalation = heartbeat_sweep.get("control_plane_escalation")
            escalation_context = f"{sweep_context}.control_plane_escalation"
            if not isinstance(escalation, dict):
                errors.append(f"{escalation_context}: must be an object")
            else:
                errors.extend(
                    require_fields(
                        escalation,
                        [
                            "enabled",
                            "trigger_categories",
                            "notification_fields",
                            "continue_other_projects",
                            "ordinary_single_project_failure_is_project_local",
                            "major_project_architecture_remains_owner_gate",
                        ],
                        escalation_context,
                    )
                )
                for field in (
                    "enabled",
                    "continue_other_projects",
                    "ordinary_single_project_failure_is_project_local",
                    "major_project_architecture_remains_owner_gate",
                ):
                    if field in escalation and escalation[field] is not True:
                        errors.append(f"{escalation_context}: {field} must be true")
                trigger_categories = escalation.get("trigger_categories")
                if (
                    not is_string_list(trigger_categories)
                    or len(trigger_categories)
                    != len(set(trigger_categories or []))
                    or set(trigger_categories) != CONTROL_PLANE_ESCALATION_TRIGGERS
                ):
                    errors.append(
                        f"{escalation_context}: trigger_categories must list the exact V2_5 control-plane triggers"
                    )
                notification_fields = escalation.get("notification_fields")
                if (
                    not is_string_list(notification_fields)
                    or len(notification_fields)
                    != len(set(notification_fields or []))
                    or set(notification_fields)
                    != CONTROL_PLANE_ESCALATION_PACKET_FIELDS
                ):
                    errors.append(
                        f"{escalation_context}: notification_fields must list the exact V2_5 owner-liaison packet"
                    )
    return errors


def validate_project_goal_contract(value: Any, context: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{context}: must be an object"]
    errors = require_fields(value, list(PROJECT_GOAL_CONTRACT_FIELDS), context)
    if errors:
        return errors
    for field in ("final_goal", "current_stage", "next_deliverable"):
        if not is_non_empty_string(value[field]):
            errors.append(f"{context}: {field} must be a non-empty string")
    acceptance_evidence = value["acceptance_evidence"]
    if (
        not is_string_list(acceptance_evidence)
        or not acceptance_evidence
        or len(acceptance_evidence) != len(set(acceptance_evidence or []))
    ):
        errors.append(
            f"{context}: acceptance_evidence must be a non-empty unique string array"
        )
    autonomous_decision_scope = value["autonomous_decision_scope"]
    if (
        not is_string_list(autonomous_decision_scope)
        or len(autonomous_decision_scope)
        != len(set(autonomous_decision_scope or []))
        or not PROJECT_GOAL_AUTONOMOUS_SCOPE_REQUIRED.issubset(
            set(autonomous_decision_scope or [])
        )
    ):
        errors.append(
            f"{context}: autonomous_decision_scope must include the required ordinary implementation and recovery categories"
        )
    stop_conditions = value["stop_conditions"]
    if (
        not is_string_list(stop_conditions)
        or len(stop_conditions) != len(set(stop_conditions or []))
        or not PROJECT_GOAL_STOP_CONDITIONS_REQUIRED.issubset(
            set(stop_conditions or [])
        )
    ):
        errors.append(
            f"{context}: stop_conditions must include the required round, ownership, owner-gate, and acceptance boundaries"
        )
    owner_only_exceptions = value["owner_only_exceptions"]
    if (
        not is_string_list(owner_only_exceptions)
        or len(owner_only_exceptions) != len(set(owner_only_exceptions or []))
        or set(owner_only_exceptions)
        != PROJECT_GOAL_OWNER_ONLY_EXCEPTIONS_REQUIRED
    ):
        errors.append(
            f"{context}: owner_only_exceptions must list the exact V2.5 owner gates"
        )
    if value["next_stage_trigger"] != PROJECT_GOAL_NEXT_STAGE_TRIGGER:
        errors.append(
            f"{context}: next_stage_trigger must be {PROJECT_GOAL_NEXT_STAGE_TRIGGER}"
        )
    if value["roll_forward_required"] is not True:
        errors.append(f"{context}: roll_forward_required must be true")
    if value["ordinary_recovery_autonomous"] is not True:
        errors.append(f"{context}: ordinary_recovery_autonomous must be true")
    return errors


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors = require_fields(
        manifest,
        ["schema_version", "portfolio_id", "goal", "policy", "projects"],
        "manifest",
    )
    if errors:
        return errors
    if manifest["schema_version"] != MANIFEST_SCHEMA:
        errors.append(f"manifest: schema_version must be {MANIFEST_SCHEMA}")
    for field in ("portfolio_id", "goal"):
        if not isinstance(manifest[field], str) or not manifest[field].strip():
            errors.append(f"manifest: {field} must be a non-empty string")
    policy = manifest["policy"]
    manifest_governance_mode = "root_controller"
    project_owner_autonomy_present = False
    project_owner_contract_version = None
    if not isinstance(policy, dict):
        errors.append("manifest: policy must be an object")
    else:
        errors.extend(
            require_fields(
                policy,
                [
                    "max_parallel_projects",
                    "default_repo_visibility",
                    "external_mutations_require_user_authorization",
                ],
                "policy",
            )
        )
        max_parallel = policy.get("max_parallel_projects")
        if (
            not isinstance(max_parallel, int)
            or isinstance(max_parallel, bool)
            or max_parallel < 1
        ):
            errors.append("policy: max_parallel_projects must be a positive integer")
        if not is_enum_value(policy.get("default_repo_visibility"), VISIBILITIES):
            errors.append("policy: default_repo_visibility is invalid")
        if not isinstance(policy.get("external_mutations_require_user_authorization"), bool):
            errors.append(
                "policy: external_mutations_require_user_authorization must be boolean"
            )
        manifest_governance_mode = policy.get(
            "governance_mode", "root_controller"
        )
        if not is_enum_value(manifest_governance_mode, GOVERNANCE_MODES):
            errors.append(
                "policy: governance_mode must be root_controller or federated_thin_kernel"
            )
        project_owner_autonomy_present = "project_owner_autonomy" in policy
        if project_owner_autonomy_present:
            autonomy = policy["project_owner_autonomy"]
            project_owner_contract_version = (
                autonomy.get("contract_version")
                if isinstance(autonomy, dict)
                else None
            )
            errors.extend(
                validate_project_owner_autonomy(autonomy)
            )
    projects = manifest["projects"]
    if not isinstance(projects, list) or not projects:
        errors.append("manifest: projects must be a non-empty array")
        return errors
    seen: set[str] = set()
    required = [
        "id",
        "name",
        "host_scope",
        "host_id",
        "root",
        "owner_task_id",
        "authorities",
        "state",
        "desired_outcome",
        "repository",
    ]
    for index, project in enumerate(projects):
        context = f"projects[{index}]"
        if not isinstance(project, dict):
            errors.append(f"{context}: must be an object")
            continue
        errors.extend(require_fields(project, required, context))
        if any(field not in project for field in required):
            continue
        for field in ("id", "name", "host_id", "root", "desired_outcome"):
            if not is_non_empty_string(project[field]):
                errors.append(f"{context}: {field} must be a non-empty string")
        project_id = project["id"]
        if isinstance(project_id, str):
            if project_id in seen:
                errors.append(f"{context}: duplicate project id {project_id}")
            seen.add(project_id)
        if not is_enum_value(project["host_scope"], HOST_SCOPES):
            errors.append(f"{context}: host_scope is invalid")
        if not is_enum_value(project["state"], PROJECT_STATES):
            errors.append(f"{context}: state is invalid")
        if not is_string_list(project["authorities"]):
            errors.append(f"{context}: authorities must be an array of strings")
        elif len(project["authorities"]) != len(set(project["authorities"])):
            errors.append(f"{context}: authorities must not contain duplicates")
        elif manifest_governance_mode == "federated_thin_kernel":
            forbidden_authorities = sorted(
                authority
                for authority in project["authorities"]
                if is_federated_project_control_authority(authority)
            )
            if forbidden_authorities:
                errors.append(
                    f"{context}: federated project authorities cannot include control-plane authorities: {', '.join(forbidden_authorities)}"
                )
        if (
            is_string_list(project["authorities"])
            and ROUTINE_PUBLIC_NETWORK_AUTHORITY in project["authorities"]
            and not project_owner_autonomy_present
        ):
            errors.append(
                f"{context}: {ROUTINE_PUBLIC_NETWORK_AUTHORITY} requires policy.project_owner_autonomy {PROJECT_TASK_CONTRACT_V2_4} or {PROJECT_TASK_CONTRACT_V2_5}"
            )
        owner_task_id = project["owner_task_id"]
        if owner_task_id is not None and not is_non_empty_string(owner_task_id):
            errors.append(f"{context}: owner_task_id must be null or a non-empty string")
        repository = project["repository"]
        if not isinstance(repository, dict):
            errors.append(f"{context}: repository must be an object")
        else:
            errors.extend(
                require_fields(
                    repository,
                    ["provider", "full_name", "visibility", "uploaded"],
                    f"{context}.repository",
                )
            )
            if not is_enum_value(repository.get("visibility"), VISIBILITIES):
                errors.append(f"{context}.repository: visibility is invalid")
            if not isinstance(repository.get("uploaded"), bool):
                errors.append(f"{context}.repository: uploaded must be boolean")
            if not is_non_empty_string(repository.get("provider")):
                errors.append(f"{context}.repository: provider must be a non-empty string")
            full_name = repository.get("full_name")
            if full_name is not None and not is_non_empty_string(full_name):
                errors.append(
                    f"{context}.repository: full_name must be null or a non-empty string"
                )
        if project_owner_contract_version == PROJECT_TASK_CONTRACT_V2_5:
            if "goal_contract" not in project:
                errors.append(
                    f"{context}: {PROJECT_TASK_CONTRACT_V2_5} requires goal_contract"
                )
            else:
                errors.extend(
                    validate_project_goal_contract(
                        project["goal_contract"], f"{context}.goal_contract"
                    )
                )
    return errors


def validate_heartbeat_project_sweep(value: Any) -> list[str]:
    context = "topology.heartbeat_project_sweep"
    if not isinstance(value, dict):
        return [f"{context}: must be an object"]
    required = [
        "sweep_id",
        "observed_at_utc",
        "source_evidence",
        "project_results",
        "control_plane_escalation",
        "global_decision",
    ]
    errors = require_fields(value, required, context)
    if errors:
        return errors
    for field in ("sweep_id", "observed_at_utc"):
        if not is_non_empty_string(value[field]):
            errors.append(f"{context}: {field} must be a non-empty string")

    source = value["source_evidence"]
    source_context = f"{context}.source_evidence"
    if not isinstance(source, dict):
        errors.append(f"{source_context}: must be an object")
    else:
        source_fields = [
            "manifest_sha256",
            "ledger_head_seq",
            "topology_evidence_id",
            "task_readback_ids",
        ]
        errors.extend(require_fields(source, source_fields, source_context))
        if "manifest_sha256" in source and not is_lower_hex(
            source["manifest_sha256"], 64
        ):
            errors.append(
                f"{source_context}: manifest_sha256 must be 64 lowercase hex characters"
            )
        ledger_head_seq = source.get("ledger_head_seq")
        if (
            not isinstance(ledger_head_seq, int)
            or isinstance(ledger_head_seq, bool)
            or ledger_head_seq < 0
        ):
            errors.append(
                f"{source_context}: ledger_head_seq must be a non-negative integer"
            )
        if not is_non_empty_string(source.get("topology_evidence_id")):
            errors.append(
                f"{source_context}: topology_evidence_id must be a non-empty string"
            )
        task_readback_ids = source.get("task_readback_ids")
        if not isinstance(task_readback_ids, dict) or not task_readback_ids:
            errors.append(
                f"{source_context}: task_readback_ids must be a non-empty object"
            )
        elif not all(
            is_non_empty_string(project_id) and is_non_empty_string(evidence_id)
            for project_id, evidence_id in task_readback_ids.items()
        ):
            errors.append(
                f"{source_context}: task_readback_ids must map non-empty project IDs to non-empty evidence IDs"
            )

    project_results = value["project_results"]
    seen_projects: set[str] = set()
    safe_action_count = 0
    owner_blocker_count = 0
    control_plane_issue_projects: set[str] = set()
    if not isinstance(project_results, list) or not project_results:
        errors.append(f"{context}: project_results must be a non-empty array")
    else:
        result_fields = [
            "project_id",
            "classification",
            "action_id",
            "admission_id",
            "dispatched_task_id",
            "owner_blocker_id",
            "reason",
            "evidence_ids",
            "control_plane_issue",
            "goal_contract_evidence_id",
            "goal_current_stage",
            "goal_next_deliverable",
            "stage_terminal",
            "goal_rolled_forward",
        ]
        for index, result in enumerate(project_results):
            result_context = f"{context}.project_results[{index}]"
            if not isinstance(result, dict):
                errors.append(f"{result_context}: must be an object")
                continue
            errors.extend(require_fields(result, result_fields, result_context))
            if any(field not in result for field in result_fields):
                continue
            project_id = result["project_id"]
            if not is_non_empty_string(project_id):
                errors.append(f"{result_context}: project_id must be non-empty")
            elif project_id in seen_projects:
                errors.append(
                    f"{result_context}: duplicate project_id {project_id}"
                )
            else:
                seen_projects.add(project_id)
            classification = result["classification"]
            if not is_enum_value(
                classification, HEARTBEAT_PROJECT_SWEEP_CLASSIFICATIONS
            ):
                errors.append(f"{result_context}: classification is invalid")
                continue
            control_plane_issue = result["control_plane_issue"]
            if control_plane_issue is not None and not is_enum_value(
                control_plane_issue, CONTROL_PLANE_PROJECT_ISSUES
            ):
                errors.append(f"{result_context}: control_plane_issue is invalid")
            elif control_plane_issue is not None and is_non_empty_string(project_id):
                control_plane_issue_projects.add(project_id)
            for field in (
                "action_id",
                "admission_id",
                "dispatched_task_id",
                "owner_blocker_id",
            ):
                field_value = result[field]
                if field_value is not None and not is_non_empty_string(field_value):
                    errors.append(
                        f"{result_context}: {field} must be null or a non-empty string"
                    )
            if not is_non_empty_string(result["reason"]):
                errors.append(f"{result_context}: reason must be non-empty")
            if (
                not is_string_list(result["evidence_ids"])
                or not result["evidence_ids"]
                or len(result["evidence_ids"]) != len(set(result["evidence_ids"]))
            ):
                errors.append(
                    f"{result_context}: evidence_ids must be a non-empty unique string array"
                )
            goal_contract_evidence_id = result["goal_contract_evidence_id"]
            if not is_non_empty_string(goal_contract_evidence_id):
                errors.append(
                    f"{result_context}: goal_contract_evidence_id must be non-empty"
                )
            elif (
                is_string_list(result["evidence_ids"])
                and goal_contract_evidence_id not in result["evidence_ids"]
            ):
                errors.append(
                    f"{result_context}: evidence_ids must include goal_contract_evidence_id"
                )
            for field in ("goal_current_stage", "goal_next_deliverable"):
                if not is_non_empty_string(result[field]):
                    errors.append(f"{result_context}: {field} must be non-empty")
            for field in ("stage_terminal", "goal_rolled_forward"):
                if not isinstance(result[field], bool):
                    errors.append(f"{result_context}: {field} must be boolean")
            if result["stage_terminal"] is True and result["goal_rolled_forward"] is not True:
                errors.append(
                    f"{result_context}: terminal stage requires goal_rolled_forward"
                )
            if result["stage_terminal"] is False and result["goal_rolled_forward"] is not False:
                errors.append(
                    f"{result_context}: non-terminal stage cannot claim goal_rolled_forward"
                )
            if classification == "DISPATCHED":
                safe_action_count += 1
                for field in ("action_id", "admission_id", "dispatched_task_id"):
                    if not is_non_empty_string(result[field]):
                        errors.append(
                            f"{result_context}: DISPATCHED requires {field}"
                        )
                if result["owner_blocker_id"] is not None:
                    errors.append(
                        f"{result_context}: DISPATCHED cannot carry owner_blocker_id"
                    )
            elif classification == "ALREADY_ACTIVE":
                safe_action_count += 1
                for field in ("action_id", "dispatched_task_id"):
                    if not is_non_empty_string(result[field]):
                        errors.append(
                            f"{result_context}: ALREADY_ACTIVE requires {field}"
                        )
                if result["owner_blocker_id"] is not None:
                    errors.append(
                        f"{result_context}: ALREADY_ACTIVE cannot carry owner_blocker_id"
                    )
            elif classification == "OWNER_BLOCKED":
                owner_blocker_count += 1
                if not is_non_empty_string(result["owner_blocker_id"]):
                    errors.append(
                        f"{result_context}: OWNER_BLOCKED requires owner_blocker_id"
                    )
                if any(
                    result[field] is not None
                    for field in ("action_id", "admission_id", "dispatched_task_id")
                ):
                    errors.append(
                        f"{result_context}: OWNER_BLOCKED cannot carry action or dispatch IDs"
                    )
            elif any(
                result[field] is not None
                for field in (
                    "action_id",
                    "admission_id",
                    "dispatched_task_id",
                    "owner_blocker_id",
                )
            ):
                errors.append(
                    f"{result_context}: {classification} cannot carry action, dispatch, or blocker IDs"
                )

    escalation = value["control_plane_escalation"]
    if escalation is not None and not isinstance(escalation, dict):
        errors.append(
            f"{context}: control_plane_escalation must be null or an object"
        )
    elif isinstance(escalation, dict):
        escalation_context = f"{context}.control_plane_escalation"
        packet_fields = ["trigger", *sorted(CONTROL_PLANE_ESCALATION_PACKET_FIELDS)]
        errors.extend(require_fields(escalation, packet_fields, escalation_context))
        if not is_enum_value(
            escalation.get("trigger"), CONTROL_PLANE_ESCALATION_TRIGGERS
        ):
            errors.append(f"{escalation_context}: trigger is invalid")
        affected_projects = escalation.get("affected_projects")
        if (
            not is_string_list(affected_projects)
            or not affected_projects
            or len(affected_projects) != len(set(affected_projects or []))
        ):
            errors.append(
                f"{escalation_context}: affected_projects must be a non-empty unique string array"
            )
        elif not control_plane_issue_projects.issubset(set(affected_projects)):
            errors.append(
                f"{escalation_context}: affected_projects must include every project with control_plane_issue"
            )
        if (
            escalation.get("trigger") == "MULTI_PROJECT_START_FAILURE"
            and (not isinstance(affected_projects, list) or len(affected_projects) < 2)
        ):
            errors.append(
                f"{escalation_context}: MULTI_PROJECT_START_FAILURE requires at least two affected projects"
            )
        if not is_non_empty_string(escalation.get("root_cause")):
            errors.append(f"{escalation_context}: root_cause must be non-empty")
        architecture_options = escalation.get("architecture_options")
        if (
            not is_string_list(architecture_options)
            or len(architecture_options) < 2
            or len(architecture_options) != len(set(architecture_options or []))
        ):
            errors.append(
                f"{escalation_context}: architecture_options must contain at least two unique options"
            )
        if not is_non_empty_string(escalation.get("recommended_option")):
            errors.append(
                f"{escalation_context}: recommended_option must be non-empty"
            )
        if escalation.get("user_decision_required") is not True:
            errors.append(
                f"{escalation_context}: user_decision_required must be true"
            )
        immediate_safe_actions = escalation.get("immediate_safe_actions")
        if (
            not is_string_list(immediate_safe_actions)
            or len(immediate_safe_actions)
            != len(set(immediate_safe_actions or []))
        ):
            errors.append(
                f"{escalation_context}: immediate_safe_actions must be a unique string array"
            )
        if not control_plane_issue_projects:
            errors.append(
                f"{escalation_context}: packet requires project control_plane_issue evidence"
            )
    if control_plane_issue_projects and escalation is None:
        errors.append(
            f"{context}: control-plane issues require a timely owner-liaison escalation packet"
        )

    global_decision = value["global_decision"]
    if not is_enum_value(
        global_decision, HEARTBEAT_PROJECT_SWEEP_GLOBAL_DECISIONS
    ):
        errors.append(f"{context}: global_decision is invalid")
    elif safe_action_count:
        if global_decision != "RUNNING":
            errors.append(
                f"{context}: a safe project action requires global_decision RUNNING"
            )
    elif owner_blocker_count or control_plane_issue_projects:
        if global_decision != "OWNER_ATTENTION":
            errors.append(
                f"{context}: owner-only or control-plane blockers with no safe action require global_decision OWNER_ATTENTION"
            )
    elif global_decision != "WAITING":
        errors.append(
            f"{context}: no safe action and no owner-only blocker requires global_decision WAITING"
        )
    return errors


def validate_topology(topology: dict[str, Any]) -> list[str]:
    errors = require_fields(
        topology,
        [
            "schema_version",
            "authoritative",
            "observed_at_utc",
            "policy",
            "migration",
            "nested_workers",
            "stage_closeouts",
            "threads",
        ],
        "topology",
    )
    if errors:
        return errors
    if topology["schema_version"] != TOPOLOGY_SCHEMA:
        errors.append(f"topology: schema_version must be {TOPOLOGY_SCHEMA}")
    if not isinstance(topology["authoritative"], bool):
        errors.append("topology: authoritative must be boolean")
    if not is_non_empty_string(topology["observed_at_utc"]):
        errors.append("topology: observed_at_utc must be a non-empty string")
    if "heartbeat_project_sweep" in topology:
        errors.extend(
            validate_heartbeat_project_sweep(topology["heartbeat_project_sweep"])
        )

    policy = topology["policy"]
    role_names: set[str] = set()
    if not isinstance(policy, dict):
        errors.append("topology.policy: must be an object")
    else:
        errors.extend(
            require_fields(
                policy,
                [
                    "max_active_turns",
                    "baseline_max_active_turns",
                    "runtime_reported_max_active_turns",
                    "reserved_control_slots",
                    "dispatch_requirements",
                    "max_writers_per_project",
                    "control_roles",
                    "migration_controller_role",
                ],
                "topology.policy",
            )
        )
        governance_mode = policy.get("governance_mode", "root_controller")
        if not is_enum_value(governance_mode, GOVERNANCE_MODES):
            errors.append(
                "topology.policy: governance_mode must be root_controller or federated_thin_kernel"
            )
        for field in (
            "max_active_turns",
            "baseline_max_active_turns",
            "max_writers_per_project",
        ):
            value = policy.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                errors.append(f"topology.policy: {field} must be a positive integer")
        configured_limit = policy.get("max_active_turns")
        baseline_limit = policy.get("baseline_max_active_turns")
        if (
            isinstance(configured_limit, int)
            and not isinstance(configured_limit, bool)
            and isinstance(baseline_limit, int)
            and not isinstance(baseline_limit, bool)
            and baseline_limit > configured_limit
        ):
            errors.append(
                "topology.policy: baseline_max_active_turns cannot exceed max_active_turns"
            )
        runtime_limit = policy.get("runtime_reported_max_active_turns")
        if runtime_limit is not None and (
            not isinstance(runtime_limit, int)
            or isinstance(runtime_limit, bool)
            or runtime_limit < 1
        ):
            errors.append(
                "topology.policy: runtime_reported_max_active_turns must be null or a positive integer"
            )
        dispatch_requirements = policy.get("dispatch_requirements")
        if not isinstance(dispatch_requirements, dict):
            errors.append("topology.policy: dispatch_requirements must be an object")
        else:
            errors.extend(
                require_fields(
                    dispatch_requirements,
                    list(DISPATCH_REQUIREMENT_FIELDS),
                    "topology.policy.dispatch_requirements",
                )
            )
            for field in DISPATCH_REQUIREMENT_FIELDS:
                if field in dispatch_requirements and not isinstance(
                    dispatch_requirements[field], bool
                ):
                    errors.append(
                        f"topology.policy.dispatch_requirements: {field} must be boolean"
                    )
        reserved_control_slots = policy.get("reserved_control_slots")
        if (
            not isinstance(reserved_control_slots, int)
            or isinstance(reserved_control_slots, bool)
            or reserved_control_slots < 0
        ):
            errors.append(
                "topology.policy: reserved_control_slots must be a non-negative integer"
            )
        elif isinstance(configured_limit, int) and not isinstance(configured_limit, bool):
            effective_limit = (
                configured_limit
                if runtime_limit is None
                else min(configured_limit, runtime_limit)
                if isinstance(runtime_limit, int) and not isinstance(runtime_limit, bool)
                else None
            )
            if effective_limit is not None and reserved_control_slots >= effective_limit:
                errors.append(
                    "topology.policy: reserved_control_slots must be less than the effective active-turn limit"
                )
        if not is_non_empty_string(policy.get("migration_controller_role")):
            errors.append(
                "topology.policy: migration_controller_role must be a non-empty string"
            )
        control_roles = policy.get("control_roles")
        if not isinstance(control_roles, list) or not control_roles:
            errors.append("topology.policy: control_roles must be a non-empty array")
        else:
            for index, definition in enumerate(control_roles):
                context = f"topology.policy.control_roles[{index}]"
                if not isinstance(definition, dict):
                    errors.append(f"{context}: must be an object")
                    continue
                errors.extend(
                    require_fields(
                        definition,
                        ["role", "required", "max_instances", "required_authorities"],
                        context,
                    )
                )
                if not is_non_empty_string(definition.get("role")):
                    errors.append(f"{context}: role must be a non-empty string")
                else:
                    role = definition["role"]
                    if role in role_names:
                        errors.append(f"{context}: duplicate control role {role}")
                    role_names.add(role)
                if not isinstance(definition.get("required"), bool):
                    errors.append(f"{context}: required must be boolean")
                max_instances = definition.get("max_instances")
                if (
                    not isinstance(max_instances, int)
                    or isinstance(max_instances, bool)
                    or max_instances < 1
                ):
                    errors.append(f"{context}: max_instances must be a positive integer")
                if not is_string_list(definition.get("required_authorities")):
                    errors.append(
                        f"{context}: required_authorities must be an array of strings"
                    )
        controller_role = policy.get("migration_controller_role")
        if is_non_empty_string(controller_role) and role_names and controller_role not in role_names:
            errors.append(
                "topology.policy: migration_controller_role must name a control role"
            )

    migration = topology["migration"]
    if not isinstance(migration, dict):
        errors.append("topology.migration: must be an object")
    else:
        errors.extend(
            require_fields(
                migration,
                ["controller_task_id", "active_target_task_id", "lock_held"],
                "topology.migration",
            )
        )
        if not is_non_empty_string(migration.get("controller_task_id")):
            errors.append(
                "topology.migration: controller_task_id must be a non-empty string"
            )
        target = migration.get("active_target_task_id")
        if target is not None and not is_non_empty_string(target):
            errors.append(
                "topology.migration: active_target_task_id must be null or a non-empty string"
            )
        if not isinstance(migration.get("lock_held"), bool):
            errors.append("topology.migration: lock_held must be boolean")

    lifecycle = topology.get("control_lifecycle")
    if lifecycle is not None:
        lifecycle_context = "topology.control_lifecycle"
        if not isinstance(lifecycle, dict):
            errors.append(f"{lifecycle_context}: must be an object")
        else:
            topology_policy = topology.get("policy")
            governance_mode = (
                topology_policy.get("governance_mode", "root_controller")
                if isinstance(topology_policy, dict)
                else "root_controller"
            )
            controller_task_id_field = (
                "controller_task_id"
                if governance_mode == "federated_thin_kernel"
                else "root_task_id"
            )
            lifecycle_fields = [
                "phase",
                controller_task_id_field,
                "safe_next_action",
                "pending_wait_id",
                "pending_owner_request_id",
                "consecutive_no_change",
                "automation_id",
                "automation_status",
                "automation_notification_policy",
                "closure_id",
                "closure_delivered",
                "closure_owner_liaison_task_id",
                "closure_delivery_turn_id",
                "pause_notice_delivered_before_pause",
            ]
            errors.extend(require_fields(lifecycle, lifecycle_fields, lifecycle_context))
            if all(field in lifecycle for field in lifecycle_fields):
                if not is_enum_value(lifecycle["phase"], CONTROL_LIFECYCLE_PHASES):
                    errors.append(f"{lifecycle_context}: phase is invalid")
                if not is_non_empty_string(lifecycle[controller_task_id_field]):
                    errors.append(
                        f"{lifecycle_context}: {controller_task_id_field} must be non-empty"
                    )
                if not isinstance(lifecycle["safe_next_action"], bool):
                    errors.append(f"{lifecycle_context}: safe_next_action must be boolean")
                for field in (
                    "pending_wait_id",
                    "pending_owner_request_id",
                    "automation_id",
                    "closure_id",
                    "closure_owner_liaison_task_id",
                    "closure_delivery_turn_id",
                ):
                    value = lifecycle[field]
                    if value is not None and not is_non_empty_string(value):
                        errors.append(
                            f"{lifecycle_context}: {field} must be null or a non-empty string"
                        )
                no_change = lifecycle["consecutive_no_change"]
                if (
                    not isinstance(no_change, int)
                    or isinstance(no_change, bool)
                    or no_change < 0
                ):
                    errors.append(
                        f"{lifecycle_context}: consecutive_no_change must be a non-negative integer"
                    )
                if not is_enum_value(lifecycle["automation_status"], AUTOMATION_STATUSES):
                    errors.append(f"{lifecycle_context}: automation_status is invalid")
                if not is_enum_value(
                    lifecycle["automation_notification_policy"],
                    AUTOMATION_NOTIFICATION_POLICIES,
                ):
                    errors.append(
                        f"{lifecycle_context}: automation_notification_policy is invalid"
                    )
                if not isinstance(lifecycle["closure_delivered"], bool):
                    errors.append(f"{lifecycle_context}: closure_delivered must be boolean")
                if not isinstance(
                    lifecycle["pause_notice_delivered_before_pause"], bool
                ):
                    errors.append(
                        f"{lifecycle_context}: pause_notice_delivered_before_pause must be boolean"
                    )
                if lifecycle["closure_delivered"] and (
                    lifecycle["closure_id"] is None
                    or lifecycle["closure_owner_liaison_task_id"] is None
                    or lifecycle["closure_delivery_turn_id"] is None
                ):
                    errors.append(
                        f"{lifecycle_context}: delivered closure requires closure, liaison, and delivery turn IDs"
                    )
                if (
                    not lifecycle["closure_delivered"]
                    and lifecycle["pause_notice_delivered_before_pause"]
                ):
                    errors.append(
                        f"{lifecycle_context}: pause notice ordering cannot be true before closure delivery"
                    )
                work_lease = lifecycle.get("work_lease")
                if work_lease is not None:
                    lease_context = f"{lifecycle_context}.work_lease"
                    if not isinstance(work_lease, dict):
                        errors.append(f"{lease_context}: must be an object")
                    else:
                        lease_fields = [
                            "action_id",
                            "admission_id",
                            "admission_result",
                            "dispatched_task_id",
                            "baseline_event_seq",
                            "latest_event_seq",
                            "progress_kind",
                            "evidence_ids",
                            "lease_renewed",
                            "action_terminal",
                        ]
                        errors.extend(
                            require_fields(work_lease, lease_fields, lease_context)
                        )
                        if all(field in work_lease for field in lease_fields):
                            if not is_non_empty_string(work_lease["action_id"]):
                                errors.append(
                                    f"{lease_context}: action_id must be non-empty"
                                )
                            for field in (
                                "admission_id",
                                "dispatched_task_id",
                            ):
                                value = work_lease[field]
                                if value is not None and not is_non_empty_string(value):
                                    errors.append(
                                        f"{lease_context}: {field} must be null or a non-empty string"
                                    )
                            admission_result = work_lease["admission_result"]
                            if admission_result is not None and not is_enum_value(
                                admission_result, WORK_ADMISSION_RESULTS
                            ):
                                errors.append(
                                    f"{lease_context}: admission_result is invalid"
                                )
                            for field in ("baseline_event_seq", "latest_event_seq"):
                                value = work_lease[field]
                                if (
                                    not isinstance(value, int)
                                    or isinstance(value, bool)
                                    or value < -1
                                ):
                                    errors.append(
                                        f"{lease_context}: {field} must be an integer >= -1"
                                    )
                            baseline = work_lease["baseline_event_seq"]
                            latest = work_lease["latest_event_seq"]
                            if (
                                isinstance(baseline, int)
                                and not isinstance(baseline, bool)
                                and isinstance(latest, int)
                                and not isinstance(latest, bool)
                                and latest < baseline
                            ):
                                errors.append(
                                    f"{lease_context}: latest_event_seq cannot precede baseline_event_seq"
                                )
                            if not is_enum_value(
                                work_lease["progress_kind"], WORK_PROGRESS_KINDS
                            ):
                                errors.append(
                                    f"{lease_context}: progress_kind is invalid"
                                )
                            evidence_ids = work_lease["evidence_ids"]
                            if not is_string_list(evidence_ids):
                                errors.append(
                                    f"{lease_context}: evidence_ids must be an array of non-empty strings"
                                )
                            elif len(evidence_ids) != len(set(evidence_ids)):
                                errors.append(
                                    f"{lease_context}: evidence_ids must be unique"
                                )
                            for field in ("lease_renewed", "action_terminal"):
                                if not isinstance(work_lease[field], bool):
                                    errors.append(
                                        f"{lease_context}: {field} must be boolean"
                                    )

    nested_workers = topology["nested_workers"]
    if not isinstance(nested_workers, list):
        errors.append("topology: nested_workers must be an array")
        nested_workers = []
    seen_worker_ids: set[str] = set()
    required_worker_fields = [
        "worker_id",
        "controller_task_id",
        "project_id",
        "host_id",
        "active",
        "writer",
        "capacity_class",
    ]
    for index, worker in enumerate(nested_workers):
        context = f"topology.nested_workers[{index}]"
        if not isinstance(worker, dict):
            errors.append(f"{context}: must be an object")
            continue
        errors.extend(require_fields(worker, required_worker_fields, context))
        if any(field not in worker for field in required_worker_fields):
            continue
        for field in ("worker_id", "controller_task_id", "host_id"):
            if not is_non_empty_string(worker[field]):
                errors.append(f"{context}: {field} must be a non-empty string")
        worker_id = worker["worker_id"]
        if isinstance(worker_id, str):
            if worker_id in seen_worker_ids:
                errors.append(f"{context}: duplicate worker_id {worker_id}")
            seen_worker_ids.add(worker_id)
        project_id = worker["project_id"]
        if project_id is not None and not is_non_empty_string(project_id):
            errors.append(f"{context}: project_id must be null or a non-empty string")
        for field in ("active", "writer"):
            if not isinstance(worker[field], bool):
                errors.append(f"{context}: {field} must be boolean")
        if not is_enum_value(worker["capacity_class"], CAPACITY_CLASSES):
            errors.append(f"{context}: capacity_class is invalid")

    stage_closeouts = topology["stage_closeouts"]
    if not isinstance(stage_closeouts, list):
        errors.append("topology: stage_closeouts must be an array")
        stage_closeouts = []
    seen_stage_ids: set[str] = set()
    required_closeout_fields = [
        "stage_id",
        "project_id",
        "project_task_id",
        "host_id",
        "branch",
        "target_branch",
        "status",
        "step_results",
        "identity_verified",
        "worktree_scope_clean",
        "conflict_free",
        "worktree_merge_required",
        "first_nonzero_step",
        "commit_sha",
        "push_readback_sha",
        "merge_readback_sha",
    ]
    for index, closeout in enumerate(stage_closeouts):
        context = f"topology.stage_closeouts[{index}]"
        if not isinstance(closeout, dict):
            errors.append(f"{context}: must be an object")
            continue
        errors.extend(require_fields(closeout, required_closeout_fields, context))
        if any(field not in closeout for field in required_closeout_fields):
            continue
        for field in (
            "stage_id",
            "project_id",
            "project_task_id",
            "host_id",
            "branch",
            "target_branch",
        ):
            if not is_non_empty_string(closeout[field]):
                errors.append(f"{context}: {field} must be a non-empty string")
        stage_id = closeout["stage_id"]
        if isinstance(stage_id, str):
            if stage_id in seen_stage_ids:
                errors.append(f"{context}: duplicate stage_id {stage_id}")
            seen_stage_ids.add(stage_id)
        if not is_enum_value(closeout["status"], STAGE_CLOSEOUT_STATUSES):
            errors.append(f"{context}: status is invalid")
        for field in (
            "identity_verified",
            "worktree_scope_clean",
            "conflict_free",
            "worktree_merge_required",
        ):
            if not isinstance(closeout[field], bool):
                errors.append(f"{context}: {field} must be boolean")
        first_nonzero_step = closeout["first_nonzero_step"]
        if first_nonzero_step is not None and first_nonzero_step not in STAGE_CLOSEOUT_STEPS:
            errors.append(
                f"{context}: first_nonzero_step must be null or a known stage step"
            )
        for field in ("commit_sha", "push_readback_sha", "merge_readback_sha"):
            value = closeout[field]
            if value is not None and not is_non_empty_string(value):
                errors.append(f"{context}: {field} must be null or a non-empty string")
        step_results = closeout["step_results"]
        if not isinstance(step_results, dict):
            errors.append(f"{context}.step_results: must be an object")
        else:
            errors.extend(
                require_fields(step_results, list(STAGE_CLOSEOUT_STEPS), f"{context}.step_results")
            )
            for step in STAGE_CLOSEOUT_STEPS:
                if step in step_results and not is_enum_value(
                    step_results[step], STAGE_STEP_RESULTS
                ):
                    errors.append(f"{context}.step_results: {step} is invalid")

    threads = topology["threads"]
    if not isinstance(threads, list) or not threads:
        errors.append("topology: threads must be a non-empty array")
        return errors
    seen_task_ids: set[str] = set()
    required_thread_fields = [
        "task_id",
        "role",
        "project_id",
        "host_id",
        "root",
        "state",
        "active_turn",
        "writer",
        "provisional",
        "authorities",
        "capacity_class",
    ]
    for index, thread in enumerate(threads):
        context = f"topology.threads[{index}]"
        if not isinstance(thread, dict):
            errors.append(f"{context}: must be an object")
            continue
        errors.extend(require_fields(thread, required_thread_fields, context))
        if any(field not in thread for field in required_thread_fields):
            continue
        for field in ("task_id", "role", "host_id", "root"):
            if not is_non_empty_string(thread[field]):
                errors.append(f"{context}: {field} must be a non-empty string")
        task_id = thread["task_id"]
        if isinstance(task_id, str):
            if task_id in seen_task_ids:
                errors.append(f"{context}: duplicate task_id {task_id}")
            seen_task_ids.add(task_id)
        project_id = thread["project_id"]
        if project_id is not None and not is_non_empty_string(project_id):
            errors.append(f"{context}: project_id must be null or a non-empty string")
        canonical_project_root = thread.get("canonical_project_root")
        if canonical_project_root is not None and not is_non_empty_string(
            canonical_project_root
        ):
            errors.append(
                f"{context}: canonical_project_root must be null or a non-empty string"
            )
        if not is_enum_value(thread["state"], THREAD_STATES):
            errors.append(f"{context}: state is invalid")
        for field in ("active_turn", "writer", "provisional"):
            if not isinstance(thread[field], bool):
                errors.append(f"{context}: {field} must be boolean")
        if not is_string_list(thread["authorities"]):
            errors.append(f"{context}: authorities must be an array of strings")
        elif len(thread["authorities"]) != len(set(thread["authorities"])):
            errors.append(f"{context}: authorities must not contain duplicates")
        if not is_enum_value(thread["capacity_class"], CAPACITY_CLASSES):
            errors.append(f"{context}: capacity_class is invalid")
        dispatch_admission = thread.get("dispatch_admission")
        if dispatch_admission is not None:
            admission_context = f"{context}.dispatch_admission"
            admission_fields = [
                "action_id",
                "input_complete",
                "admission_id",
                "admission_result",
                "writer_task_id",
            ]
            if not isinstance(dispatch_admission, dict):
                errors.append(f"{admission_context}: must be null or an object")
            else:
                errors.extend(
                    require_fields(dispatch_admission, admission_fields, admission_context)
                )
                if all(field in dispatch_admission for field in admission_fields):
                    for field in ("action_id", "admission_id", "writer_task_id"):
                        if not is_non_empty_string(dispatch_admission[field]):
                            errors.append(
                                f"{admission_context}: {field} must be a non-empty string"
                            )
                    if not isinstance(dispatch_admission["input_complete"], bool):
                        errors.append(f"{admission_context}: input_complete must be boolean")
                    if not is_enum_value(
                        dispatch_admission["admission_result"], WORK_ADMISSION_RESULTS
                    ):
                        errors.append(f"{admission_context}: admission_result is invalid")
        context_health = thread.get("context_health")
        if context_health is None:
            continue
        health_context = f"{context}.context_health"
        if not isinstance(context_health, dict):
            errors.append(f"{health_context}: must be an object")
            continue
        health_fields = [
            "pressure",
            "signals",
            "compaction_observed",
            "summary_quality",
            "controller_notified",
            "notification_target_task_id",
            "notification_id",
        ]
        errors.extend(require_fields(context_health, health_fields, health_context))
        if any(field not in context_health for field in health_fields):
            continue
        if not is_enum_value(context_health["pressure"], CONTEXT_PRESSURE_STATES):
            errors.append(f"{health_context}: pressure is invalid")
        signals = context_health["signals"]
        if not is_string_list(signals):
            errors.append(f"{health_context}: signals must be an array of strings")
        elif len(signals) != len(set(signals)):
            errors.append(f"{health_context}: signals must not contain duplicates")
        if not isinstance(context_health["compaction_observed"], bool):
            errors.append(f"{health_context}: compaction_observed must be boolean")
        summary_quality = context_health["summary_quality"]
        if summary_quality is not None:
            if not isinstance(summary_quality, dict):
                errors.append(f"{health_context}: summary_quality must be null or an object")
            else:
                errors.extend(
                    require_fields(
                        summary_quality,
                        list(SUMMARY_QUALITY_FIELDS),
                        f"{health_context}.summary_quality",
                    )
                )
                for field in SUMMARY_QUALITY_FIELDS:
                    if field in summary_quality and not isinstance(summary_quality[field], bool):
                        errors.append(
                            f"{health_context}.summary_quality: {field} must be boolean"
                        )
        notified = context_health["controller_notified"]
        if not isinstance(notified, bool):
            errors.append(f"{health_context}: controller_notified must be boolean")
        notification_target = context_health["notification_target_task_id"]
        notification_id = context_health["notification_id"]
        if notification_target is not None and not is_non_empty_string(notification_target):
            errors.append(
                f"{health_context}: notification_target_task_id must be null or a non-empty string"
            )
        if notification_id is not None and not is_non_empty_string(notification_id):
            errors.append(
                f"{health_context}: notification_id must be null or a non-empty string"
            )
        if notified is True and (notification_target is None or notification_id is None):
            errors.append(
                f"{health_context}: a delivered notification requires target and notification ID"
            )
        if notified is False and (notification_target is not None or notification_id is not None):
            errors.append(
                f"{health_context}: an undelivered notification cannot retain target or notification ID"
            )
    return errors


def audit_topology(
    manifest: dict[str, Any], topology: dict[str, Any]
) -> dict[str, Any]:
    manifest_errors = validate_manifest(manifest)
    topology_errors = validate_topology(topology)
    if manifest_errors or topology_errors:
        raise ControlError("; ".join(manifest_errors + topology_errors))

    findings: list[dict[str, Any]] = []

    def finding(code: str, message: str, **evidence: Any) -> None:
        item = {"code": code, "message": message}
        if evidence:
            item["evidence"] = evidence
        findings.append(item)

    policy = topology["policy"]
    manifest_governance_mode = manifest["policy"].get(
        "governance_mode", "root_controller"
    )
    topology_governance_mode = policy.get("governance_mode", "root_controller")
    governance_mode = (
        "federated_thin_kernel"
        if "federated_thin_kernel"
        in {manifest_governance_mode, topology_governance_mode}
        else "root_controller"
    )
    control_role_names = {
        definition["role"] for definition in policy["control_roles"]
    }
    threads = topology["threads"]
    nested_workers = topology["nested_workers"]
    stage_closeouts = topology["stage_closeouts"]
    projects = {project["id"]: project for project in manifest["projects"]}
    tasks = {thread["task_id"]: thread for thread in threads}
    active_threads = [thread for thread in threads if thread["active_turn"]]
    active_nested_workers = [worker for worker in nested_workers if worker["active"]]
    active_execution_unit_count = len(active_threads) + len(active_nested_workers)
    configured_max_active_turns = policy["max_active_turns"]
    runtime_reported_max_active_turns = policy["runtime_reported_max_active_turns"]
    effective_limit = effective_max_active_turns(policy)
    baseline_limit = policy["baseline_max_active_turns"]
    active_surge_threads = [
        thread
        for thread in active_threads
        if thread["capacity_class"] == "surge"
    ]
    required_surge_slot_count = max(
        0,
        active_execution_unit_count
        + policy["reserved_control_slots"]
        - baseline_limit,
    )
    new_dispatch_budget = max(
        0,
        effective_limit
        - active_execution_unit_count
        - policy["reserved_control_slots"],
    )
    context_pressure_counts: Counter[str] = Counter()

    if manifest_governance_mode != topology_governance_mode:
        finding(
            "GOVERNANCE_MODE_MISMATCH",
            "manifest and topology governance modes must match; audit fails closed to the stricter federated mode",
            manifest_governance_mode=manifest_governance_mode,
            topology_governance_mode=topology_governance_mode,
            effective_governance_mode=governance_mode,
        )
    if not topology["authoritative"]:
        finding(
            "NON_AUTHORITATIVE_TOPOLOGY",
            "topology audit requires executor-owned runtime readback",
        )
    project_owner_autonomy = manifest["policy"].get("project_owner_autonomy", {})
    contract_version = (
        project_owner_autonomy.get("contract_version")
        if isinstance(project_owner_autonomy, dict)
        else None
    )
    heartbeat_sweep = topology.get("heartbeat_project_sweep")
    if contract_version == PROJECT_TASK_CONTRACT_V2_5:
        if not isinstance(heartbeat_sweep, dict):
            finding(
                "HEARTBEAT_PROJECT_SWEEP_MISSING",
                "V2.5 requires a fresh per-project sweep on every heartbeat",
                expected_project_ids=sorted(projects),
            )
        else:
            sweep_results = {
                result["project_id"]: result
                for result in heartbeat_sweep["project_results"]
            }
            observed_project_ids = set(sweep_results)
            expected_project_ids = set(projects)
            if observed_project_ids != expected_project_ids:
                finding(
                    "HEARTBEAT_PROJECT_SWEEP_INCOMPLETE",
                    "every manifest project must receive exactly one heartbeat classification",
                    missing_project_ids=sorted(
                        expected_project_ids - observed_project_ids
                    ),
                    unexpected_project_ids=sorted(
                        observed_project_ids - expected_project_ids
                    ),
                )
            source_evidence = heartbeat_sweep["source_evidence"]
            source_task_project_ids = set(source_evidence["task_readback_ids"])
            if source_task_project_ids != expected_project_ids:
                finding(
                    "HEARTBEAT_PROJECT_SWEEP_TASK_READBACK_INCOMPLETE",
                    "the sweep must derive every project decision from a fresh task readback",
                    missing_project_ids=sorted(
                        expected_project_ids - source_task_project_ids
                    ),
                    unexpected_project_ids=sorted(
                        source_task_project_ids - expected_project_ids
                    ),
                )
            expected_manifest_sha256 = sha256_text(canonical_json(manifest))
            if source_evidence["manifest_sha256"] != expected_manifest_sha256:
                finding(
                    "HEARTBEAT_PROJECT_SWEEP_MANIFEST_DRIFT",
                    "the sweep must use the audited canonical manifest",
                    expected_manifest_sha256=expected_manifest_sha256,
                    observed_manifest_sha256=source_evidence["manifest_sha256"],
                )
            if heartbeat_sweep["observed_at_utc"] != topology["observed_at_utc"]:
                finding(
                    "HEARTBEAT_PROJECT_SWEEP_STALE_TOPOLOGY",
                    "the project sweep and topology must come from the same wake readback",
                    topology_observed_at_utc=topology["observed_at_utc"],
                    sweep_observed_at_utc=heartbeat_sweep["observed_at_utc"],
                )
            escalation = heartbeat_sweep["control_plane_escalation"]
            if isinstance(escalation, dict):
                unexpected_affected_projects = sorted(
                    set(escalation["affected_projects"]) - expected_project_ids
                )
                if unexpected_affected_projects:
                    finding(
                        "HEARTBEAT_CONTROL_ESCALATION_PROJECT_UNKNOWN",
                        "control-plane escalation can name only manifest projects",
                        unexpected_project_ids=unexpected_affected_projects,
                    )
            for project_id in sorted(expected_project_ids & observed_project_ids):
                result = sweep_results[project_id]
                project = projects[project_id]
                classification = result["classification"]
                goal_contract = project.get("goal_contract")
                if isinstance(goal_contract, dict) and (
                    result["goal_current_stage"] != goal_contract["current_stage"]
                    or result["goal_next_deliverable"]
                    != goal_contract["next_deliverable"]
                ):
                    finding(
                        "HEARTBEAT_PROJECT_GOAL_DRIFT",
                        "the heartbeat classification must use the manifest project's current goal stage",
                        project_id=project_id,
                        expected_current_stage=goal_contract["current_stage"],
                        observed_current_stage=result["goal_current_stage"],
                        expected_next_deliverable=goal_contract["next_deliverable"],
                        observed_next_deliverable=result["goal_next_deliverable"],
                    )
                if (
                    classification == "COMPLETE_FROZEN"
                    and project["state"] not in {"complete", "frozen"}
                ):
                    finding(
                        "HEARTBEAT_PROJECT_SWEEP_FALSE_COMPLETE",
                        "COMPLETE_FROZEN requires a complete or frozen manifest project",
                        project_id=project_id,
                        project_state=project["state"],
                    )
                if classification in HEARTBEAT_PROJECT_SWEEP_SAFE_CLASSIFICATIONS:
                    dispatched_task_id = result["dispatched_task_id"]
                    if dispatched_task_id not in tasks:
                        finding(
                            "HEARTBEAT_PROJECT_SWEEP_DISPATCH_TARGET_MISSING",
                            "a runnable classification must reference an authoritative project task",
                            project_id=project_id,
                            classification=classification,
                            dispatched_task_id=dispatched_task_id,
                        )
                    elif tasks[dispatched_task_id]["project_id"] != project_id:
                        finding(
                            "HEARTBEAT_PROJECT_SWEEP_DISPATCH_TARGET_MISMATCH",
                            "the runnable task must belong to the classified project",
                            project_id=project_id,
                            dispatched_task_id=dispatched_task_id,
                            observed_project_id=tasks[dispatched_task_id]["project_id"],
                        )
                    if (
                        project["owner_task_id"] is not None
                        and dispatched_task_id != project["owner_task_id"]
                    ):
                        finding(
                            "HEARTBEAT_PROJECT_SWEEP_NON_OWNER_DISPATCH",
                            "a project sweep cannot bypass the manifest owner/writer",
                            project_id=project_id,
                            expected_owner_task_id=project["owner_task_id"],
                            dispatched_task_id=dispatched_task_id,
                        )
    for requirement, enabled in policy["dispatch_requirements"].items():
        if not enabled:
            finding(
                "DISPATCH_REQUIREMENT_DISABLED",
                "all surge-slot dispatch requirements must remain enabled",
                requirement=requirement,
            )
    if len(active_threads) > effective_limit:
        finding(
            "ACTIVE_TURN_LIMIT_EXCEEDED",
            "active turns exceed the configured limit after runtime clamping",
            active_turn_count=len(active_threads),
            configured_max_active_turns=configured_max_active_turns,
            effective_max_active_turns=effective_limit,
            runtime_reported_max_active_turns=runtime_reported_max_active_turns,
            task_ids=[thread["task_id"] for thread in active_threads],
        )
    if (
        active_nested_workers
        and active_execution_unit_count > effective_limit
    ):
        finding(
            "ACTIVE_EXECUTION_UNIT_LIMIT_EXCEEDED",
            "visible active turns plus nested workers exceed the configured limit",
            active_turn_count=len(active_threads),
            active_nested_worker_count=len(active_nested_workers),
            active_execution_unit_count=active_execution_unit_count,
            configured_max_active_execution_units=configured_max_active_turns,
            effective_max_active_execution_units=effective_limit,
            runtime_reported_max_active_turns=runtime_reported_max_active_turns,
            worker_ids=[worker["worker_id"] for worker in active_nested_workers],
        )

    for definition in policy["control_roles"]:
        matching = [thread for thread in threads if thread["role"] == definition["role"]]
        if definition["required"] and not matching:
            finding(
                "REQUIRED_CONTROL_ROLE_MISSING",
                f"required control role is missing: {definition['role']}",
                role=definition["role"],
            )
        if len(matching) > definition["max_instances"]:
            finding(
                "CONTROL_ROLE_MULTIPLICITY",
                f"control role exceeds max_instances: {definition['role']}",
                role=definition["role"],
                task_ids=[thread["task_id"] for thread in matching],
            )
        required_authorities = set(definition["required_authorities"])
        for thread in matching:
            missing = sorted(required_authorities - set(thread["authorities"]))
            if missing:
                finding(
                    "CONTROL_ROLE_AUTHORITY_MISSING",
                    f"control role lacks required authorities: {definition['role']}",
                    task_id=thread["task_id"],
                    missing_authorities=missing,
                )

    if governance_mode == "federated_thin_kernel":
        missing_control_roles = sorted(FEDERATED_CONTROL_ROLES - control_role_names)
        unexpected_control_roles = sorted(control_role_names - FEDERATED_CONTROL_ROLES)
        if missing_control_roles:
            finding(
                "FEDERATED_CONTROL_ROLE_MISSING",
                "federated thin-kernel governance requires scheduler, runtime supervisor, and owner liaison roles",
                missing_roles=missing_control_roles,
            )
        if unexpected_control_roles:
            finding(
                "FEDERATED_CONTROL_ROLE_NOT_ALLOWED",
                "federated thin-kernel governance cannot add another persistent control role",
                unexpected_roles=unexpected_control_roles,
            )
        if "root_controller" in control_role_names:
            finding(
                "FEDERATED_ROOT_CONTROL_ROLE_FORBIDDEN",
                "federated thin-kernel governance cannot declare a persistent root control role",
            )
        if policy["migration_controller_role"] != "runtime_supervisor":
            finding(
                "FEDERATED_MIGRATION_CONTROLLER_ROLE_INVALID",
                "federated thin-kernel governance reserves migration control for runtime_supervisor",
                observed_role=policy["migration_controller_role"],
            )
        definitions_by_role = {
            definition["role"]: definition
            for definition in policy["control_roles"]
            if definition["role"] in FEDERATED_CONTROL_ROLES
        }
        for role in sorted(FEDERATED_CONTROL_ROLES):
            definition = definitions_by_role.get(role)
            if definition is not None and (
                not definition["required"] or definition["max_instances"] != 1
            ):
                finding(
                    "FEDERATED_CONTROL_ROLE_POLICY_INVALID",
                    "each thin-kernel role must be required with exactly one instance",
                    role=role,
                    required=definition["required"],
                    max_instances=definition["max_instances"],
                )
            minimum_authorities = FEDERATED_CONTROL_ROLE_MINIMUM_AUTHORITIES[role]
            if definition is not None:
                missing_policy_minimum = sorted(
                    minimum_authorities
                    - set(definition["required_authorities"])
                )
                if missing_policy_minimum:
                    finding(
                        "FEDERATED_CONTROL_POLICY_AUTHORITY_MINIMUM_MISSING",
                        "thin-kernel policy must declare each role's minimum authorities",
                        role=role,
                        missing_authorities=missing_policy_minimum,
                    )
            live_role_tasks = [
                thread
                for thread in threads
                if thread["role"] == role
                and thread["state"] in LIVE_CONTROL_STATES
            ]
            if len(live_role_tasks) != 1:
                finding(
                    "FEDERATED_LIVE_CONTROL_ROLE_COUNT_INVALID",
                    "each thin-kernel role requires exactly one live task",
                    role=role,
                    live_task_ids=[
                        thread["task_id"] for thread in live_role_tasks
                    ],
                    live_count=len(live_role_tasks),
                )
            for live_role_task in live_role_tasks:
                missing_runtime_minimum = sorted(
                    minimum_authorities
                    - set(live_role_task["authorities"])
                )
                if missing_runtime_minimum:
                    finding(
                        "FEDERATED_CONTROL_RUNTIME_AUTHORITY_MINIMUM_MISSING",
                        "a live thin-kernel task lacks its minimum operating authorities",
                        role=role,
                        task_id=live_role_task["task_id"],
                        missing_authorities=missing_runtime_minimum,
                    )
        for control_thread in (
            thread
            for thread in threads
            if thread["role"] in FEDERATED_CONTROL_ROLE_AUTHORITIES
        ):
            allowed_authorities = FEDERATED_CONTROL_ROLE_AUTHORITIES[
                control_thread["role"]
            ]
            observed_authorities = set(control_thread["authorities"])
            not_allowed = sorted(observed_authorities - allowed_authorities)
            if not_allowed:
                finding(
                    "FEDERATED_SCHEDULER_AUTHORITY_ESCALATION"
                    if control_thread["role"] == "scheduler"
                    else "FEDERATED_CONTROL_AUTHORITY_ESCALATION",
                    "a thin-kernel control role holds authority outside its role allowlist",
                    task_id=control_thread["task_id"],
                    role=control_thread["role"],
                    not_allowed_authorities=not_allowed,
                    explicitly_forbidden_authorities=sorted(
                        observed_authorities
                        & FEDERATED_SCHEDULER_FORBIDDEN_AUTHORITIES
                    ),
                )

    writer_counts: Counter[str] = Counter()
    for thread in threads:
        if (
            governance_mode == "federated_thin_kernel"
            and thread["project_id"] is None
            and thread["role"] not in FEDERATED_CONTROL_ROLES
            and thread["state"] != "retired"
        ):
            finding(
                "FEDERATED_NON_PROJECT_ROLE_NOT_ALLOWED",
                "a live projectless task outside the three thin-kernel roles could recreate a hidden controller",
                task_id=thread["task_id"],
                role=thread["role"],
                state=thread["state"],
            )
        if thread["role"] in control_role_names and (
            thread["project_id"] is not None or thread["writer"]
        ):
            finding(
                "CONTROL_PROJECT_EXECUTION_FORBIDDEN",
                "a declared control role cannot attach to a project or hold a writer lease",
                task_id=thread["task_id"],
                role=thread["role"],
                project_id=thread["project_id"],
                writer=thread["writer"],
            )
        if (
            governance_mode == "federated_thin_kernel"
            and thread["role"] == "root_controller"
            and thread["state"] != "retired"
        ):
            finding(
                "FEDERATED_ROOT_CONTROLLER_FORBIDDEN",
                "federated thin-kernel governance cannot retain a non-retired root controller",
                task_id=thread["task_id"],
                state=thread["state"],
            )
        if thread["role"] == "root_controller" and (
            thread["project_id"] is not None or thread["writer"]
        ):
            finding(
                "ROOT_PROJECT_EXECUTION_FORBIDDEN",
                "the root controller cannot attach to a project or hold its writer lease",
                task_id=thread["task_id"],
                project_id=thread["project_id"],
                writer=thread["writer"],
            )
        if thread["active_turn"] and thread["state"] != "active":
            finding(
                "ACTIVE_TURN_STATE_MISMATCH",
                "an active turn must use state=active",
                task_id=thread["task_id"],
                state=thread["state"],
            )
        if thread["active_turn"] and thread["capacity_class"] == "surge":
            dispatch_admission = thread.get("dispatch_admission")
            if (
                thread["role"] in control_role_names
                or thread["project_id"] is None
                or not thread["writer"]
            ):
                finding(
                    "SURGE_PROJECT_WRITER_REQUIRED",
                    "a surge slot can carry only an independent project writer action",
                    task_id=thread["task_id"],
                    role=thread["role"],
                    project_id=thread["project_id"],
                    writer=thread["writer"],
                )
            if dispatch_admission is None:
                finding(
                    "SURGE_ADMISSION_EVIDENCE_MISSING",
                    "an active surge task requires complete input and fresh ZERO admission evidence",
                    task_id=thread["task_id"],
                )
            else:
                if not dispatch_admission["input_complete"]:
                    finding(
                        "SURGE_INPUT_INCOMPLETE",
                        "a surge slot cannot carry an incomplete or filler action",
                        task_id=thread["task_id"],
                        action_id=dispatch_admission["action_id"],
                    )
                if dispatch_admission["admission_result"] != "ZERO":
                    finding(
                        "SURGE_FRESH_ADMISSION_REQUIRED",
                        "a surge action requires a fresh admission result of ZERO",
                        task_id=thread["task_id"],
                        action_id=dispatch_admission["action_id"],
                        admission_id=dispatch_admission["admission_id"],
                        admission_result=dispatch_admission["admission_result"],
                    )
                if dispatch_admission["writer_task_id"] != thread["task_id"]:
                    finding(
                        "SURGE_WRITER_IDENTITY_MISMATCH",
                        "surge admission must name the same independent project writer task",
                        task_id=thread["task_id"],
                        writer_task_id=dispatch_admission["writer_task_id"],
                    )
        if thread["provisional"] and thread["state"] not in {"queued", "handoff_only"}:
            finding(
                "PROVISIONAL_TASK_NOT_FROZEN",
                "a provisional task must remain queued or handoff_only",
                task_id=thread["task_id"],
                state=thread["state"],
            )
        if thread["writer"]:
            if thread["project_id"] is None:
                finding(
                    "WRITER_WITHOUT_PROJECT",
                    "a writer lease must belong to one project",
                    task_id=thread["task_id"],
                )
            else:
                writer_counts[thread["project_id"]] += 1
            if thread["provisional"]:
                finding(
                    "PROVISIONAL_WRITER",
                    "a provisional task cannot hold a writer lease",
                    task_id=thread["task_id"],
                )
        project_id = thread["project_id"]
        if project_id is not None and project_id not in projects:
            finding(
                "UNKNOWN_PROJECT_TASK",
                "task references a project absent from the manifest",
                task_id=thread["task_id"],
                project_id=project_id,
            )
        elif (
            project_id is not None
            and governance_mode == "federated_thin_kernel"
        ):
            unexpected_authorities = sorted(
                set(thread["authorities"])
                - set(projects[project_id]["authorities"])
            )
            if unexpected_authorities:
                finding(
                    "PROJECT_AUTHORITY_OUTSIDE_MANIFEST",
                    "project task authorities must remain inside the manifest authority envelope",
                    task_id=thread["task_id"],
                    project_id=project_id,
                    unexpected_authorities=unexpected_authorities,
                )
            owner_task_id = projects[project_id]["owner_task_id"]
            owner_only_authorities = sorted(
                set(thread["authorities"])
                & FEDERATED_PROJECT_OWNER_ONLY_AUTHORITIES
            )
            if (
                governance_mode == "federated_thin_kernel"
                and owner_only_authorities
                and thread["task_id"] != owner_task_id
            ):
                finding(
                    "PROJECT_OWNER_ONLY_AUTHORITY_HELD_BY_NON_OWNER",
                    "project-local decision, admission, and fresh-round authorities belong only to the manifest owner task",
                    task_id=thread["task_id"],
                    project_id=project_id,
                    manifest_owner_task_id=owner_task_id,
                    owner_only_authorities=owner_only_authorities,
                )
        context_health = thread.get("context_health")
        if context_health is None:
            continue
        pressure = context_health["pressure"]
        context_pressure_counts[pressure] += 1
        summary_quality = context_health["summary_quality"]
        if context_health["compaction_observed"] and summary_quality is None:
            finding(
                "CONTEXT_SUMMARY_QUALITY_MISSING",
                "a compacted task requires a short/accurate/usable summary audit",
                task_id=thread["task_id"],
                pressure=pressure,
            )
        failed_summary_gates = (
            [
                field
                for field in SUMMARY_QUALITY_FIELDS
                if summary_quality is not None and not summary_quality[field]
            ]
            if summary_quality is not None
            else []
        )
        if failed_summary_gates and pressure != "renewal_required":
            finding(
                "CONTEXT_PRESSURE_UNDERCLASSIFIED",
                "failed summary-quality gates require renewal_required context pressure",
                task_id=thread["task_id"],
                pressure=pressure,
                failed_summary_gates=failed_summary_gates,
            )
        if pressure == "renewal_required" and not context_health["signals"]:
            finding(
                "CONTEXT_RENEWAL_WITHOUT_SIGNAL",
                "renewal_required needs at least one authoritative pressure signal",
                task_id=thread["task_id"],
            )
        if pressure == "renewal_required" and not context_health["controller_notified"]:
            finding(
                "CONTEXT_RENEWAL_NOTIFICATION_REQUIRED",
                "the scheduler must notify the sole migration controller once",
                task_id=thread["task_id"],
                controller_task_id=topology["migration"]["controller_task_id"],
                signals=context_health["signals"],
                failed_summary_gates=failed_summary_gates,
            )
        if (
            context_health["controller_notified"]
            and context_health["notification_target_task_id"]
            != topology["migration"]["controller_task_id"]
        ):
            finding(
                "CONTEXT_RENEWAL_WRONG_NOTIFICATION_TARGET",
                "context-renewal notification must target the sole migration controller",
                task_id=thread["task_id"],
                expected_controller_task_id=topology["migration"]["controller_task_id"],
                observed_notification_target_task_id=context_health[
                    "notification_target_task_id"
                ],
                notification_id=context_health["notification_id"],
            )

    for worker in nested_workers:
        if worker["capacity_class"] == "surge":
            finding(
                "SURGE_NESTED_WORKER_FORBIDDEN",
                "expanded capacity is reserved for independent project tasks, never nested workers",
                worker_id=worker["worker_id"],
                controller_task_id=worker["controller_task_id"],
                active=worker["active"],
            )
        controller = tasks.get(worker["controller_task_id"])
        if controller is None:
            finding(
                "NESTED_WORKER_CONTROLLER_MISSING",
                "a nested worker must reference an authoritative controller task",
                worker_id=worker["worker_id"],
                controller_task_id=worker["controller_task_id"],
            )
        else:
            if worker["project_id"] is not None and (
                controller["role"] == "root_controller"
                or controller["project_id"] != worker["project_id"]
            ):
                finding(
                    "PROJECT_WORKER_WRONG_CONTROLLER",
                    "project work must be controlled by that project's independent task, never Root",
                    worker_id=worker["worker_id"],
                    project_id=worker["project_id"],
                    controller_task_id=worker["controller_task_id"],
                    controller_role=controller["role"],
                    controller_project_id=controller["project_id"],
                )
            if worker["active"] and not controller["active_turn"]:
                finding(
                    "ACTIVE_NESTED_WORKER_CONTROLLER_INACTIVE",
                    "an active nested worker requires an active controller turn",
                    worker_id=worker["worker_id"],
                    controller_task_id=worker["controller_task_id"],
                )
            if worker["host_id"] != controller["host_id"]:
                finding(
                    "NESTED_WORKER_HOST_MISMATCH",
                    "a nested worker must run on its declared controller host",
                    worker_id=worker["worker_id"],
                    controller_task_id=worker["controller_task_id"],
                    worker_host_id=worker["host_id"],
                    controller_host_id=controller["host_id"],
                )
        if worker["writer"]:
            if worker["project_id"] is None:
                finding(
                    "NESTED_WRITER_WITHOUT_PROJECT",
                    "a nested writer lease must belong to one project",
                    worker_id=worker["worker_id"],
                )
            else:
                writer_counts[worker["project_id"]] += 1

    if len(active_surge_threads) < required_surge_slot_count:
        finding(
            "SURGE_SLOT_EVIDENCE_MISSING",
            "active load beyond the baseline dispatch envelope requires eligible surge project tasks",
            baseline_max_active_turns=baseline_limit,
            reserved_control_slots=policy["reserved_control_slots"],
            required_surge_slot_count=required_surge_slot_count,
            active_surge_slot_count=len(active_surge_threads),
            active_execution_unit_count=active_execution_unit_count,
        )

    stage_closeout_status_counts: Counter[str] = Counter()
    for closeout in stage_closeouts:
        stage_closeout_status_counts[closeout["status"]] += 1
        project_id = closeout["project_id"]
        project_task = tasks.get(closeout["project_task_id"])
        if project_id not in projects:
            finding(
                "STAGE_CLOSEOUT_UNKNOWN_PROJECT",
                "stage closeout references a project absent from the manifest",
                stage_id=closeout["stage_id"],
                project_id=project_id,
            )
        if project_task is None:
            finding(
                "STAGE_CLOSEOUT_PROJECT_TASK_MISSING",
                "stage closeout requires the existing project task",
                stage_id=closeout["stage_id"],
                project_task_id=closeout["project_task_id"],
            )
        else:
            if project_task["role"] == "root_controller":
                finding(
                    "STAGE_CLOSEOUT_ROOT_EXECUTOR_FORBIDDEN",
                    "Root may arbitrate the closeout but cannot commit, push, or merge project work",
                    stage_id=closeout["stage_id"],
                    project_task_id=closeout["project_task_id"],
                )
            if project_task["project_id"] != project_id:
                finding(
                    "STAGE_CLOSEOUT_PROJECT_TASK_MISMATCH",
                    "stage closeout task must own the declared project",
                    stage_id=closeout["stage_id"],
                    project_id=project_id,
                    task_project_id=project_task["project_id"],
                )
            if project_task["host_id"] != closeout["host_id"]:
                finding(
                    "STAGE_CLOSEOUT_HOST_MISMATCH",
                    "stage closeout host must match its project task",
                    stage_id=closeout["stage_id"],
                    closeout_host_id=closeout["host_id"],
                    task_host_id=project_task["host_id"],
                )
            if closeout["status"] == "in_progress" and not project_task["writer"]:
                finding(
                    "STAGE_CLOSEOUT_WRITER_REQUIRED",
                    "an in-progress project closeout requires that project's writer lease",
                    stage_id=closeout["stage_id"],
                    project_task_id=closeout["project_task_id"],
                )

        blocking_conditions: list[str] = []
        if not closeout["identity_verified"]:
            blocking_conditions.append("identity_unverified")
            finding(
                "STAGE_CLOSEOUT_IDENTITY_UNVERIFIED",
                "project task, branch, target, and host identity must be verified before mutation",
                stage_id=closeout["stage_id"],
            )
        if not closeout["worktree_scope_clean"]:
            blocking_conditions.append("dirty_worktree")
            finding(
                "STAGE_CLOSEOUT_DIRTY_WORKTREE",
                "foreign or unowned dirty paths stop closeout until retained state is resolved",
                stage_id=closeout["stage_id"],
            )
        if not closeout["conflict_free"]:
            blocking_conditions.append("conflict")
            finding(
                "STAGE_CLOSEOUT_CONFLICT",
                "a merge conflict stops the formal closeout without force merging",
                stage_id=closeout["stage_id"],
            )
        if blocking_conditions and closeout["status"] != "stopped":
            finding(
                "STAGE_CLOSEOUT_STOP_REQUIRED",
                "identity, worktree, or conflict blockers require status=stopped",
                stage_id=closeout["stage_id"],
                blockers=blocking_conditions,
            )
        if (
            closeout["worktree_merge_required"]
            and closeout["branch"] == closeout["target_branch"]
        ):
            finding(
                "STAGE_CLOSEOUT_BRANCH_TARGET_AMBIGUOUS",
                "a required worktree merge needs distinct source and target branches",
                stage_id=closeout["stage_id"],
                branch=closeout["branch"],
                target_branch=closeout["target_branch"],
            )

        step_results = closeout["step_results"]
        first_nonzero_step = closeout["first_nonzero_step"]
        observed_nonzero_steps = [
            step for step in STAGE_CLOSEOUT_STEPS if step_results[step] == "NONZERO"
        ]
        if first_nonzero_step is None and observed_nonzero_steps:
            finding(
                "STAGE_CLOSEOUT_NONZERO_MARKER_MISSING",
                "a nonzero step requires an exact first_nonzero_step marker",
                stage_id=closeout["stage_id"],
                nonzero_steps=observed_nonzero_steps,
            )
        if first_nonzero_step is not None:
            finding(
                "STAGE_CLOSEOUT_FIRST_NONZERO",
                "the formal stage closeout stopped at its first nonzero step",
                stage_id=closeout["stage_id"],
                first_nonzero_step=first_nonzero_step,
            )
            if step_results[first_nonzero_step] != "NONZERO":
                finding(
                    "STAGE_CLOSEOUT_NONZERO_MARKER_MISMATCH",
                    "first_nonzero_step must identify a step whose result is NONZERO",
                    stage_id=closeout["stage_id"],
                    first_nonzero_step=first_nonzero_step,
                    observed_result=step_results[first_nonzero_step],
                )
            first_index = STAGE_CLOSEOUT_STEPS.index(first_nonzero_step)
            continued_steps = [
                step
                for step in STAGE_CLOSEOUT_STEPS[first_index + 1 :]
                if step_results[step] != "UNEXECUTED"
            ]
            if continued_steps:
                finding(
                    "STAGE_CLOSEOUT_CONTINUED_AFTER_NONZERO",
                    "all steps after the first nonzero must remain UNEXECUTED",
                    stage_id=closeout["stage_id"],
                    continued_steps=continued_steps,
                )
            if closeout["status"] != "stopped":
                finding(
                    "STAGE_CLOSEOUT_NONZERO_NOT_STOPPED",
                    "a first nonzero requires status=stopped",
                    stage_id=closeout["stage_id"],
                    status=closeout["status"],
                )

        if step_results["commit"] == "PASS" and closeout["commit_sha"] is None:
            finding(
                "STAGE_CLOSEOUT_COMMIT_READBACK_MISSING",
                "a passing commit step requires its exact commit SHA",
                stage_id=closeout["stage_id"],
            )
        if step_results["push"] == "PASS" and closeout["push_readback_sha"] is None:
            finding(
                "STAGE_CLOSEOUT_PUSH_READBACK_MISSING",
                "a passing push step requires remote SHA readback",
                stage_id=closeout["stage_id"],
            )
        if step_results["merge"] == "PASS" and closeout["merge_readback_sha"] is None:
            finding(
                "STAGE_CLOSEOUT_MERGE_READBACK_MISSING",
                "a passing merge step requires target-branch SHA readback",
                stage_id=closeout["stage_id"],
            )

        if closeout["status"] == "complete":
            incomplete_steps = [
                step
                for step in ("evidence", "test", "diff", "readback", "commit", "push")
                if step_results[step] != "PASS"
            ]
            if step_results["build"] not in {"PASS", "NOT_REQUIRED"}:
                incomplete_steps.append("build")
            expected_merge_results = (
                {"PASS"} if closeout["worktree_merge_required"] else {"PASS", "NOT_REQUIRED"}
            )
            if step_results["merge"] not in expected_merge_results:
                incomplete_steps.append("merge")
            if incomplete_steps or first_nonzero_step is not None:
                finding(
                    "STAGE_CLOSEOUT_INCOMPLETE",
                    "complete requires evidence/test/build/diff/readback then commit/push/merge closure",
                    stage_id=closeout["stage_id"],
                    incomplete_steps=incomplete_steps,
                )

    for project_id, count in sorted(writer_counts.items()):
        if count > policy["max_writers_per_project"]:
            finding(
                "PROJECT_WRITER_LIMIT_EXCEEDED",
                "project has more concurrent writer leases than allowed",
                project_id=project_id,
                writer_count=count,
                max_writers_per_project=policy["max_writers_per_project"],
                task_ids=[
                    thread["task_id"]
                    for thread in threads
                    if thread["project_id"] == project_id and thread["writer"]
                ]
                + [
                    worker["worker_id"]
                    for worker in nested_workers
                    if worker["project_id"] == project_id and worker["writer"]
                ],
            )

    for project_id, project in projects.items():
        owner_task_id = project["owner_task_id"]
        federated_owner_required = (
            governance_mode == "federated_thin_kernel"
            and project["state"] not in {"frozen", "complete"}
        )
        if federated_owner_required:
            missing_manifest_owner_authorities = sorted(
                FEDERATED_PROJECT_OWNER_ONLY_AUTHORITIES
                - set(project["authorities"])
            )
            if missing_manifest_owner_authorities:
                finding(
                    "FEDERATED_PROJECT_AUTHORITY_MINIMUM_MISSING",
                    "an unfinished federated project manifest must grant its owner local decision, admission, and fresh-round authority",
                    project_id=project_id,
                    missing_authorities=missing_manifest_owner_authorities,
                )
            if owner_task_id is None:
                finding(
                    "FEDERATED_PROJECT_OWNER_REQUIRED",
                    "an unfinished federated project requires one manifest owner task",
                    project_id=project_id,
                    project_state=project["state"],
                )
        if owner_task_id is None:
            continue
        owner = tasks.get(owner_task_id)
        if owner is None:
            finding(
                "OWNER_TASK_MISSING",
                "manifest owner_task_id is absent from the topology",
                project_id=project_id,
                owner_task_id=owner_task_id,
            )
            continue
        if owner["project_id"] != project_id:
            finding(
                "OWNER_PROJECT_MISMATCH",
                "manifest owner task is attached to a different project",
                project_id=project_id,
                owner_task_id=owner_task_id,
                observed_project_id=owner["project_id"],
            )
        owner_runtime_required = (
            governance_mode != "federated_thin_kernel" or federated_owner_required
        )
        if owner_runtime_required and not owner["writer"]:
            finding(
                "OWNER_WITHOUT_WRITER_LEASE",
                "manifest owner task must hold the project's writer lease",
                project_id=project_id,
                owner_task_id=owner_task_id,
            )
        if owner_runtime_required and owner["state"] not in LIVE_CONTROL_STATES:
            finding(
                "OWNER_TASK_NOT_LIVE",
                "manifest owner task must be live to exercise project autonomy",
                project_id=project_id,
                owner_task_id=owner_task_id,
                state=owner["state"],
            )
        if federated_owner_required:
            missing_owner_authorities = sorted(
                FEDERATED_PROJECT_OWNER_ONLY_AUTHORITIES
                - set(owner["authorities"])
            )
            if missing_owner_authorities:
                finding(
                    "FEDERATED_PROJECT_OWNER_AUTHORITY_MINIMUM_MISSING",
                    "the live federated project owner lacks local decision, admission, or fresh-round authority",
                    project_id=project_id,
                    owner_task_id=owner_task_id,
                    missing_authorities=missing_owner_authorities,
                )
        if owner["host_id"] != project["host_id"]:
            finding(
                "OWNER_HOST_MISMATCH",
                "manifest owner task is on a different host",
                project_id=project_id,
                owner_task_id=owner_task_id,
                expected_host_id=project["host_id"],
                observed_host_id=owner["host_id"],
            )
        expected_root = canonical_root(project["root"], project["host_scope"])
        observed_roots = [owner["root"]]
        if owner.get("canonical_project_root") is not None:
            observed_roots.append(owner["canonical_project_root"])
        root_matches = any(
            expected_root == canonical_root(root, project["host_scope"])
            for root in observed_roots
        )
        if not root_matches:
            finding(
                "OWNER_ROOT_MISMATCH",
                "manifest root matches neither the execution root nor its canonical project root",
                project_id=project_id,
                owner_task_id=owner_task_id,
                expected_root=project["root"],
                observed_execution_root=owner["root"],
                observed_canonical_project_root=owner.get("canonical_project_root"),
            )

    migration = topology["migration"]
    controller = tasks.get(migration["controller_task_id"])
    if controller is None:
        finding(
            "MIGRATION_CONTROLLER_MISSING",
            "migration controller task is absent from the topology",
            controller_task_id=migration["controller_task_id"],
        )
    elif controller["role"] != policy["migration_controller_role"]:
        finding(
            "MIGRATION_CONTROLLER_ROLE_MISMATCH",
            "migration controller task has the wrong control role",
            controller_task_id=migration["controller_task_id"],
            expected_role=policy["migration_controller_role"],
            observed_role=controller["role"],
        )
    elif (
        governance_mode == "federated_thin_kernel"
        and controller["state"] not in LIVE_CONTROL_STATES
    ):
        finding(
            "FEDERATED_MIGRATION_CONTROLLER_NOT_LIVE",
            "the federated migration controller must be a live runtime supervisor",
            controller_task_id=migration["controller_task_id"],
            state=controller["state"],
        )
    target_task_id = migration["active_target_task_id"]
    if migration["lock_held"] and target_task_id is None:
        finding(
            "MIGRATION_LOCK_WITHOUT_TARGET",
            "a held migration lock requires one active target",
        )
    if not migration["lock_held"] and target_task_id is not None:
        finding(
            "MIGRATION_TARGET_WITHOUT_LOCK",
            "an active migration target requires the migration lock",
            active_target_task_id=target_task_id,
        )
    if target_task_id is not None and target_task_id not in tasks:
        finding(
            "MIGRATION_TARGET_MISSING",
            "active migration target is absent from the topology",
            active_target_task_id=target_task_id,
        )

    lifecycle = topology.get("control_lifecycle")
    if lifecycle is not None:
        phase = lifecycle["phase"]
        controller_task_id_field = (
            "controller_task_id"
            if topology_governance_mode == "federated_thin_kernel"
            else "root_task_id"
        )
        expected_controller_role = (
            "scheduler"
            if topology_governance_mode == "federated_thin_kernel"
            else "root_controller"
        )
        controller_task_id = lifecycle[controller_task_id_field]
        control_task = tasks.get(controller_task_id)
        controller_identity_evidence = {
            controller_task_id_field: controller_task_id
        }
        work_lease = lifecycle.get("work_lease")
        qualifying_work_evidence = False
        if isinstance(work_lease, dict):
            progress_kind = work_lease["progress_kind"]
            ledger_delta_proved = (
                work_lease["latest_event_seq"] > work_lease["baseline_event_seq"]
                and bool(work_lease["evidence_ids"])
            )
            admission_proved = (
                work_lease["admission_result"] == "ZERO"
                and work_lease["admission_id"] is not None
                and ledger_delta_proved
                and work_lease["admission_id"] in work_lease["evidence_ids"]
            )
            dispatch_proved = (
                admission_proved
                and work_lease["dispatched_task_id"] is not None
                and work_lease["dispatched_task_id"] in tasks
            )
            qualifying_work_evidence = (
                (progress_kind == "admitted" and admission_proved)
                or (progress_kind == "dispatched" and dispatch_proved)
                or (progress_kind == "evidence_delta" and ledger_delta_proved)
                or (
                    progress_kind == "terminal"
                    and ledger_delta_proved
                    and work_lease["action_terminal"]
                )
            )
            if progress_kind != "none" and not qualifying_work_evidence:
                finding(
                    "WORK_LEASE_EVIDENCE_INVALID",
                    "declared work progress is not backed by its required evidence",
                    action_id=work_lease["action_id"],
                    progress_kind=progress_kind,
                )
            if (
                work_lease["dispatched_task_id"] is not None
                and work_lease["dispatched_task_id"] not in tasks
            ):
                finding(
                    "WORK_LEASE_DISPATCH_TARGET_MISSING",
                    "a dispatched work lease must reference an authoritative task",
                    action_id=work_lease["action_id"],
                    dispatched_task_id=work_lease["dispatched_task_id"],
                )
            if work_lease["lease_renewed"] and not qualifying_work_evidence:
                finding(
                    "WORK_LEASE_RENEWED_WITHOUT_EVIDENCE",
                    "an active work lease cannot renew without qualifying progress evidence",
                    action_id=work_lease["action_id"],
                    progress_kind=progress_kind,
                )
        incomplete_project_ids = [
            project_id
            for project_id, project in projects.items()
            if project["state"] != "complete"
        ]
        if control_task is None:
            finding(
                "CONTROL_LIFECYCLE_CONTROLLER_MISSING"
                if governance_mode == "federated_thin_kernel"
                else "CONTROL_LIFECYCLE_ROOT_MISSING",
                f"control lifecycle {controller_task_id_field} is absent from the topology",
                **controller_identity_evidence,
            )
        elif control_task["role"] != expected_controller_role:
            finding(
                "CONTROL_LIFECYCLE_CONTROLLER_ROLE_MISMATCH"
                if governance_mode == "federated_thin_kernel"
                else "CONTROL_LIFECYCLE_ROOT_ROLE_MISMATCH",
                f"control lifecycle must reference the {expected_controller_role}",
                **controller_identity_evidence,
                observed_role=control_task["role"],
            )
        if phase == "running" and not lifecycle["safe_next_action"]:
            finding(
                "RUNNING_WITHOUT_SAFE_NEXT_ACTION",
                "running control state requires one safe next action",
                **controller_identity_evidence,
            )
        if phase == "running" and work_lease is None:
            finding(
                "RUNNING_WITHOUT_WORK_LEASE",
                "running control state requires an evidence-backed work lease",
                **controller_identity_evidence,
            )
        if phase == "running" and work_lease is not None:
            if not qualifying_work_evidence:
                finding(
                    "RUNNING_WITHOUT_WORK_EVIDENCE",
                    "running control state must admit, dispatch, advance evidence, or terminate one action",
                    **controller_identity_evidence,
                    action_id=work_lease["action_id"],
                )
            if work_lease["action_terminal"]:
                finding(
                    "STALE_SAFE_NEXT_ACTION",
                    "a terminal action cannot remain the running safe next action",
                    action_id=work_lease["action_id"],
                )
            if (
                lifecycle["automation_status"] == "ACTIVE"
                and not work_lease["lease_renewed"]
            ):
                finding(
                    "ACTIVE_AUTOMATION_WITHOUT_RENEWED_WORK_LEASE",
                    "an active running monitor requires a renewed work lease",
                    action_id=work_lease["action_id"],
                    automation_id=lifecycle["automation_id"],
                )
        if phase == "waiting" and not (
            lifecycle["pending_wait_id"] or lifecycle["pending_owner_request_id"]
        ):
            finding(
                "WAITING_WITHOUT_PENDING_EVENT",
                "waiting control state requires an identified wait or owner request",
                **controller_identity_evidence,
            )
        if (
            phase == "waiting"
            and lifecycle["automation_status"] == "ACTIVE"
            and lifecycle["consecutive_no_change"] >= 1
            and contract_version != PROJECT_TASK_CONTRACT_V2_5
        ):
            finding(
                "WAITING_AUTOMATION_NOT_PAUSED_AFTER_EMPTY_CHECK",
                "a waiting monitor must pause after its first empty check unless a new bounded poll is freshly admitted",
                pending_wait_id=lifecycle["pending_wait_id"],
                consecutive_no_change=lifecycle["consecutive_no_change"],
                automation_id=lifecycle["automation_id"],
            )
        if phase == "complete" and incomplete_project_ids:
            finding(
                "CONTROL_COMPLETE_WITH_INCOMPLETE_PROJECTS",
                "control state cannot be complete while portfolio projects remain incomplete",
                incomplete_project_ids=incomplete_project_ids,
            )
        if phase in {"complete", "stopped"} and lifecycle["safe_next_action"]:
            finding(
                "TERMINAL_CONTROL_WITH_SAFE_NEXT_ACTION",
                "complete or stopped control state cannot retain a safe next action",
                phase=phase,
            )
        if (
            incomplete_project_ids
            and phase == "running"
            and lifecycle["consecutive_no_change"] >= 1
            and lifecycle["pending_wait_id"] is None
            and lifecycle["pending_owner_request_id"] is None
        ):
            finding(
                "CONTROL_STALL_OWNER_ATTENTION_REQUIRED",
                "one empty running monitor check without an identified wait requires owner attention",
                consecutive_no_change=lifecycle["consecutive_no_change"],
                incomplete_project_ids=incomplete_project_ids,
            )
        if lifecycle["closure_delivered"]:
            liaison = tasks.get(lifecycle["closure_owner_liaison_task_id"])
            if liaison is None or liaison["role"] != "owner_liaison":
                finding(
                    "CONTROL_CLOSURE_WRONG_LIAISON",
                    "control closure must be delivered to the declared owner liaison",
                    closure_owner_liaison_task_id=lifecycle[
                        "closure_owner_liaison_task_id"
                    ],
                    observed_role=None if liaison is None else liaison["role"],
                )
        if lifecycle["automation_status"] == "PAUSED":
            if not lifecycle["closure_delivered"]:
                finding(
                    "PAUSED_AUTOMATION_WITHOUT_OWNER_NOTICE",
                    "a monitor may pause only after an owner-liaison notice is delivered",
                    phase=phase,
                    closure_id=lifecycle["closure_id"],
                    automation_id=lifecycle["automation_id"],
                )
            if not lifecycle["pause_notice_delivered_before_pause"]:
                finding(
                    "PAUSE_BEFORE_OWNER_NOTICE",
                    "the delivered owner notice must be read back before the monitor pauses",
                    phase=phase,
                    closure_id=lifecycle["closure_id"],
                    automation_id=lifecycle["automation_id"],
                )
            if lifecycle["automation_notification_policy"] != "ALL":
                finding(
                    "PAUSE_NOTICE_NOT_USER_VISIBLE",
                    "a pause or stop notice must not be limited to failed runs",
                    phase=phase,
                    automation_id=lifecycle["automation_id"],
                    automation_notification_policy=lifecycle[
                        "automation_notification_policy"
                    ],
                )
        if phase in {"owner_attention", "complete", "stopped"}:
            if not lifecycle["closure_delivered"]:
                finding(
                    "OWNER_LIAISON_HANDOFF_REQUIRED",
                    "attention or terminal control state requires one delivered owner-liaison handoff",
                    phase=phase,
                    closure_id=lifecycle["closure_id"],
                )
            if lifecycle["automation_status"] != "PAUSED":
                finding(
                    "TERMINAL_AUTOMATION_NOT_PAUSED",
                    "attention or terminal control state requires the monitor automation to pause",
                    phase=phase,
                    automation_id=lifecycle["automation_id"],
                )

    return {
        "schema_version": TOPOLOGY_AUDIT_SCHEMA,
        "ok": not findings,
        "portfolio_id": manifest["portfolio_id"],
        "governance_mode": governance_mode,
        "manifest_governance_mode": manifest_governance_mode,
        "topology_governance_mode": topology_governance_mode,
        "observed_at_utc": topology["observed_at_utc"],
        "thread_count": len(threads),
        "active_turn_count": len(active_threads),
        "active_nested_worker_count": len(active_nested_workers),
        "active_execution_unit_count": active_execution_unit_count,
        "configured_max_active_turns": configured_max_active_turns,
        "effective_max_active_turns": effective_limit,
        "runtime_reported_max_active_turns": runtime_reported_max_active_turns,
        "baseline_max_active_turns": baseline_limit,
        "required_surge_slot_count": required_surge_slot_count,
        "active_surge_slot_count": len(active_surge_threads),
        "reserved_control_slots": policy["reserved_control_slots"],
        "new_dispatch_budget": new_dispatch_budget,
        "stage_closeout_count": len(stage_closeouts),
        "stage_closeout_status_counts": dict(sorted(stage_closeout_status_counts.items())),
        "writer_counts": dict(sorted(writer_counts.items())),
        "context_pressure_counts": dict(sorted(context_pressure_counts.items())),
        "control_phase": None if lifecycle is None else lifecycle["phase"],
        "finding_count": len(findings),
        "findings": findings,
    }


def canonical_root(path: str, scope: str) -> str:
    if scope == "local":
        return os.path.normcase(os.path.abspath(path)).rstrip("\\/")
    return path.rstrip("/")


def evaluate_admission(plan: dict[str, Any], readback: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    stopped = False
    first_nonzero: str | None = None
    outcome = "PASS"

    def add(name: str, passed: bool, failure_class: str, reason: str) -> None:
        nonlocal stopped, first_nonzero, outcome
        if stopped:
            checks.append(
                {"name": name, "status": "UNEXECUTED", "reason": "earlier first-nonzero"}
            )
        elif passed:
            checks.append({"name": name, "status": "PASS", "reason": reason})
        else:
            checks.append(
                {
                    "name": name,
                    "status": "NONZERO",
                    "reason": reason,
                    "outcome_class": failure_class,
                }
            )
            stopped = True
            first_nonzero = name
            outcome = failure_class

    plan_fields = [
        "project_id",
        "action_id",
        "action_class",
        "expected_host_scope",
        "expected_host_id",
        "expected_root",
        "required_authorities",
        "portfolio_lane_state",
        "external_mutation",
        "user_authorized",
        "continuation",
        "transport_model_override_present",
        "transport_effort_override_present",
        "migration_fence_required",
    ]
    readback_fields = [
        "project_id",
        "authoritative",
        "observed_host_scope",
        "observed_host_id",
        "observed_root",
        "granted_authorities",
    ]
    missing = require_fields(plan, plan_fields, "plan") + require_fields(
        readback, readback_fields, "readback"
    )
    shape_errors = list(missing)
    if not missing:
        for field in (
            "project_id",
            "action_id",
            "action_class",
            "expected_host_id",
            "expected_root",
        ):
            if not is_non_empty_string(plan[field]):
                shape_errors.append(f"plan: {field} must be a non-empty string")
        if not is_enum_value(plan["expected_host_scope"], HOST_SCOPES):
            shape_errors.append("plan: expected_host_scope is invalid")
        if not is_enum_value(plan["portfolio_lane_state"], PROJECT_STATES):
            shape_errors.append("plan: portfolio_lane_state is invalid")
        if not is_string_list(plan["required_authorities"]):
            shape_errors.append("plan: required_authorities must be an array of strings")
        for field in ADMISSION_BOOLEAN_FIELDS:
            if not isinstance(plan[field], bool):
                shape_errors.append(f"plan: {field} must be boolean")
        if not is_non_empty_string(readback["project_id"]):
            shape_errors.append("readback: project_id must be a non-empty string")
        if not isinstance(readback["authoritative"], bool):
            shape_errors.append("readback: authoritative must be boolean")
        if not is_enum_value(readback["observed_host_scope"], HOST_SCOPES):
            shape_errors.append("readback: observed_host_scope is invalid")
        for field in ("observed_host_id", "observed_root"):
            if not is_non_empty_string(readback[field]):
                shape_errors.append(f"readback: {field} must be a non-empty string")
        if not is_string_list(readback["granted_authorities"]):
            shape_errors.append(
                "readback: granted_authorities must be an array of strings"
            )
    add(
        "input_shape",
        not shape_errors,
        "BLOCKED_CONFIG",
        "; ".join(shape_errors) or "shape valid",
    )

    if shape_errors:
        for name in (
            "authoritative_readback",
            "project_match",
            "host_match",
            "root_match",
            "authority_present",
            "lane_allows_action",
            "external_mutation_authorized",
            "continuation_omits_overrides",
            "migration_fence_valid",
        ):
            add(name, False, "BLOCKED_CONFIG", "input shape unavailable")
    else:
        add(
            "authoritative_readback",
            bool(readback["authoritative"]),
            "BLOCKED_RUNTIME_READBACK",
            "runtime-owned readback required",
        )
        add(
            "project_match",
            plan["project_id"] == readback["project_id"],
            "BLOCKED_PROJECT_IDENTITY",
            "project IDs match",
        )
        add(
            "host_match",
            plan["expected_host_scope"] == readback["observed_host_scope"]
            and plan["expected_host_id"] == readback["observed_host_id"],
            "BLOCKED_HOST_IDENTITY",
            "host scope and ID match",
        )
        root_match = canonical_root(
            str(plan["expected_root"]), str(plan["expected_host_scope"])
        ) == canonical_root(str(readback["observed_root"]), str(plan["expected_host_scope"]))
        add("root_match", root_match, "BLOCKED_HOST_IDENTITY", "canonical roots match")
        granted = set(readback["granted_authorities"])
        required = set(plan["required_authorities"])
        add(
            "authority_present",
            required <= granted,
            "BLOCKED_MISSING_AUTHORITY",
            "required authorities are granted",
        )
        lane_ok = plan["portfolio_lane_state"] != "frozen" or plan["action_class"] in {
            "control_read",
            "control_write",
        }
        add("lane_allows_action", lane_ok, "BLOCKED_FROZEN_LANE", "lane permits action")
        add(
            "external_mutation_authorized",
            not plan["external_mutation"] or bool(plan["user_authorized"]),
            "BLOCKED_MISSING_AUTHORITY",
            "external mutation has explicit user authorization",
        )
        continuation_ok = not plan["continuation"] or (
            not plan["transport_model_override_present"]
            and not plan["transport_effort_override_present"]
        )
        add(
            "continuation_omits_overrides",
            continuation_ok,
            "BLOCKED_CONFIG",
            "continuation transport preserves frozen settings",
        )
        fence = readback.get("migration_fence")
        fence_ok = not plan["migration_fence_required"] or (
            isinstance(fence, dict)
            and bool(fence.get("controller_task_id"))
            and bool(fence.get("fence_token"))
        )
        add(
            "migration_fence_valid",
            fence_ok,
            "BLOCKED_MIGRATION_FENCE",
            "migration fence is present when required",
        )

    return {
        "schema_version": "codex-project-pilot-admission/1",
        "formal_result": "NONZERO" if stopped else "ZERO",
        "outcome_class": outcome,
        "first_nonzero_check": first_nonzero,
        "checks": checks,
        "unexecuted_checks": [c["name"] for c in checks if c["status"] == "UNEXECUTED"],
    }


def event_hash(event: dict[str, Any]) -> str:
    without_hash = {key: value for key, value in event.items() if key != "event_hash"}
    return sha256_text(canonical_json(without_hash))


def validate_event(event: Any, *, stored: bool) -> list[str]:
    if not isinstance(event, dict):
        return ["event must be an object"]
    required = [
        "schema_version",
        "event_id",
        "event_time_utc",
        "portfolio_id",
        "project_id",
        "action_id",
        "event_type",
        "actor",
        "payload",
    ]
    if stored:
        required.extend(["seq", "prev_event_hash", "event_hash"])
    errors = require_fields(event, required, "event")
    if errors:
        return errors
    if event["schema_version"] != EVENT_SCHEMA:
        errors.append(f"event: schema_version must be {EVENT_SCHEMA}")
    for field in (
        "event_id",
        "event_time_utc",
        "portfolio_id",
        "project_id",
        "action_id",
        "event_type",
        "actor",
    ):
        if not is_non_empty_string(event[field]):
            errors.append(f"event: {field} must be a non-empty string")
    if not isinstance(event["payload"], dict):
        errors.append("event: payload must be an object")
    if stored:
        if not isinstance(event["seq"], int) or isinstance(event["seq"], bool):
            errors.append("event: seq must be an integer")
        if not is_lower_hex(event["prev_event_hash"], 64):
            errors.append("event: prev_event_hash must be 64 lowercase hex characters")
        if not is_lower_hex(event["event_hash"], 64):
            errors.append("event: event_hash must be 64 lowercase hex characters")
    return errors


def verify_ledger(path: Path) -> dict[str, Any]:
    previous = ZERO_HASH
    count = 0
    if path.exists():
        try:
            lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        except OSError as exc:
            raise ControlError(f"cannot read ledger {path}: {exc}") from exc
        for index, line in enumerate(lines):
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ControlError(f"ledger JSON invalid at seq {index}: {exc}") from exc
            event_errors = validate_event(event, stored=True)
            if event_errors:
                raise ControlError(
                    f"ledger event invalid at seq {index}: {'; '.join(event_errors)}"
                )
            if event.get("seq") != index:
                raise ControlError(f"ledger seq mismatch at index {index}")
            if event.get("prev_event_hash") != previous:
                raise ControlError(f"ledger previous hash mismatch at seq {index}")
            calculated = event_hash(event)
            if event.get("event_hash") != calculated:
                raise ControlError(f"ledger event hash mismatch at seq {index}")
            previous = calculated
            count += 1
    return {
        "ok": True,
        "event_count": count,
        "last_seq": count - 1,
        "last_hash": previous,
        "ledger_path": str(path.resolve()),
    }


def append_event(
    ledger: Path, event_path: Path, expected_seq: int, expected_prev_hash: str
) -> dict[str, Any]:
    if not ledger.parent.is_dir():
        raise ControlError(f"ledger directory does not exist: {ledger.parent}")
    lock_dir = Path(f"{ledger}.lock")
    try:
        lock_dir.mkdir()
    except FileExistsError as exc:
        raise ControlError(f"ledger lock already exists: {lock_dir}") from exc
    try:
        current = verify_ledger(ledger)
        if current["last_seq"] != expected_seq or current["last_hash"] != expected_prev_hash:
            raise ControlError(
                "ledger CAS mismatch: "
                f"actual_seq={current['last_seq']} actual_hash={current['last_hash']}"
            )
        event = load_json(event_path)
        event_errors = validate_event(event, stored=False)
        if event_errors:
            raise ControlError("; ".join(event_errors))
        next_event = {
            key: value
            for key, value in event.items()
            if key not in {"seq", "prev_event_hash", "event_hash"}
        }
        next_event["seq"] = current["last_seq"] + 1
        next_event["prev_event_hash"] = current["last_hash"]
        next_event["event_hash"] = event_hash(next_event)
        needs_newline = ledger.exists() and ledger.stat().st_size > 0
        with ledger.open("a", encoding="utf-8", newline="\n") as handle:
            if needs_newline:
                with ledger.open("rb") as check:
                    check.seek(-1, os.SEEK_END)
                    if check.read(1) != b"\n":
                        handle.write("\n")
            handle.write(canonical_json(next_event) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return {
            "ok": True,
            "seq": next_event["seq"],
            "event_hash": next_event["event_hash"],
            "ledger_path": str(ledger.resolve()),
        }
    finally:
        try:
            lock_dir.rmdir()
        except OSError:
            pass


def status_summary(manifest: dict[str, Any], ledger_path: Path | None) -> dict[str, Any]:
    errors = validate_manifest(manifest)
    if errors:
        raise ControlError("; ".join(errors))
    counts = Counter(project["state"] for project in manifest["projects"])
    result: dict[str, Any] = {
        "ok": True,
        "portfolio_id": manifest["portfolio_id"],
        "project_count": len(manifest["projects"]),
        "states": dict(sorted(counts.items())),
        "incomplete_project_ids": [
            project["id"] for project in manifest["projects"] if project["state"] != "complete"
        ],
    }
    if ledger_path is not None:
        result["ledger"] = verify_ledger(ledger_path)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-manifest")
    validate.add_argument("manifest", type=Path)
    status = sub.add_parser("status")
    status.add_argument("manifest", type=Path)
    status.add_argument("--ledger", type=Path)
    topology = sub.add_parser("audit-topology")
    topology.add_argument("manifest", type=Path)
    topology.add_argument("topology", type=Path)
    admit = sub.add_parser("admit")
    admit.add_argument("plan", type=Path)
    admit.add_argument("readback", type=Path)
    append = sub.add_parser("append-event")
    append.add_argument("ledger", type=Path)
    append.add_argument("event", type=Path)
    append.add_argument("--expected-seq", type=int, required=True)
    append.add_argument("--expected-prev-hash", required=True)
    verify = sub.add_parser("verify-ledger")
    verify.add_argument("ledger", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate-manifest":
            errors = validate_manifest(load_json(args.manifest))
            result = {"ok": not errors, "errors": errors, "manifest": str(args.manifest)}
            print(canonical_json(result))
            return 0 if not errors else 10
        if args.command == "status":
            print(canonical_json(status_summary(load_json(args.manifest), args.ledger)))
            return 0
        if args.command == "audit-topology":
            result = audit_topology(load_json(args.manifest), load_json(args.topology))
            print(canonical_json(result))
            return 0 if result["ok"] else 10
        if args.command == "admit":
            result = evaluate_admission(load_json(args.plan), load_json(args.readback))
            print(canonical_json(result))
            return 0 if result["formal_result"] == "ZERO" else 10
        if args.command == "append-event":
            if not is_lower_hex(args.expected_prev_hash, 64):
                raise ControlError("expected previous hash must be 64 lowercase hex characters")
            print(
                canonical_json(
                    append_event(
                        args.ledger,
                        args.event,
                        args.expected_seq,
                        args.expected_prev_hash,
                    )
                )
            )
            return 0
        if args.command == "verify-ledger":
            print(canonical_json(verify_ledger(args.ledger)))
            return 0
    except ControlError as exc:
        print(canonical_json({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 20
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
