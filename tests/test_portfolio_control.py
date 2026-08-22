import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "portfolio_control.py"
SPEC = importlib.util.spec_from_file_location("portfolio_control", MODULE_PATH)
assert SPEC and SPEC.loader
CONTROL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTROL)


def valid_manifest():
    return {
        "schema_version": "codex-project-pilot/1",
        "portfolio_id": "example",
        "goal": "Finish every evidenced outcome.",
        "policy": {
            "max_parallel_projects": 2,
            "default_repo_visibility": "private",
            "external_mutations_require_user_authorization": True,
        },
        "projects": [
            {
                "id": "alpha",
                "name": "Alpha",
                "host_scope": "local",
                "host_id": "local",
                "root": str(Path.cwd()),
                "owner_task_id": None,
                "authorities": ["control_read", "repo_read"],
                "state": "ready",
                "desired_outcome": "Verified private mirror",
                "repository": {
                    "provider": "github",
                    "full_name": None,
                    "visibility": "private",
                    "uploaded": False,
                },
            }
        ],
    }


def valid_topology():
    root = str(Path.cwd())
    return {
        "schema_version": "codex-project-pilot-topology/1",
        "authoritative": True,
        "observed_at_utc": "2026-08-22T00:00:00Z",
        "policy": {
            "max_active_turns": 3,
            "max_writers_per_project": 1,
            "control_roles": [
                {
                    "role": "root_controller",
                    "required": True,
                    "max_instances": 1,
                    "required_authorities": ["portfolio_decide"],
                },
                {
                    "role": "scheduler",
                    "required": True,
                    "max_instances": 1,
                    "required_authorities": ["topology_read"],
                },
                {
                    "role": "runtime_supervisor",
                    "required": True,
                    "max_instances": 1,
                    "required_authorities": ["ledger_write", "migration_control"],
                },
                {
                    "role": "owner_liaison",
                    "required": True,
                    "max_instances": 1,
                    "required_authorities": ["owner_request"],
                },
            ],
            "migration_controller_role": "runtime_supervisor",
        },
        "migration": {
            "controller_task_id": "runtime-1",
            "active_target_task_id": None,
            "lock_held": False,
        },
        "control_lifecycle": {
            "phase": "running",
            "root_task_id": "root-1",
            "safe_next_action": True,
            "pending_wait_id": None,
            "pending_owner_request_id": None,
            "consecutive_no_change": 0,
            "automation_id": "portfolio-heartbeat",
            "automation_status": "ACTIVE",
            "closure_id": None,
            "closure_delivered": False,
            "closure_owner_liaison_task_id": None,
            "work_lease": {
                "action_id": "alpha-action-1",
                "admission_id": "alpha-admission-1",
                "admission_result": "ZERO",
                "dispatched_task_id": None,
                "baseline_event_seq": 0,
                "latest_event_seq": 1,
                "progress_kind": "admitted",
                "evidence_ids": ["alpha-admission-1"],
                "lease_renewed": True,
                "action_terminal": False,
            },
        },
        "threads": [
            {
                "task_id": "root-1",
                "role": "root_controller",
                "project_id": None,
                "host_id": "local",
                "root": root,
                "state": "idle",
                "active_turn": False,
                "writer": False,
                "provisional": False,
                "authorities": ["portfolio_decide"],
            },
            {
                "task_id": "scheduler-1",
                "role": "scheduler",
                "project_id": None,
                "host_id": "local",
                "root": root,
                "state": "idle",
                "active_turn": False,
                "writer": False,
                "provisional": False,
                "authorities": ["topology_read"],
            },
            {
                "task_id": "runtime-1",
                "role": "runtime_supervisor",
                "project_id": None,
                "host_id": "local",
                "root": root,
                "state": "active",
                "active_turn": True,
                "writer": False,
                "provisional": False,
                "authorities": ["ledger_write", "migration_control"],
            },
            {
                "task_id": "liaison-1",
                "role": "owner_liaison",
                "project_id": None,
                "host_id": "local",
                "root": root,
                "state": "idle",
                "active_turn": False,
                "writer": False,
                "provisional": False,
                "authorities": ["owner_request"],
            },
            {
                "task_id": "alpha-owner",
                "role": "project_owner",
                "project_id": "alpha",
                "host_id": "local",
                "root": root,
                "state": "active",
                "active_turn": True,
                "writer": True,
                "provisional": False,
                "authorities": ["repo_write"],
            },
        ],
    }


