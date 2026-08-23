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
                "authorities": [
                    "control_read",
                    "repo_read",
                    "project_local_decide",
                    "project_local_admission",
                    "project_fresh_round_derive",
                ],
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


def enable_v24_routine_public_network(manifest):
    manifest["policy"]["project_owner_autonomy"] = {
        "contract_version": "PROJECT_TASK_CONTRACT_V2_4",
        "routine_public_network": {
            "authority": "routine_public_network",
            "allowed_categories": [
                "public_dependency_fetch",
                "public_documentation_lookup",
                "read_only_public_api",
                "build_resource_fetch",
                "network_diagnostic",
            ],
            "minimum_envelope_fields": [
                "purpose",
                "domains_or_urls",
                "write_locations",
                "credential_boundary",
                "frequency",
                "expected_evidence",
                "stop_condition",
            ],
            "credentials_allowed": False,
        },
        "owner_gate_categories": [
            "credential_or_private_data",
            "production_or_real_user_impact",
            "destructive_operation",
            "external_publication_or_deployment",
            "cross_host_migration",
            "material_scope_or_dependency_expansion",
            "irreversible_external_write",
            "major_architecture_direction",
        ],
        "first_nonzero_stops_round": True,
        "fresh_round_requires_material_difference": True,
    }
    manifest["projects"][0]["authorities"].append("routine_public_network")
    return manifest


def valid_topology():
    root = str(Path.cwd())
    return {
        "schema_version": "codex-project-pilot-topology/1",
        "authoritative": True,
        "observed_at_utc": "2026-08-22T00:00:00Z",
        "policy": {
            "max_active_turns": 3,
            "baseline_max_active_turns": 3,
            "runtime_reported_max_active_turns": None,
            "reserved_control_slots": 1,
            "dispatch_requirements": {
                "complete_input_required": True,
                "fresh_admission_required": True,
                "independent_writer_required": True,
                "effective_project_action_required": True,
            },
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
                    "required_authorities": ["topology_read", "dispatch_policy"],
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
        "nested_workers": [],
        "stage_closeouts": [],
        "control_lifecycle": {
            "phase": "running",
            "root_task_id": "root-1",
            "safe_next_action": True,
            "pending_wait_id": None,
            "pending_owner_request_id": None,
            "consecutive_no_change": 0,
            "automation_id": "portfolio-heartbeat",
            "automation_status": "ACTIVE",
            "automation_notification_policy": "ALL",
            "closure_id": None,
            "closure_delivered": False,
            "closure_owner_liaison_task_id": None,
            "closure_delivery_turn_id": None,
            "pause_notice_delivered_before_pause": False,
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
                "capacity_class": "baseline",
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
                "authorities": ["topology_read", "dispatch_policy"],
                "capacity_class": "baseline",
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
                "capacity_class": "baseline",
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
                "capacity_class": "baseline",
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
                "authorities": ["repo_read"],
                "capacity_class": "baseline",
            },
        ],
    }


def valid_federated_topology():
    topology = valid_topology()
    topology["policy"]["governance_mode"] = "federated_thin_kernel"
    topology["policy"]["control_roles"] = [
        definition
        for definition in topology["policy"]["control_roles"]
        if definition["role"] != "root_controller"
    ]
    lifecycle = topology["control_lifecycle"]
    lifecycle["controller_task_id"] = "scheduler-1"
    del lifecycle["root_task_id"]
    topology["threads"] = [
        thread
        for thread in topology["threads"]
        if thread["role"] != "root_controller"
    ]
    owner = next(
        thread for thread in topology["threads"] if thread["task_id"] == "alpha-owner"
    )
    owner["authorities"] = [
        "repo_read",
        "project_local_decide",
        "project_local_admission",
        "project_fresh_round_derive",
    ]
    return topology


