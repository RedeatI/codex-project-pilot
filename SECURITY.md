# Security policy

Do not include credentials, tokens, private keys, personal data, production data,
or secret values in issues, manifests, ledgers, fixtures, or command output.

Report a vulnerability through GitHub private vulnerability reporting when it is
available. Otherwise open a minimal public issue without sensitive details and ask
the maintainer for a private channel.

The ledger is tamper-evident, not an authorization or secret store. A stale ledger
lock is fail-closed and must be inspected before an explicitly authorized recovery.
