"""End-to-end CLI smoke test using an isolated temporary portfolio."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).parents[1]
CONTROL = ROOT / "scripts" / "portfolio_control.py"
ZERO_HASH = "0" * 64


def write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def run_cli(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(CONTROL), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        if completed.stdout:
            print(completed.stdout, end="", file=sys.stderr)
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        raise SystemExit(completed.returncode)
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        print(f"invalid CLI JSON output: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if not isinstance(result, dict):
        print("CLI JSON output must be an object", file=sys.stderr)
        raise SystemExit(1)
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="codex-project-pilot-") as directory:
        runtime_root = Path(directory).resolve()
        manifest_path = runtime_root / "portfolio.json"
        plan_path = runtime_root / "plan.json"
        readback_path = runtime_root / "readback.json"
        event_path = runtime_root / "event.json"
        ledger_path = runtime_root / "events.jsonl"
        topology_path = runtime_root / "topology.json"

        write_json(
            manifest_path,
            {
                "schema_version": "codex-project-pilot/1",
                "portfolio_id": "e2e-portfolio",
                "goal": "Verify the deterministic control loop.",
                "policy": {
                    "max_parallel_projects": 1,
                    "default_repo_visibility": "private",
                    "external_mutations_require_user_authorization": True,
                },
                "projects": [
                    {
                        "id": "alpha",
                        "name": "Alpha",
                        "host_scope": "local",
                        "host_id": "e2e-local",
                        "root": str(runtime_root),
                        "owner_task_id": None,
                        "authorities": ["control_read", "control_write"],
                        "state": "ready",
                        "desired_outcome": "Verified local control flow",
                        "repository": {
                            "provider": "github",
                            "full_name": None,
                            "visibility": "private",
                            "uploaded": False,
                        },
                    }
                ],
            },
        )
        write_json(
            plan_path,
            {
                "project_id": "alpha",
                "action_id": "e2e-control-1",
                "action_class": "control_write",
                "expected_host_scope": "local",
                "expected_host_id": "e2e-local",
                "expected_root": str(runtime_root),
                "required_authorities": ["control_write"],
                "portfolio_lane_state": "ready",
                "external_mutation": False,
                "user_authorized": False,
                "continuation": False,
                "transport_model_override_present": False,
                "transport_effort_override_present": False,
                "migration_fence_required": False,
            },
        )
        write_json(
            readback_path,
            {
                "project_id": "alpha",
                "authoritative": True,
                "observed_host_scope": "local",
                "observed_host_id": "e2e-local",
                "observed_root": str(runtime_root),
                "granted_authorities": ["control_read", "control_write"],
            },
        )
        write_json(
            event_path,
            {
                "schema_version": "codex-project-pilot-event/1",
                "event_id": "e2e-event-1",
                "event_time_utc": "2026-08-18T00:00:00Z",
                "portfolio_id": "e2e-portfolio",
                "project_id": "alpha",
                "action_id": "e2e-control-1",
                "event_type": "ADMISSION_PASS",
                "actor": "e2e-cli",
                "payload": {"formal_result": "ZERO"},
            },
        )
        write_json(
            topology_path,
            {
                "schema_version": "codex-project-pilot-topology/1",
                "authoritative": True,
                "observed_at_utc": "2026-08-22T00:00:00Z",
                "policy": {
                    "max_active_turns": 2,
                    "max_writers_per_project": 1,
                    "control_roles": [
                        {
                            "role": "root_controller",
                            "required": True,
                            "max_instances": 1,
                            "required_authorities": ["portfolio_decide"],
                        },
                        {
                            "role": "runtime_supervisor",
                            "required": True,
                            "max_instances": 1,
                            "required_authorities": [
                                "ledger_write",
                                "migration_control",
                            ],
                        },
                    ],
                    "migration_controller_role": "runtime_supervisor",
                },
                "migration": {
                    "controller_task_id": "runtime-1",
                    "active_target_task_id": None,
                    "lock_held": False,
                },
                "threads": [
                    {
                        "task_id": "root-1",
                        "role": "root_controller",
                        "project_id": None,
                        "host_id": "e2e-local",
                        "root": str(runtime_root),
                        "state": "idle",
                        "active_turn": False,
                        "writer": False,
                        "provisional": False,
                        "authorities": ["portfolio_decide"],
                    },
                    {
                        "task_id": "runtime-1",
                        "role": "runtime_supervisor",
                        "project_id": None,
                        "host_id": "e2e-local",
                        "root": str(runtime_root),
                        "state": "idle",
                        "active_turn": False,
                        "writer": False,
                        "provisional": False,
                        "authorities": ["ledger_write", "migration_control"],
                    },
                    {
                        "task_id": "alpha-owner",
                        "role": "project_owner",
                        "project_id": "alpha",
                        "host_id": "e2e-local",
                        "root": str(runtime_root),
                        "state": "active",
                        "active_turn": True,
                        "writer": True,
                        "provisional": False,
                        "authorities": ["control_write"],
                    },
                ],
            },
        )

        manifest = run_cli("validate-manifest", str(manifest_path))
        admission = run_cli("admit", str(plan_path), str(readback_path))
        topology = run_cli("audit-topology", str(manifest_path), str(topology_path))
        appended = run_cli(
            "append-event",
            str(ledger_path),
            str(event_path),
            "--expected-seq",
            "-1",
            "--expected-prev-hash",
            ZERO_HASH,
        )
        verified = run_cli("verify-ledger", str(ledger_path))
        status = run_cli("status", str(manifest_path), "--ledger", str(ledger_path))

        if (
            not manifest.get("ok")
            or admission.get("formal_result") != "ZERO"
            or not topology.get("ok")
        ):
            return 1
        if appended.get("seq") != 0 or verified.get("event_count") != 1:
            return 1
        if status.get("incomplete_project_ids") != ["alpha"]:
            return 1
        print(
            json.dumps(
                {
                    "ok": True,
                    "manifest": "PASS",
                    "admission": "ZERO",
                    "topology": "PASS",
                    "ledger_events": 1,
                    "status": "PASS",
                },
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
