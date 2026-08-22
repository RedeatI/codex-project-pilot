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
                    "max_writers_per_project",
                    "control_roles",
                    "migration_controller_role",
                ],
                "topology.policy",
            )
        )
        for field in ("max_active_turns", "max_writers_per_project"):
            value = policy.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                errors.append(f"topology.policy: {field} must be a positive integer")
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
    threads = topology["threads"]
    projects = {project["id"]: project for project in manifest["projects"]}
    tasks = {thread["task_id"]: thread for thread in threads}
    active_threads = [thread for thread in threads if thread["active_turn"]]
    context_pressure_counts: Counter[str] = Counter()

    if not topology["authoritative"]:
        finding(
            "NON_AUTHORITATIVE_TOPOLOGY",
            "topology audit requires executor-owned runtime readback",
        )
    if len(active_threads) > policy["max_active_turns"]:
        finding(
            "ACTIVE_TURN_LIMIT_EXCEEDED",
            "active turns exceed the configured portfolio limit",
            active_turn_count=len(active_threads),
            max_active_turns=policy["max_active_turns"],
            task_ids=[thread["task_id"] for thread in active_threads],
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

    writer_counts: Counter[str] = Counter()
    for thread in threads:
        if thread["active_turn"] and thread["state"] != "active":
            finding(
                "ACTIVE_TURN_STATE_MISMATCH",
                "an active turn must use state=active",
                task_id=thread["task_id"],
                state=thread["state"],
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
                ],
            )

    for project_id, project in projects.items():
        owner_task_id = project["owner_task_id"]
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
        if not owner["writer"]:
            finding(
                "OWNER_WITHOUT_WRITER_LEASE",
                "manifest owner task must hold the project's writer lease",
                project_id=project_id,
                owner_task_id=owner_task_id,
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

    return {
        "schema_version": TOPOLOGY_AUDIT_SCHEMA,
        "ok": not findings,
        "portfolio_id": manifest["portfolio_id"],
        "observed_at_utc": topology["observed_at_utc"],
        "thread_count": len(threads),
        "active_turn_count": len(active_threads),
        "writer_counts": dict(sorted(writer_counts.items())),
        "context_pressure_counts": dict(sorted(context_pressure_counts.items())),
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