def valid_stage_closeout():
    return {
        "stage_id": "alpha-stage-1",
        "project_id": "alpha",
        "project_task_id": "alpha-owner",
        "host_id": "local",
        "branch": "worktree/alpha-stage-1",
        "target_branch": "main",
        "status": "complete",
        "step_results": {
            "evidence": "PASS",
            "test": "PASS",
            "build": "NOT_REQUIRED",
            "diff": "PASS",
            "readback": "PASS",
            "commit": "PASS",
            "push": "PASS",
            "merge": "PASS",
        },
        "identity_verified": True,
        "worktree_scope_clean": True,
        "conflict_free": True,
        "worktree_merge_required": True,
        "first_nonzero_step": None,
        "commit_sha": "a" * 40,
        "push_readback_sha": "a" * 40,
        "merge_readback_sha": "b" * 40,
    }


class PortfolioControlTests(unittest.TestCase):
    def test_manifest_validation(self):
        self.assertEqual(CONTROL.validate_manifest(valid_manifest()), [])

    def test_manifest_validation_accepts_v24_routine_public_network(self):
        manifest = enable_v24_routine_public_network(valid_manifest())
        self.assertEqual(CONTROL.validate_manifest(manifest), [])

    def test_manifest_validation_keeps_legacy_manifest_compatible(self):
        manifest = valid_manifest()
        self.assertNotIn("project_owner_autonomy", manifest["policy"])
        self.assertEqual(CONTROL.validate_manifest(manifest), [])

    def test_manifest_rejects_network_authority_without_v24_policy(self):
        manifest = valid_manifest()
        manifest["projects"][0]["authorities"].append("routine_public_network")
        errors = CONTROL.validate_manifest(manifest)
        self.assertTrue(
            any(
                "routine_public_network requires policy.project_owner_autonomy PROJECT_TASK_CONTRACT_V2_4"
                in error
                for error in errors
            )
        )

    def test_manifest_rejects_v24_policy_that_allows_credentials(self):
        manifest = enable_v24_routine_public_network(valid_manifest())
        manifest["policy"]["project_owner_autonomy"]["routine_public_network"][
            "credentials_allowed"
        ] = True
        errors = CONTROL.validate_manifest(manifest)
        self.assertIn(
            "policy.project_owner_autonomy.routine_public_network: credentials_allowed must be false",
            errors,
        )

    def test_manifest_rejects_v24_policy_with_missing_owner_gate(self):
        manifest = enable_v24_routine_public_network(valid_manifest())
        manifest["policy"]["project_owner_autonomy"]["owner_gate_categories"].pop()
        errors = CONTROL.validate_manifest(manifest)
        self.assertIn(
            "policy.project_owner_autonomy: owner_gate_categories must list the exact V2_4 owner gates",
            errors,
        )

    def test_federated_manifest_rejects_project_control_plane_authority(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        manifest["projects"][0]["authorities"].append("portfolio_decide")
        errors = CONTROL.validate_manifest(manifest)
        self.assertTrue(
            any("control-plane authorities: portfolio_decide" in error for error in errors)
        )

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
        self.assertEqual(result["active_nested_worker_count"], 0)
        self.assertEqual(result["active_execution_unit_count"], 2)
        self.assertEqual(result["reserved_control_slots"], 1)
        self.assertEqual(result["new_dispatch_budget"], 0)
        self.assertEqual(result["writer_counts"], {"alpha": 1})

    def test_topology_audit_accepts_federated_thin_kernel(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        manifest["projects"][0]["owner_task_id"] = "alpha-owner"
        result = CONTROL.audit_topology(manifest, valid_federated_topology())
        self.assertTrue(result["ok"])
        self.assertEqual(result["governance_mode"], "federated_thin_kernel")

    def test_topology_audit_rejects_nonretired_root_in_federated_mode(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        root = copy.deepcopy(valid_topology()["threads"][0])
        topology["threads"].append(root)
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "FEDERATED_ROOT_CONTROLLER_FORBIDDEN",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_scheduler_authority_escalation(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        scheduler = next(
            thread for thread in topology["threads"] if thread["role"] == "scheduler"
        )
        scheduler["authorities"].append("portfolio_decide")
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "FEDERATED_SCHEDULER_AUTHORITY_ESCALATION",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_fails_closed_on_manifest_topology_mode_mismatch(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        result = CONTROL.audit_topology(manifest, valid_topology())
        codes = {finding["code"] for finding in result["findings"]}
        self.assertFalse(result["ok"])
        self.assertEqual(result["governance_mode"], "federated_thin_kernel")
        self.assertIn("GOVERNANCE_MODE_MISMATCH", codes)
        self.assertIn("FEDERATED_ROOT_CONTROLLER_FORBIDDEN", codes)

    def test_topology_audit_rejects_control_role_as_project_writer(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        scheduler = next(
            thread for thread in topology["threads"] if thread["role"] == "scheduler"
        )
        scheduler["project_id"] = "alpha"
        scheduler["writer"] = True
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "CONTROL_PROJECT_EXECUTION_FORBIDDEN",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_unknown_scheduler_authority(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        scheduler = next(
            thread for thread in topology["threads"] if thread["role"] == "scheduler"
        )
        scheduler["authorities"].append("authority_grant")
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "FEDERATED_SCHEDULER_AUTHORITY_ESCALATION",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_scheduler_as_migration_controller(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        topology["policy"]["migration_controller_role"] = "scheduler"
        topology["migration"]["controller_task_id"] = "scheduler-1"
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "FEDERATED_MIGRATION_CONTROLLER_ROLE_INVALID",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_runtime_or_liaison_authority_escalation(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        runtime = next(
            thread
            for thread in topology["threads"]
            if thread["role"] == "runtime_supervisor"
        )
        liaison = next(
            thread
            for thread in topology["threads"]
            if thread["role"] == "owner_liaison"
        )
        runtime["authorities"].append("portfolio_decide")
        liaison["authorities"].append("repo_write")
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        escalations = [
            finding
            for finding in result["findings"]
            if finding["code"] == "FEDERATED_CONTROL_AUTHORITY_ESCALATION"
        ]
        self.assertEqual(len(escalations), 2)

    def test_topology_audit_rejects_renamed_hidden_controller(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        topology["policy"]["control_roles"].append(
            {
                "role": "portfolio_governor",
                "required": True,
                "max_instances": 1,
                "required_authorities": ["portfolio_decide"],
            }
        )
        governor = copy.deepcopy(topology["threads"][0])
        governor["task_id"] = "governor-1"
        governor["role"] = "portfolio_governor"
        governor["authorities"] = ["portfolio_decide"]
        topology["threads"].append(governor)
        result = CONTROL.audit_topology(manifest, topology)
        codes = {finding["code"] for finding in result["findings"]}
        self.assertFalse(result["ok"])
        self.assertIn("FEDERATED_CONTROL_ROLE_NOT_ALLOWED", codes)
        self.assertIn("FEDERATED_NON_PROJECT_ROLE_NOT_ALLOWED", codes)

    def test_topology_audit_rejects_project_authority_outside_manifest(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        owner = next(
            thread for thread in topology["threads"] if thread["task_id"] == "alpha-owner"
        )
        owner["authorities"].append("repo_write")
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "PROJECT_AUTHORITY_OUTSIDE_MANIFEST",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_validation_handles_malformed_policy_without_exception(self):
        topology = valid_topology()
        topology["policy"] = []
        errors = CONTROL.validate_topology(topology)
        self.assertIn("topology.policy: must be an object", errors)

    def test_topology_audit_requires_one_live_task_for_each_thin_kernel_role(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        liaison = next(
            thread
            for thread in topology["threads"]
            if thread["role"] == "owner_liaison"
        )
        liaison["state"] = "retired"
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "FEDERATED_LIVE_CONTROL_ROLE_COUNT_INVALID",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_retired_federated_migration_controller(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        runtime = next(
            thread
            for thread in topology["threads"]
            if thread["role"] == "runtime_supervisor"
        )
        runtime["state"] = "retired"
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "FEDERATED_MIGRATION_CONTROLLER_NOT_LIVE",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_requires_minimum_thin_kernel_authorities(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        topology = valid_federated_topology()
        for definition in topology["policy"]["control_roles"]:
            definition["required_authorities"] = []
        for thread in topology["threads"]:
            if thread["role"] in {
                "scheduler",
                "runtime_supervisor",
                "owner_liaison",
            }:
                thread["authorities"] = []
        result = CONTROL.audit_topology(manifest, topology)
        codes = {finding["code"] for finding in result["findings"]}
        self.assertFalse(result["ok"])
        self.assertIn("FEDERATED_CONTROL_POLICY_AUTHORITY_MINIMUM_MISSING", codes)
        self.assertIn("FEDERATED_CONTROL_RUNTIME_AUTHORITY_MINIMUM_MISSING", codes)

    def test_topology_audit_rejects_non_live_manifest_owner(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        manifest["projects"][0]["owner_task_id"] = "alpha-owner"
        topology = valid_federated_topology()
        owner = next(
            thread for thread in topology["threads"] if thread["task_id"] == "alpha-owner"
        )
        owner["state"] = "retired"
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "OWNER_TASK_NOT_LIVE",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_exempts_frozen_federated_owner_runtime_requirements(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        manifest["projects"][0]["owner_task_id"] = "alpha-owner"
        manifest["projects"][0]["state"] = "frozen"
        topology = valid_federated_topology()
        owner = next(
            thread for thread in topology["threads"] if thread["task_id"] == "alpha-owner"
        )
        owner["writer"] = False
        owner["state"] = "unavailable"
        owner["active_turn"] = False
        owner["authorities"] = ["repo_read"]

        result = CONTROL.audit_topology(manifest, topology)

        self.assertTrue(result["ok"])
        self.assertNotIn(
            "OWNER_WITHOUT_WRITER_LEASE",
            {finding["code"] for finding in result["findings"]},
        )
        self.assertNotIn(
            "OWNER_TASK_NOT_LIVE",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_reserves_project_local_governance_for_owner(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        manifest["projects"][0]["owner_task_id"] = "alpha-owner"
        topology = valid_federated_topology()
        scoped = copy.deepcopy(
            next(
                thread
                for thread in topology["threads"]
                if thread["task_id"] == "alpha-owner"
            )
        )
        scoped["task_id"] = "alpha-scoped"
        scoped["writer"] = False
        scoped["authorities"] = ["project_local_decide"]
        topology["threads"].append(scoped)
        result = CONTROL.audit_topology(manifest, topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "PROJECT_OWNER_ONLY_AUTHORITY_HELD_BY_NON_OWNER",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_requires_owner_for_unfinished_federated_project(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        result = CONTROL.audit_topology(manifest, valid_federated_topology())
        self.assertFalse(result["ok"])
        self.assertIn(
            "FEDERATED_PROJECT_OWNER_REQUIRED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_requires_owner_autonomy_authority_minimum(self):
        manifest = valid_manifest()
        manifest["policy"]["governance_mode"] = "federated_thin_kernel"
        manifest["projects"][0]["owner_task_id"] = "alpha-owner"
        manifest["projects"][0]["authorities"] = ["control_read", "repo_read"]
        topology = valid_federated_topology()
        owner = next(
            thread for thread in topology["threads"] if thread["task_id"] == "alpha-owner"
        )
        owner["authorities"] = ["repo_read"]
        result = CONTROL.audit_topology(manifest, topology)
        codes = {finding["code"] for finding in result["findings"]}
        self.assertFalse(result["ok"])
        self.assertIn("FEDERATED_PROJECT_AUTHORITY_MINIMUM_MISSING", codes)
        self.assertIn("FEDERATED_PROJECT_OWNER_AUTHORITY_MINIMUM_MISSING", codes)

    def test_legacy_topology_preserves_project_authority_compatibility(self):
        manifest = valid_manifest()
        manifest["projects"][0]["owner_task_id"] = "alpha-owner"
        topology = valid_topology()
        owner = next(
            thread for thread in topology["threads"] if thread["task_id"] == "alpha-owner"
        )
        owner["authorities"] = ["repo_write"]
        result = CONTROL.audit_topology(manifest, topology)
        self.assertTrue(result["ok"])

    def test_topology_audit_counts_nested_workers_in_capacity(self):
        topology = valid_topology()
        topology["policy"]["max_active_turns"] = 4
        topology["policy"]["baseline_max_active_turns"] = 4
        topology["nested_workers"].append(
            {
                "worker_id": "runtime-worker-1",
                "controller_task_id": "runtime-1",
                "project_id": None,
                "host_id": "local",
                "active": True,
                "writer": False,
                "capacity_class": "baseline",
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])
        self.assertEqual(result["active_turn_count"], 2)
        self.assertEqual(result["active_nested_worker_count"], 1)
        self.assertEqual(result["active_execution_unit_count"], 3)
        self.assertEqual(result["new_dispatch_budget"], 0)

    def test_topology_audit_uses_configured_limit_ten_without_runtime_cap(self):
        topology = valid_topology()
        topology["policy"]["max_active_turns"] = 10
        topology["policy"]["baseline_max_active_turns"] = 6
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])
        self.assertEqual(result["configured_max_active_turns"], 10)
        self.assertEqual(result["effective_max_active_turns"], 10)
        self.assertIsNone(result["runtime_reported_max_active_turns"])
        self.assertEqual(result["new_dispatch_budget"], 7)

    def test_topology_audit_clamps_limit_ten_to_runtime_readback(self):
        topology = valid_topology()
        topology["policy"]["max_active_turns"] = 10
        topology["policy"]["baseline_max_active_turns"] = 6
        topology["policy"]["runtime_reported_max_active_turns"] = 8
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])
        self.assertEqual(result["configured_max_active_turns"], 10)
        self.assertEqual(result["effective_max_active_turns"], 8)
        self.assertEqual(result["new_dispatch_budget"], 5)

    def test_topology_audit_requires_surge_evidence_beyond_baseline_envelope(self):
        topology = valid_topology()
        topology["policy"]["max_active_turns"] = 10
        topology["policy"]["baseline_max_active_turns"] = 2
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertEqual(result["required_surge_slot_count"], 1)
        self.assertIn(
            "SURGE_SLOT_EVIDENCE_MISSING",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_accepts_fresh_admitted_surge_project_writer(self):
        topology = valid_topology()
        topology["policy"]["max_active_turns"] = 10
        topology["policy"]["baseline_max_active_turns"] = 2
        project_thread = topology["threads"][-1]
        project_thread["capacity_class"] = "surge"
        project_thread["dispatch_admission"] = {
            "action_id": "alpha-effective-action-2",
            "input_complete": True,
            "admission_id": "alpha-admission-2",
            "admission_result": "ZERO",
            "writer_task_id": "alpha-owner",
        }
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])
        self.assertEqual(result["required_surge_slot_count"], 1)
        self.assertEqual(result["active_surge_slot_count"], 1)

    def test_topology_audit_rejects_incomplete_or_nonzero_surge_action(self):
        topology = valid_topology()
        topology["policy"]["max_active_turns"] = 10
        topology["policy"]["baseline_max_active_turns"] = 2
        project_thread = topology["threads"][-1]
        project_thread["capacity_class"] = "surge"
        project_thread["dispatch_admission"] = {
            "action_id": "alpha-filler-action",
            "input_complete": False,
            "admission_id": "alpha-admission-nonzero",
            "admission_result": "NONZERO",
            "writer_task_id": "scheduler-1",
        }
        result = CONTROL.audit_topology(valid_manifest(), topology)
        codes = {finding["code"] for finding in result["findings"]}
        self.assertFalse(result["ok"])
        self.assertIn("SURGE_INPUT_INCOMPLETE", codes)
        self.assertIn("SURGE_FRESH_ADMISSION_REQUIRED", codes)
        self.assertIn("SURGE_WRITER_IDENTITY_MISMATCH", codes)

    def test_topology_audit_forbids_nested_worker_in_surge_capacity(self):
        topology = valid_topology()
        topology["policy"]["max_active_turns"] = 10
        topology["nested_workers"].append(
            {
                "worker_id": "runtime-surge-worker",
                "controller_task_id": "runtime-1",
                "project_id": None,
                "host_id": "local",
                "active": True,
                "writer": False,
                "capacity_class": "surge",
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "SURGE_NESTED_WORKER_FORBIDDEN",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_nested_worker_capacity_overflow(self):
        topology = valid_topology()
        topology["nested_workers"].extend(
            [
                {
                    "worker_id": "runtime-worker-1",
                    "controller_task_id": "runtime-1",
                    "project_id": None,
                    "host_id": "local",
                    "active": True,
                    "writer": False,
                    "capacity_class": "baseline",
                },
                {
                    "worker_id": "runtime-worker-2",
                    "controller_task_id": "runtime-1",
                    "project_id": None,
                    "host_id": "local",
                    "active": True,
                    "writer": False,
                    "capacity_class": "baseline",
                },
            ]
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "ACTIVE_EXECUTION_UNIT_LIMIT_EXCEEDED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_counts_nested_project_writers(self):
        topology = valid_topology()
        topology["policy"]["max_active_turns"] = 4
        topology["policy"]["baseline_max_active_turns"] = 4
        topology["nested_workers"].append(
            {
                "worker_id": "alpha-worker-1",
                "controller_task_id": "runtime-1",
                "project_id": "alpha",
                "host_id": "local",
                "active": True,
                "writer": True,
                "capacity_class": "baseline",
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "PROJECT_WRITER_LIMIT_EXCEEDED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_root_as_project_writer(self):
        topology = valid_topology()
        root = topology["threads"][0]
        root["project_id"] = "alpha"
        root["writer"] = True
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "ROOT_PROJECT_EXECUTION_FORBIDDEN",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_root_controlled_project_worker(self):
        topology = valid_topology()
        topology["nested_workers"].append(
            {
                "worker_id": "alpha-worker-1",
                "controller_task_id": "root-1",
                "project_id": "alpha",
                "host_id": "local",
                "active": False,
                "writer": False,
                "capacity_class": "baseline",
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "PROJECT_WORKER_WRONG_CONTROLLER",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_accepts_project_controlled_nested_worker(self):
        topology = valid_topology()
        topology["policy"]["max_active_turns"] = 4
        topology["policy"]["baseline_max_active_turns"] = 4
        topology["nested_workers"].append(
            {
                "worker_id": "alpha-worker-1",
                "controller_task_id": "alpha-owner",
                "project_id": "alpha",
                "host_id": "local",
                "active": True,
                "writer": False,
                "capacity_class": "baseline",
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])

    def test_topology_audit_accepts_complete_stage_closeout(self):
        topology = valid_topology()
        topology["stage_closeouts"].append(valid_stage_closeout())
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])
        self.assertEqual(result["stage_closeout_status_counts"], {"complete": 1})

    def test_topology_audit_rejects_closeout_without_merge_readback(self):
        topology = valid_topology()
        closeout = valid_stage_closeout()
        closeout["merge_readback_sha"] = None
        topology["stage_closeouts"].append(closeout)
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "STAGE_CLOSEOUT_MERGE_READBACK_MISSING",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_stops_closeout_after_first_nonzero(self):
        topology = valid_topology()
        closeout = valid_stage_closeout()
        closeout["status"] = "stopped"
        closeout["step_results"].update(
            {
                "build": "NONZERO",
                "diff": "UNEXECUTED",
                "readback": "UNEXECUTED",
                "commit": "UNEXECUTED",
                "push": "UNEXECUTED",
                "merge": "UNEXECUTED",
            }
        )
        closeout["first_nonzero_step"] = "build"
        closeout["commit_sha"] = None
        closeout["push_readback_sha"] = None
        closeout["merge_readback_sha"] = None
        topology["stage_closeouts"].append(closeout)
        result = CONTROL.audit_topology(valid_manifest(), topology)
        codes = {finding["code"] for finding in result["findings"]}
        self.assertFalse(result["ok"])
        self.assertIn("STAGE_CLOSEOUT_FIRST_NONZERO", codes)
        self.assertNotIn("STAGE_CLOSEOUT_CONTINUED_AFTER_NONZERO", codes)

    def test_topology_audit_rejects_closeout_continuing_after_nonzero(self):
        topology = valid_topology()
        closeout = valid_stage_closeout()
        closeout["status"] = "stopped"
        closeout["step_results"]["build"] = "NONZERO"
        closeout["first_nonzero_step"] = "build"
        topology["stage_closeouts"].append(closeout)
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "STAGE_CLOSEOUT_CONTINUED_AFTER_NONZERO",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_root_stage_closeout_executor(self):
        topology = valid_topology()
        closeout = valid_stage_closeout()
        closeout["project_task_id"] = "root-1"
        topology["stage_closeouts"].append(closeout)
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "STAGE_CLOSEOUT_ROOT_EXECUTOR_FORBIDDEN",
            {finding["code"] for finding in result["findings"]},
        )

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
        self.assertFalse(result["ok"])
        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("PAUSED_AUTOMATION_WITHOUT_OWNER_NOTICE", codes)
        self.assertIn("PAUSE_BEFORE_OWNER_NOTICE", codes)

        lifecycle.update(
            {
                "closure_id": "closure-1",
                "closure_delivered": True,
                "closure_owner_liaison_task_id": "liaison-1",
                "closure_delivery_turn_id": "liaison-turn-1",
                "pause_notice_delivered_before_pause": True,
            }
        )
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertTrue(result["ok"])

    def test_topology_audit_rejects_muted_pause_notice(self):
        topology = valid_topology()
        lifecycle = topology["control_lifecycle"]
        lifecycle.update(
            {
                "phase": "waiting",
                "safe_next_action": False,
                "pending_wait_id": "external-job-1",
                "automation_status": "PAUSED",
                "automation_notification_policy": "FAILED_RUNS_ONLY",
                "closure_id": "closure-1",
                "closure_delivered": True,
                "closure_owner_liaison_task_id": "liaison-1",
                "closure_delivery_turn_id": "liaison-turn-1",
                "pause_notice_delivered_before_pause": True,
            }
        )
        del lifecycle["work_lease"]
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "PAUSE_NOTICE_NOT_USER_VISIBLE",
            {finding["code"] for finding in result["findings"]},
        )

    def test_topology_audit_rejects_pause_before_owner_notice(self):
        topology = valid_topology()
        lifecycle = topology["control_lifecycle"]
        lifecycle.update(
            {
                "phase": "waiting",
                "safe_next_action": False,
                "pending_wait_id": "external-job-1",
                "automation_status": "PAUSED",
                "closure_id": "closure-1",
                "closure_delivered": True,
                "closure_owner_liaison_task_id": "liaison-1",
                "closure_delivery_turn_id": "liaison-turn-1",
                "pause_notice_delivered_before_pause": False,
            }
        )
        del lifecycle["work_lease"]
        result = CONTROL.audit_topology(valid_manifest(), topology)
        self.assertFalse(result["ok"])
        self.assertIn(
            "PAUSE_BEFORE_OWNER_NOTICE",
            {finding["code"] for finding in result["findings"]},
        )

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
                "closure_delivery_turn_id": "liaison-turn-1",
                "pause_notice_delivered_before_pause": True,
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
                "closure_delivery_turn_id": "liaison-turn-1",
                "pause_notice_delivered_before_pause": True,
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
