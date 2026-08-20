# Prove It proof engine

The local proof engine is an optional deterministic companion to the Prove It Agent Skill. It exists to make consequential completion claims auditable without replacing the coding agent's normal tools.

## Evidence boundary

Prove It distinguishes **server-observed** evidence from **agent-reported** evidence.

Server-observed evidence comes from:

- `proveit.record_source` — verifies a workspace file, optional line range / expected text, and SHA-256 digest;
- `proveit.run_check` — executes one allowlisted argv command without a shell and records exit code, duration, output digest/excerpt, and a Git worktree fingerprint when available.

`proveit.record_evidence` records observations produced by browser tools, deployed systems, external services, human inspection, or host-native tools. Those items remain agent-reported even if the agent labels their strength as verified.

Agent-reported evidence can support a PARTIAL result. It cannot by itself produce the strongest VERIFIED criterion state.

## Evidence freshness

Server-observed evidence is not permanent proof.

### Source evidence

Source evidence records the verified file's SHA-256 digest. On status/report, the proof engine re-hashes that file. If the digest differs or the file disappears, the evidence is stale.

### Check evidence

When a check runs inside a Git workspace, Prove It records a worktree fingerprint covering:

- current HEAD;
- tracked staged and unstaged changes (`git diff HEAD`);
- untracked file paths and contents.

If that fingerprint changes later, the check evidence becomes stale.

For non-Git workspaces, check freshness may be `unknown` because Prove It intentionally does not hash an arbitrary whole directory.

### Status effect

Stale server-observed evidence remains in the historical ledger but is ignored when deriving current VERIFIED/CONTRADICTED state.

This prevents a passing test or verified source anchor from remaining conclusive after later edits.

## Persistence and ledger integrity

Default state:

```text
.prove-it/
├── proof.json
└── PROOF.md
```

Set `PROVE_IT_STATE_DIR` to place the state elsewhere. Set `PROVE_IT_WORKSPACE` when the MCP host launches the server outside the target repository.

Writes use a temporary file, flush + `fsync`, and `os.replace` to avoid half-written ledgers. Owner-only permissions are applied where supported.

Every ledger load performs internal validation without a third-party JSON Schema dependency. Validation checks include:

- required top-level fields;
- schema version;
- criterion/evidence ID validity and uniqueness;
- allowed evidence relations, strengths, and provenance;
- criterion/evidence cross-reference consistency;
- non-empty task, criteria, and evidence summaries.

`proof.schema.json` documents the wire/storage structure for external tooling.

## Verification commands

`proveit.run_check` is narrower than a general shell tool:

- argv array only;
- `shell=False`;
- cwd must resolve inside the workspace;
- timeout is clamped to 1–1800 seconds;
- command basename must be allowlisted;
- mutating Git subcommands are rejected;
- captured output is truncated to 32k characters while SHA-256 represents the complete captured stdout/stderr.

Default command names are oriented to tests and builds (`pytest`, Python, uv, npm/pnpm/yarn/bun, cargo, Go, .NET, Make/CMake/Ninja, Maven/Gradle, and read-only Git).

Override the name allowlist with `PROVE_IT_ALLOWED_CHECKS`, a comma-separated list.

### Not a sandbox

The command restrictions are guardrails, not isolation. Interpreters, test runners, build systems, and package-manager scripts can execute project code. Do not use `proveit.run_check` on untrusted repositories without an external sandbox.

## Readiness semantics

Current evidence determines criterion state:

- `VERIFIED` — at least one fresh/usable server-observed verified supporting item and no fresh/usable server-observed contradiction;
- `PARTIAL` — supporting evidence exists but not at current server-observed verified strength;
- `CONTRADICTED` — fresh/usable server-observed contradicting evidence exists;
- `PENDING` — no current supporting evidence exists;
- `BLOCKED` / `WAIVED` — explicit override with a non-empty reason.

Overall readiness:

- `READY` — all criteria are VERIFIED or WAIVED, and at least one is VERIFIED;
- `CONDITIONAL` — no criterion is CONTRADICTED but at least one is PARTIAL, PENDING, or BLOCKED;
- `NOT_READY` — any criterion is CONTRADICTED.

A READY result proves only the recorded acceptance contract.

## Source-state reporting

A proof session records source state when it starts. Status/report also captures source state at evaluation time. In a Git workspace this includes commit, branch, dirty flag, and worktree fingerprint.

This makes it clear whether the repository changed between the beginning of the proof and the final report.

## MCP surface

Tools:

- `proveit.start`
- `proveit.add_criterion`
- `proveit.record_source`
- `proveit.record_evidence`
- `proveit.run_check`
- `proveit.set_criterion_state`
- `proveit.status`
- `proveit.report`

Resources:

- `proveit://proof/current`
- `proveit://proof/report`

The MCP intentionally excludes generic filesystem, shell, browser, Git mutation, and deployment tools.
