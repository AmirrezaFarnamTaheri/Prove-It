# Prove It

**If you claim it works, prove it.**

Prove It is an evidence-driven engineering plugin for coding agents. It combines a reusable engineering skill with an optional local MCP proof engine that turns acceptance criteria into a durable evidence contract.

Prove It is deliberately not another agent runtime. The host keeps doing normal repository, editor, browser, Git, and shell work. Prove It adds the discipline around that work: inspect source truth, scale rigor to risk, implement the whole change, verify what matters, and make only completion claims that the evidence supports.

## What it changes

A coding agent should not earn **done** by sounding confident. Prove It pushes the agent to:

1. inspect real source state before inventing explanations;
2. distinguish verified facts, inference, assumptions, and unknowns;
3. scale investigation and verification to the actual risk;
4. complete the requested behavior instead of stopping at commentary;
5. search for contradictory evidence on consequential conclusions;
6. verify with checks appropriate to the task;
7. treat broad due diligence as both risk discovery and asset/value discovery;
8. map consequential completion claims to observable evidence.

For work that needs a durable proof trail, the optional local MCP adds:

```text
user task
   │
   ▼
Prove It skill ───────► engineering work with host-native tools
   │
   ├─ acceptance criteria
   ├─ source truth
   ├─ proportional rigor
   └─ verification discipline
   │
   ▼
local prove-it MCP
   ├─ source-state capture
   ├─ source evidence + file hashes
   ├─ bounded verification checks
   ├─ stale-evidence detection
   ├─ evidence ledger
   └─ readiness report
   │
   ▼
.prove-it/proof.json + .prove-it/PROOF.md
```

## Editions

| Edition | Best for | Surface |
| --- | --- | --- |
| **Prove It Lite** | Drop-in everyday discipline | One `SKILL.md` |
| **Prove It** | Repository-scale and consequential engineering | Skill + profiles + templates + composer + evals |
| **Prove It + local MCP** | Auditable acceptance contracts | Full Prove It + `proveit.*` proof tools |

Prove It Lite is maintained separately so the small edition stays small.

## Install as a Claude Code plugin

The repository follows the current Claude Code plugin layout: `.claude-plugin/plugin.json` at the root and the skill at `skills/prove-it/`.

For a local checkout:

```text
/plugin marketplace add /absolute/path/to/prove-it
/plugin install prove-it@prove-it
```

For a public GitHub repository:

```text
/plugin marketplace add <owner>/prove-it
/plugin install prove-it@prove-it
```

The skill works without Python and without MCP.

## Install as a standalone Agent Skill

`skills/prove-it/` is the portable skill bundle. Copy that directory into the Agent Skills location used by your host, or package it as `skill.zip`.

The skill entrypoint is:

```text
skills/prove-it/SKILL.md
```

The skill loads `protocols/core.md` plus only the profiles relevant to the task. It does not load every specialist profile by default.

## Install the optional local proof engine

Requires Python 3.10+.

From a checkout:

```bash
python -m pip install -e '.[mcp]'
```

From a published package:

```bash
python -m pip install 'prove-it-protocol[mcp]'
```

This installs:

- `prove-it` — prompt composer and static eval CLI;
- `prove-it-mcp` — local stdio MCP proof engine;
- `prove-it-proof` — human CLI for proof state and reports.

The MCP integration targets the stable v2 line of the official MCP Python SDK (`mcp>=2,<3`) and Python 3.10+.

### Connect the local MCP

Generate a portable stdio configuration:

```bash
prove-it mcp-config
```

Or pin a workspace explicitly:

```bash
prove-it mcp-config --workspace /path/to/repo
```

Equivalent configuration:

```json
{
  "mcpServers": {
    "prove-it": {
      "command": "prove-it-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

A copy is provided as [`.mcp.json.example`](.mcp.json.example).

The Claude plugin does **not** auto-enable the MCP. That keeps the plugin usable without a Python runtime or third-party dependency. Enable the proof engine only where a durable proof contract is useful.

## Proof workflow

For consequential work:

1. call `proveit.start` with a concise task and observable acceptance criteria;
2. perform engineering work with the host's normal tools;
3. attach local source evidence with `proveit.record_source`;
4. attach bounded local checks with `proveit.run_check` when appropriate;
5. record external or host-observed evidence with `proveit.record_evidence`;
6. inspect unresolved criteria with `proveit.status`;
7. call `proveit.report` before making the final consequential completion claim.

### MCP tools

| Tool | Purpose |
| --- | --- |
| `proveit.start` | Start a proof session and capture initial source state |
| `proveit.add_criterion` | Add one acceptance criterion |
| `proveit.record_source` | Verify workspace source evidence and SHA-256 it |
| `proveit.record_evidence` | Record explicitly agent-reported evidence |
| `proveit.run_check` | Execute one bounded allowlisted verification command without a shell |
| `proveit.set_criterion_state` | Mark a criterion blocked/waived or clear that override |
| `proveit.status` | Compute criterion states, evidence freshness, and readiness |
| `proveit.report` | Persist and return the complete proof report |

Resources:

- `proveit://proof/current`
- `proveit://proof/report`