class PortfolioControlTests(unittest.TestCase):
    def test_manifest_validation(self):
        self.assertEqual(CONTROL.validate_manifest(valid_manifest()), [])

    def test_admission_stops_after_first_nonzero(self):
        plan = {
            "project_id": "alpha",
            "action_id": "publish-1",
            "action_class": "repo_write",
            "expected_host_scope": "local",
            "expected_host_id": "local",
            "expected_root": str(Path.cwd()),
            "required_authorities": ["repo_write"],
            "portfolio_lane_state": "ready",
            "external_mutation": True,
            "user_authorized": True,
            "continuation": True,
            "transport_model_override_present": False,
            "transport_effort_override_present": False,
            "migration_fence_required": False,
        }
        readback = {
            "project_id": "alpha",
            "authoritative": False,
            "observed_host_scope": "local",
            "observed_host_id": "local",
            "observed_root": str(Path.cwd()),
            "granted_authorities": ["repo_write"],
        }
        result = CONTROL.evaluate_admission(plan, readback)
        self.assertEqual(result["formal_result"], "NONZERO")
        self.assertEqual(result["first_nonzero_check"], "authoritative_readback")
        self.assertIn("project_match", result["unexecuted_checks"])

    def test_admission_rejects_invalid_shape_without_crashing(self):
        plan = {
            "project_id": "alpha",
            "action_id": "publish-1",
            "action_class": "repo_write",
            "expected_host_scope": "local",
            "expected_host_id": "local",
            "expected_root": str(Path.cwd()),
            "required_authorities": "repo_write",
            "portfolio_lane_state": "ready",
            "external_mutation": True,
            "user_authorized": True,
            "continuation": False,
            "transport_model_override_present": False,
            "transport_effort_override_present": False,
            "migration_fence_required": False,
        }
        readback = {
            "project_id": "alpha",
            "authoritative": True,
            "observed_host_scope": "local",
            "observed_host_id": "local",
            "observed_root": str(Path.cwd()),
            "granted_authorities": ["repo_write"],
        }
        result = CONTROL.evaluate_admission(plan, readback)
        self.assertEqual(result["first_nonzero_check"], "input_shape")
        self.assertEqual(result["outcome_class"], "BLOCKED_CONFIG")

    def test_admission_rejects_host_scope_mismatch(self):
        plan = {
            "project_id": "alpha",
            "action_id": "inspect-1",
            "action_class": "control_read",
            "expected_host_scope": "local",
            "expected_host_id": "shared-name",
            "expected_root": str(Path.cwd()),
            "required_authorities": ["control_read"],
            "portfolio_lane_state": "ready",
            "external_mutation": False,
            "user_authorized": False,
            "continuation": False,
            "transport_model_override_present": False,
            "transport_effort_override_present": False,
            "migration_fence_required": False,
        }
        readback = {
            "project_id": "alpha",
            "authoritative": True,
            "observed_host_scope": "remote",
            "observed_host_id": "shared-name",
            "observed_root": str(Path.cwd()),
            "granted_authorities": ["control_read"],
        }
        result = CONTROL.evaluate_admission(plan, readback)
        self.assertEqual(result["first_nonzero_check"], "host_match")
        self.assertEqual(result["outcome_class"], "BLOCKED_HOST_IDENTITY")

    def test_topology_audit_passes_for_control_plane_and_single_writer(self):
        manifest = valid_manifest()
        manifest["projects"][0]["owner_task_id"] = "alpha-owner"
        result = CONTROL.audit_topology(manifest, valid_topology())
        self.assertTrue(result["ok"])
        self.assertEqual(result["active_turn_count"], 2)
        self.assertEqual(result["writer_counts"], {"alpha": 1})

    def test_topology_audit_reports_duplicate_control_role(self):
        topology = valid_topology()
        duplicate = copy.deepcopy(topology["threads"][1])
        duplicate["task_id"] = "scheduler-2"
        topology["threads"].append(duplicate)
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "CONTROL_ROLE_MULTIPLICITY",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_reports_multiple_project_writers(self):
        topology = valid_topology()
        duplicate = copy.deepcopy(topology["threads"][-1])
        duplicate["task_id"] = "alpha-writer-2"
        duplicate["active_turn"] = False
        duplicate["state"] = "idle"
        topology["threads"].append(duplicate)
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "PROJECT_WRITER_LIMIT_EXCEEDED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_reports_unfenced_migration_target(self):
        topology = valid_topology()
        topology["migration"]["active_target_task_id"] = "alpha-owner"
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "MIGRATION_TARGET_WITHOUT_LOCK",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_checks_manifest_owner_identity(self):
        manifest = valid_manifest()
        manifest["projects"][0]["owner_task_id"] = "missing-owner"
        result = CONTROL.audit_topology(manifest, valid_topology())
        self.assertFalse(result["ok"])
        self.assertIn(
            "OWNER_TASK_MISSING",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_accepts_managed_worktree_with_canonical_root(self):
        manifest = valid_manifest()
        manifest["projects"][0]["owner_task_id"] = "alpha-owner"
        topology = valid_topology()
        topology["threads"][-1]["root"] = str(Path.cwd() / "managed-worktree")
        topology["threads"][-1]["canonical_project_root"] = str(Path.cwd())
        result = CONTROL.audit_topology(manifest, topology)
        self.assertTrue(result["ok"])

    def test_topology_audit_requires_summary_quality_after_compaction(self):
        topology = valid_topology()
        topology["threads"][1]["context_health"] = {
            "pressure": "watch",
            "signals": ["compaction_observed"],
            "compaction_observed": True,
            "summary_quality": None,
            "controller_notified": False,
            "notification_target_task_id": None,
            "notification_id": None,
        }
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "CONTEXT_SUMMARY_QUALITY_MISSING",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_requires_context_renewal_notification(self):
        topology = valid_topology()
        topology["threads"][1]["context_health"] = {
            "pressure": "renewal_required",
            "signals": ["summary_missing_next_action"],
            "compaction_observed": True,
            "summary_quality": {"short": True, "accurate": True, "usable": False},
            "controller_notified": False,
            "notification_target_task_id": None,
            "notification_id": None,
        }
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "CONTEXT_RENEWAL_NOTIFICATION_REQUIRED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_accepts_deduplicated_controller_notification(self):
        topology = valid_topology()
        topology["threads"][1]["context_health"] = {
            "pressure": "renewal_required",
            "signals": ["runtime_context_warning"],
            "compaction_observed": False,
            "summary_quality": None,
            "controller_notified": True,
            "notification_target_task_id": "runtime-1",
            "notification_id": "context-renewal-scheduler-1-20260823t010000z",
        }
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])
        self.assertEqual(result["context_pressure_counts"], {"renewal_required": 1})

    def test_topology_audit_rejects_wrong_context_notification_target(self):
        topology = valid_topology()
        topology["threads"][1]["context_health"] = {
            "pressure": "renewal_required",
            "signals": ["runtime_context_warning"],
            "compaction_observed": False,
            "summary_quality": None,
            "controller_notified": True,
            "notification_target_task_id": "root-1",
            "notification_id": "context-renewal-scheduler-1-20260823t010000z",
        }
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "CONTEXT_RENEWAL_WRONG_NOTIFICATION_TARGET",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_does_not_treat_idle_root_as_terminal(self):
        topology = valid_topology()
        topology["threads"][0]["state"] = "idle"
        topology["threads"][0]["active_turn"] = False
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])
        self.assertEqual(result["control_phase"], "running")

    def test_topology_audit_escalates_repeated_unowned_no_change(self):
        topology = valid_topology()
        lifecycle = topology["control_lifecycle"]
        lifecycle["safe_next_action"] = False
        lifecycle["consecutive_no_change"] = 2
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("RUNNING_WITHOUT_SAFE_NEXT_ACTION", codes)
        self.assertIn("CONTROL_STALL_OWNER_ATTENTION_REQUIRED", codes)

    def test_topology_audit_requires_running_work_lease(self):
        topology = valid_topology()
        del topology["control_lifecycle"]["work_lease"]
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "RUNNING_WITHOUT_WORK_LEASE",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_reused_admission_without_ledger_delta(self):
        topology = valid_topology()
        lease = topology["control_lifecycle"]["work_lease"]
        lease["latest_event_seq"] = lease["baseline_event_seq"]
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("WORK_LEASE_EVIDENCE_INVALID", codes)
        self.assertIn("WORK_LEASE_RENEWED_WITHOUT_EVIDENCE", codes)

    def test_topology_audit_rejects_work_lease_renewal_without_evidence(self):
        topology = valid_topology()
        lease = topology["control_lifecycle"]["work_lease"]
        lease.update(
            {
                "admission_id": None,
                "admission_result": None,
                "progress_kind": "none",
                "evidence_ids": [],
                "lease_renewed": True,
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("RUNNING_WITHOUT_WORK_EVIDENCE", codes)
        self.assertIn("WORK_LEASE_RENEWED_WITHOUT_EVIDENCE", codes)

    def test_topology_audit_rejects_terminal_action_as_safe_next_action(self):
        topology = valid_topology()
        lease = topology["control_lifecycle"]["work_lease"]
        lease.update(
            {
                "baseline_event_seq": 10,
                "latest_event_seq": 11,
                "progress_kind": "terminal",
                "evidence_ids": ["event-11"],
                "action_terminal": True,
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "STALE_SAFE_NEXT_ACTION",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_accepts_authoritative_dispatch_work_lease(self):
        topology = valid_topology()
        lease = topology["control_lifecycle"]["work_lease"]
        lease.update(
            {
                "dispatched_task_id": "alpha-owner",
                "progress_kind": "dispatched",
                "evidence_ids": ["alpha-admission-1", "dispatch-alpha-owner"],
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])

    def test_topology_audit_pauses_waiting_monitor_after_first_empty_check(self):
        topology = valid_topology()
        lifecycle = topology["control_lifecycle"]
        lifecycle.update(
            {
                "phase": "waiting",
                "safe_next_action": False,
                "pending_wait_id": "external-job-1",
                "consecutive_no_change": 1,
            }
        )
        del lifecycle["work_lease"]
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "WAITING_AUTOMATION_NOT_PAUSED_AFTER_EMPTY_CHECK",
            {finding["code"] for finding in result["findings"]},
        )

        lifecycle["automation_status"] = "PAUSED"
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])

    def test_topology_audit_requires_liaison_and_paused_terminal_monitor(self):
        topology = valid_topology()
        lifecycle = topology["control_lifecycle"]
        lifecycle["phase"] = "owner_attention"
        lifecycle["safe_next_action"] = False
        lifecycle["closure_id"] = "closure-1"
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("OWNER_LIAISON_HANDOFF_REQUIRED", codes)
        self.assertIn("TERMINAL_AUTOMATION_NOT_PAUSED", codes)

    def test_topology_audit_accepts_delivered_owner_attention_closure(self):
        topology = valid_topology()
        lifecycle = topology["control_lifecycle"]
        lifecycle.update(
            {
                "phase": "owner_attention",
                "safe_next_action": False,
                "pending_owner_request_id": "closure-1",
                "consecutive_no_change": 3,
                "automation_status": "PAUSED",
                "closure_id": "closure-1",
                "closure_delivered": True,
                "closure_owner_liaison_task_id": "liaison-1",
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])

    def test_topology_audit_rejects_false_portfolio_completion(self):
        topology = valid_topology()
        lifecycle = topology["control_lifecycle"]
        lifecycle.update(
            {
                "phase": "complete",
                "safe_next_action": False,
                "automation_status": "PAUSED",
                "closure_id": "closure-1",
                "closure_delivered": True,
                "closure_owner_liaison_task_id": "liaison-1",
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "CONTROL_COMPLETE_WITH_INCOMPLETE_PROJECTS",
            {finding["code"] for finding in result["findings"]},
        )

    def test_hash_chained_append_and_verify(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / "events.jsonl"
            event_path = root / "event.json"
            event_path.write_text(
                json.dumps(
                    {
                        "schema_version": "codex-project-pilot-event/1",
                        "event_id": "event-1",
                        "event_time_utc": "2026-08-18T00:00:00Z",
                        "portfolio_id": "example",
                        "project_id": "alpha",
                        "action_id": "publish-1",
                        "event_type": "ADMISSION_PASS",
                        "actor": "root",
                        "payload": {"result": "PASS"},
                    }
                ),
                encoding="utf-8",
            )
            appended = CONTROL.append_event(ledger, event_path, -1, "0" * 64)
            verified = CONTROL.verify_ledger(ledger)
            self.assertEqual(appended["seq"], 0)
            self.assertEqual(verified["event_count"], 1)
            self.assertEqual(verified["last_hash"], appended["event_hash"])

    def test_ledger_rejects_hash_valid_event_with_invalid_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "events.jsonl"
            event = {
                "schema_version": "wrong/1",
                "event_id": "event-1",
                "event_time_utc": "2026-08-18T00:00:00Z",
                "portfolio_id": "example",
                "project_id": "alpha",
                "action_id": "publish-1",
                "event_type": "ADMISSION_PASS",
                "actor": "root",
                "payload": {},
                "seq": 0,
                "prev_event_hash": "0" * 64,
            }
            event["event_hash"] = CONTROL.event_hash(event)
            ledger.write_text(CONTROL.canonical_json(event) + "\n", encoding="utf-8")
            with self.assertRaises(CONTROL.ControlError):
                CONTROL.verify_ledger(ledger)


if __name__ == "__main__":
    unittest.main()
