# Contributing

Contributions are welcome when they improve measurable engineering behavior, proof integrity, host compatibility, or repository maintainability.

## Source of truth

Edit canonical files only:

- Agent Skill: `skills/prove-it/`
- Composer adapters: `adapters/`
- Python runtime: `src/prove_it/`
- Static evals: `evals/cases/`
- Documentation: `docs/` plus the root project docs

Do not commit generated package-resource mirrors, compiled prompts, wheel trees, proof ledgers, bytecode, or test caches.

## Set up

```bash
python -m pip install -e '.[dev]'
```

For MCP SDK integration tests:

```bash
python -m pip install -e '.[dev,mcp]'
```

## Before changing protocol text

Ask:

1. Is this rule broadly universal, or should it be a conditional profile?
2. What concrete failure mode does it prevent?
3. Could it make unrelated tasks worse?
4. Can the change be represented in a regression fixture?
5. Is the wording falsifiable, or merely more forceful?

Prefer conditional rules over global mandates when applicability depends on system constraints.

## Required checks

Run:

```bash
make check
```

That runs the test suite, static composition evals, generates the standalone master prompt under `build/generated/`, and validates it.

For package changes also run:

```bash
make wheel
```

Then install the wheel into a clean temporary target and verify `prove-it list`, `prove-it eval`, and proof-core imports outside the checkout.

For Claude plugin changes, run Claude Code's plugin validator when available:

```text
/plugin validate
```

## Tests

Add regression coverage for defects, especially around:

- proof-ledger integrity;
- evidence freshness;
- path/workspace boundaries;
- command restrictions;
- readiness derivation;
- installed-package resource discovery;
- plugin metadata and version consistency.

The optional official-MCP integration test may skip when the `mcp` extra is not installed. It must run in CI/release environments that install `.[dev,mcp]`.

## Behavioral changes

For material prompt behavior changes, add or update an eval case. When you have model-run evidence, record:

- model and version;
- date;
- relevant settings/tool environment;
- baseline condition;
- candidate condition;
- improvements;
- regressions;
- token/time overhead when available.

Do not present anecdotal success as a benchmark.

## Documentation

Update docs in the same change when behavior, CLI commands, MCP semantics, installation, security boundaries, or packaging changes.

Relative links should resolve from the repository. Commands should be executable as written or clearly labeled as illustrative.

## Style

Prefer direct, testable language. Avoid superlatives such as "perfect", "ultimate", "bulletproof", or "zero-risk".

## Release discipline

Follow [`docs/release-process.md`](docs/release-process.md). Keep the version synchronized across `pyproject.toml`, `manifest.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and `CHANGELOG.md`.
