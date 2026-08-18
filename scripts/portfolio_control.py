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
ZERO_HASH = "0" * 64
PROJECT_STATES = {"frozen", "ready", "active", "waiting", "blocked", "complete"}
HOST_SCOPES = {"local", "remote"}
VISIBILITIES = {"private", "public", "internal"}
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
