# GitHub publication

Read this reference whenever the portfolio action creates a repository, changes
visibility, pushes commits, or publishes a release.

## Scope and identity

- Require explicit authorization for the exact repository and visibility.
- Prove GitHub account or organization, repository existence, visibility, remote,
  branch, and authentication from runtime tools. Do not infer them from a task
  title or old report.
- If a corresponding repository already exists, read it back and do not create a
  duplicate unless the user explicitly requests a mirror.
- Preserve non-GitHub remotes. Add a named GitHub remote instead of overwriting an
  unrelated `origin`.

## Privacy gate

Before staging or pushing, inspect tracked, untracked, ignored, and historical
content for:

- environment files and secret-bearing local configuration;
- credentials, API tokens, private keys, certificates, and signing material;
- personal or production data, databases, logs, backups, dumps, and archives;
- IDE, operating-system, machine-path, cache, and build artifacts;
- unexpectedly large binaries or model files;
- secrets embedded in Git history.

Report paths and categories, never secret values. Exclude unsafe files through
`.gitignore` or index changes without deleting the user's local originals. A real
secret stops publication until it is removed from the candidate and rotated when
necessary.

## Initial repository upload

1. Inspect `git status -sb`, diffs, HEAD, branch, and sanitized remotes.
2. Stage only the user-confirmed safe scope and run `git diff --cached --check`.
3. Re-run the privacy gate on the exact staged or committed candidate.
4. Create the repository with the authorized visibility.
5. If workflows could trigger on first push, disable Actions before pushing or
   obtain explicit authorization for those runs.
6. Push the intended branch without force.
7. Read back repository owner/name, visibility, URL, default branch, remote ref,
   candidate commit, and local status.

Use a private repository by default only when the user has not requested public or
internal visibility. Public release also requires a license and a deliberate review
of documentation, attribution, security contact, and redistribution rights.

Never claim upload completion from a local commit alone.
