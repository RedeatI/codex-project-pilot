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
    "max_parallel_projects": 3,
    "default_repo_visibility": "private",
    "external_mutations_require_user_authorization": true
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
- `portfolio_id`, `goal`, project `id`, `name`, `host_id`, `root`, and
  `desired_outcome` are non-empty strings.
- Project IDs are unique and stable across task renewal or repository relocation.
- `host_scope` is `local` or `remote`; `host_id` identifies the actual executor,
  not a display label inferred from a path.
- `state` is one of `frozen`, `ready`, `active`, `waiting`, `blocked`, or
  `complete`.
- Authorities are explicit strings. Absence means no authority.
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

## Thread identity boundary

`owner_task_id` names the intended current writer for a project. It is not proof
that the task still exists, is on the correct host/root, or holds the writer lease.
Keep volatile task state out of the portfolio manifest and capture it in a separate
authoritative topology snapshot described in
[thread-architecture.md](thread-architecture.md).

Run `audit-topology` after task creation, owner transfer, recovery, migration, or a
material concurrency change. Update `owner_task_id` only from runtime readback; do
not preserve a stale task ID merely because it appears in an earlier report.
