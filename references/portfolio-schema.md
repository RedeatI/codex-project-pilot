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
      "contract_version": "PROJECT_TASK_CONTRACT_V2_4",
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
  the policy contains the exact `PROJECT_TASK_CONTRACT_V2_4` block shown above.
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
project objective or its V2.4 autonomy: the same project owner may derive a fresh
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
