# Codex Project Pilot

An evidence-backed Codex Skill for coordinating several projects, repositories,
and agent-owned workstreams toward one persistent goal.

It provides a portable portfolio manifest, runtime admissions, deterministic
thread-topology audits, first-nonzero formal-round semantics, a hash-chained
decision ledger, long-contract routing, and privacy-gated GitHub publication
guidance.

The recommended `federated_thin_kernel` topology puts project-local decisions,
admission, recovery, verification, and closeout in each project's owner task. Its
thin governance kernel retains only scheduling/efficiency policy, deterministic
runtime supervision and migrations, and one owner liaison. There is no persistent
root controller. The legacy `root_controller` mode remains available for portfolios
whose shared authority cannot yet be partitioned. Runtime snapshots make authority
creep, stale owners, unfenced migrations, excess active turns, and multiple project
writers visible before they become coordination failures.

High-concurrency audits count both visible active turns and nested workers, including
workers hidden inside a controller. A configurable control-slot reserve
is subtracted before computing the new-dispatch budget, so unrelated active tasks and
in-turn helpers cannot silently overcommit the host or starve terminal-event handling.
The configured limit is policy, not a claim about the Codex platform: an authoritative
smaller runtime limit clamps the effective limit automatically. Capacity beyond the
declared baseline is surge capacity and may carry only a complete, effective project
action with a fresh `ZERO` admission and the same independent project task holding its
writer lease. Control roles, nested workers, filler work, and duplicate actions cannot
consume surge slots.
In federated mode, a project owner may decide and execute only inside its explicit
project authority envelope. The scheduler may rank ready actions and optimize
capacity, but cannot grant authority, mutate a repository, write the control ledger,
run migrations, or act as a hidden root. Cross-project conflicts and authority
expansion are routed through the owner liaison for an exact user decision. Manifest
and topology governance modes must match; a mismatch fails closed to federated
enforcement. Every declared control role is forbidden from attaching to a project or
holding its writer lease. Federated mode requires exactly one live `scheduler`,
`runtime_supervisor`, and `owner_liaison`; each has a minimum capability set and a
maximum allowlist. Project envelopes cannot contain control-plane authorities, and
only the manifest owner may hold project-local decision/admission/recovery authority.
Every unfinished, non-frozen project must bind one live writer owner and give both
the manifest envelope and that owner the three autonomy authorities. Legacy mode
keeps its prior permissive project-authority behavior for compatibility.
Each stage is preferably dispatched as one complete contract covering preflight,
implementation or diagnosis, decision-changing tests/build, diff/readback, commit,
non-force push, fast-forward merge, and target readback. Project-controlled
non-writing helpers may diagnose routine harness or evidence issues, while the project
task retains the only writer. A first nonzero stops that round, not the project goal;
the coordinator derives a materially different fresh round without escalating routine
mechanical failures. Unknown identity, foreign dirty paths, conflicts, or a first
nonzero stop the remaining gates; force push and force merge are outside the contract.

The `PROJECT_TASK_CONTRACT_V2_4` prompt adds a validation-value gate: before any check,
name the blocker it removes or decision it changes and the new evidence expected.
Skip repeated or decision-irrelevant checks while preserving required safety,
authority, publication, merge, and release evidence. It also makes Sol-specific risk
claims traceable instead of treating community anecdotes as facts.

V2.4 also makes routine public networking an explicit project-local authority rather
than a blanket portfolio permission. A granted project may fetch public dependencies
and build resources, consult public documentation, use read-only public APIs, and run
network diagnostics with a compact purpose/domain/write-location/no-credential/
frequency/evidence/stop envelope. Credentials or private data, production or real-user
effects, destructive or irreversible writes, external publication/deployment,
cross-host migration, material scope or dependency expansion, and major architecture
direction remain owner gates. Older manifests remain valid; they gain no network
authority until they adopt the V2.4 policy and grant `routine_public_network` to the
specific project.

