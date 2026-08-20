# Security

Prove It contains instruction text, a local prompt composer, and an optional local stdio MCP proof engine. The proof engine can read source files inside a configured workspace and can execute explicitly requested verification commands.

## Security model

The MCP is intended for local development use. It exposes no network listener and performs no authentication because stdio hosts launch it as a child process.

The host remains the primary security boundary. Keep its normal permission prompts, sandboxing, filesystem restrictions, credential isolation, and network policies enabled.

## Verification command boundary

`proveit.run_check` deliberately avoids a general shell:

- `shell=False`;
- argv arrays only;
- cwd must resolve inside the configured workspace;
- command basename must be allowlisted;
- execution timeout is bounded;
- output capture is bounded;
- mutating Git subcommands are rejected.

These controls reduce accidental misuse. They do **not** make command execution safe for untrusted repositories. Python, test runners, package-manager scripts, build systems, and Make/Gradle/Maven tasks can execute arbitrary project code.

Do not run verification against untrusted code outside an appropriate sandbox.

## Filesystem boundaries

`proveit.record_source` resolves paths before use and rejects paths that escape the configured workspace, including symlink escapes.

By default proof state is written to `.prove-it/` inside the workspace. `PROVE_IT_STATE_DIR` intentionally allows operators to place state elsewhere; when using that override, the operator is responsible for the destination's access controls.

Proof JSON and Markdown are written atomically. Permissions are tightened to owner-only (`0600`) where the platform permits it.

## Sensitive evidence

Proof state can contain:

- source excerpts;
- command lines;
- test/build output excerpts;
- file paths;
- repository source-state metadata.

Those may contain confidential information even when Prove It never intentionally reads secrets. `.prove-it/` is gitignored by this repository; downstream projects should also keep proof state out of version control unless deliberate review says otherwise.

Do not record secrets, tokens, passwords, private keys, or sensitive customer data as evidence.

## MCP dependency

The optional MCP integration depends on the official `mcp` Python package constrained to the stable v2 major line (`mcp>=2,<3`). Review dependency updates normally; Prove It does not auto-update its runtime dependencies.

## Prompt limitations

Instruction text cannot make downstream agents secure by itself. Security-sensitive work still requires appropriate architecture, code review, automated testing, runtime controls, and operational safeguards.

## Reporting vulnerabilities

For a hosted public repository, use the hosting platform's private vulnerability-reporting mechanism when available. Do not disclose secrets or weaponized exploit details in a public issue.