See [`docs/proof-engine.md`](docs/proof-engine.md) for the exact evidence and freshness semantics.

## Proof semantics

Evidence provenance matters:

- **server-observed** — Prove It directly verified a source anchor or executed a local check;
- **agent-reported** — the host/agent reports an observation produced elsewhere.

Server-observed evidence is also freshness-aware:

- source evidence becomes stale if the verified file hash changes;
- check evidence recorded in a Git workspace becomes stale if the worktree fingerprint changes;
- evidence whose freshness cannot be recomputed is reported as `unknown`; the original server observation remains usable but the report exposes that freshness caveat.

Stale server-observed evidence does not keep a criterion VERIFIED or CONTRADICTED.

Criterion states:

- **VERIFIED** — fresh server-observed supporting evidence exists and no fresh server-observed contradiction exists;
- **PARTIAL** — only non-conclusive supporting evidence exists;
- **CONTRADICTED** — fresh server-observed contradicting evidence exists;
- **PENDING** — no current supporting evidence exists;
- **BLOCKED / WAIVED** — explicit exceptional state with a reason.

Overall readiness:

- **READY** — every criterion is VERIFIED or WAIVED, with at least one VERIFIED criterion;
- **CONDITIONAL** — nothing is contradicted, but at least one criterion is partial, pending, or blocked;
- **NOT_READY** — at least one criterion is contradicted.

A READY result proves the **recorded acceptance contract**, not every possible property of the software.

## Verification command boundary

`proveit.run_check` is narrower than a generic shell tool: it uses argv arrays with `shell=False`, keeps cwd inside the workspace, bounds execution time and captured output, blocks mutating Git subcommands, and requires an allowlisted command name.

It is **not a security sandbox**. Python, package-manager scripts, build tools, and test runners can execute project code. Keep the host's normal approval, sandboxing, and credential-isolation policies enabled.

Override the command-name allowlist with:

```bash
export PROVE_IT_ALLOWED_CHECKS="pytest,python,npm,cargo,go"
```

## Prompt composer

Prove It remains useful without the MCP:

```bash
prove-it list
prove-it compose \
  --task examples/security-review/task.json \
  --template audit \
  --profile security \
  --profile audit-remediation \
  --adapter generic \
  -o build/security-review-prompt.md
prove-it validate --prompt build/security-review-prompt.md
prove-it eval
```

Canonical protocol resources are embedded into built wheels at package-build time, so installed commands work outside a repository checkout without committing generated resource mirrors.

For executive technical due diligence:

```bash
prove-it compose \
  --task path/to/due-diligence-task.json \
  --template due-diligence \
  --profile technical-due-diligence \
  --profile peer-benchmarking \
  --profile audit-remediation \
  --adapter generic \
  -o build/due-diligence-prompt.md
```

The due-diligence profile adds corpus accounting, a nine-dimension technical asset lens, asset/capability inventory, risk-and-value discovery, knowledge preservation, peer comparison where useful, and evidence-based opportunity prioritization. It deliberately does not make exhaustive traversal or “10x” claims mandatory for ordinary tasks.

## Repository layout

```text
.
├── .claude-plugin/            # Claude Code plugin / marketplace metadata
├── skills/prove-it/           # Canonical Agent Skill + profiles + templates
├── adapters/                  # Thin model/host prompt adapters
├── src/prove_it/              # Composer + proof core + MCP wrapper
├── evals/                     # Static fixtures and behavioral rubric
├── examples/                  # Input examples; generated prompts are not committed
├── docs/                      # Product, proof, design, and source documentation
├── tests/                     # Composer / proof / packaging regression tests
├── manifest.json              # Composer resource map
├── proof.schema.json          # Proof-ledger schema
└── spec.task.schema.json      # Composer task schema
```

Generated prompt files, wheel build trees, cached package resources, bytecode, test caches, and proof ledgers are intentionally excluded from source control.

## Development

Install development dependencies:

```bash
python -m pip install -e '.[dev]'
```

Run the local gate:

```bash
make check
```

Run the optional MCP SDK integration gate:

```bash
python -m pip install -e '.[dev,mcp]'
pytest -q
```

Build the wheel:

```bash
make wheel
```

Generate the standalone master prompt only when needed:

```bash
make dist
```

The generated file is written under `build/generated/` and is not committed.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/release-process.md`](docs/release-process.md) before releasing changes.

## Design boundary

The local MCP exists for one question:

> **Does this help establish whether the agent's engineering claim is actually true?**

If not, it does not belong in `proveit.*`.

## Status

Current version: **0.4.0**.

The protocol and proof core are covered by deterministic local tests and static evals. Behavioral model benchmarking remains an ongoing evaluation program; Prove It does not claim universal improvement without benchmark evidence.

## License

MIT. See [`LICENSE`](LICENSE).