V2.4 continuous progress keeps a project moving after each completed stage: the same
owner plans and fresh-admits the next long contract. A temporarily blocked acceptance
or external gate stays visibly `BLOCKED`, with dependent gates `UNEXECUTED`, while
independent feature, integration, test, documentation, performance, or evidence work
continues inside the existing authority envelope. It never fabricates acceptance,
bypasses safety or publication evidence, or creates filler and duplicate work.
Project-controlled helpers remain capacity-counted nonwriters under the same owner.

Delivery-first staging prioritizes core implementation, integration, and acceptance
candidates. Non-blocking deep security research may be deferred into one explicit
pre-release gate, while known critical/high findings, authentication and permission
fail-closed behavior, credential and destructive-data risks, required dependency or
supply-chain checks, and publication gates remain blocking. Focus-project preference
never bypasses capacity, admission, authority, or writer-lease requirements.

Optional per-task context-health readbacks make summary degradation and runtime
context warnings auditable. Scheduling emits one deduplicated renewal recommendation
to the sole migration controller; it never migrates a task based on a fixed number
of compactions or an invented token threshold.

Authorized stuck-thread recovery remains fail-closed. Waiting, ordinary latency,
one idle turn, and unknown state are not proof of a stuck task. Only the sole
migration controller may act after authoritative identity/blocker evidence, a fresh
materially-different admission, and the global migration lock. The provisional
successor stays `HANDOFF_ONLY` until `HANDOFF_ACCEPTED`; only then may the writer
lease transfer and the preserved old task be recoverably archived. Old tasks,
worktrees, and retained evidence are never deleted.

Cross-host relocation is a separate, proposal-only gate. A user's willingness to
consider a move does not authorize it. The scheduler may request one only after
source-host necessity and an exact target host/path are proven, and the packet must
preserve model/thinking, worktree and retained evidence, the single migration lock,
and a recoverable rollback. Execution waits for a new exact user authorization.

Real owner-dependent blockers are never left in silent waiting. The owner liaison
receives one exact blocker, the reason automation cannot solve it, minimal options,
the recommendation, and the next step. Authorized mechanical, path, harness, and
scheduling issues stay internal and do not generate low-value user messages.

Control-lifecycle readbacks distinguish a finished turn from a finished portfolio.
An active running monitor must renew a machine-auditable work lease with admission,
dispatch, ledger delta, or terminal evidence. Plans and timestamp-only snapshots do
not count. The first empty check cannot create a silent stop: every pause must first
send one deduplicated result or decision notice through the owner liaison, read back
its matching delivery turn, and remain visible for successful as well as failed
runs. Only then may the recurring automation pause.

## Install

Requires Python 3.10 or newer for the deterministic control script.

```powershell
git clone https://github.com/RedeatI/codex-project-pilot.git "$env:USERPROFILE\.codex\skills\codex-project-pilot"
```

Then invoke `$codex-project-pilot` or describe a multi-project portfolio task.

## Validate

```powershell
python scripts/portfolio_control.py --help
python scripts/portfolio_control.py audit-topology portfolio.json topology.json
python -m unittest discover -s tests -v
python tests/e2e_cli.py
python path\to\skill-creator\scripts\quick_validate.py .
```

See `references/portfolio-schema.md` for the manifest and
`references/thread-architecture.md` for control-plane and project-task topology.
See `references/execution-contracts.md` for admission and convergence behavior.
Use `references/project-task-prompt-template.md` for project-task dispatch prompts
and `references/gpt-5p6-sol-risk-calibration.md` for the evidence classification.
Read `references/github-publication.md` before any GitHub upload or visibility
change.

## Safety model

The Skill automates routing and evidence handling, not permission. External writes,
publication, releases, destructive cleanup, and credential use remain explicitly
authorized actions. Real secrets stop a publication candidate and are never printed
into reports or ledgers.

## License

Apache License 2.0.
