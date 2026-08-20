# Prove It — Product specification

## Product statement

Prove It makes coding agents earn the word **done**.

It combines a portable Agent Skill with optional local proof tooling. The skill changes engineering behavior; the proof engine records acceptance criteria and evidence for consequential completion claims.

## Users

Primary users:

- developers delegating non-trivial repository work to coding agents;
- teams standardizing engineering quality across agents/models;
- maintainers auditing or remediating unfamiliar systems;
- operators who need an inspectable record of why an agent claimed completion.

## Problems

Coding agents commonly fail in predictable ways:

- infer architecture from superficial clues;
- stop at advice when implementation was requested;
- apply the same amount of process to every task;
- miss contradictory paths or stale documentation;
- claim tests/builds/deployments were verified when they were not;
- treat a previous passing check as permanently conclusive after later edits;
- perform broad audits as defect lists while missing valuable capabilities, institutional knowledge, and modernization leverage.

Prove It addresses these failure modes without replacing host-native development tools.

## Product layers

### Agent Skill

`skills/prove-it/` provides:

- universal evidence-driven engineering rules;
- conditional specialist profiles;
- task-mode templates, including technical due diligence;
- a dedicated due-diligence profile for corpus-accounted risk/value assessment;
- proof-engine usage guidance when MCP is available.

The skill must remain useful with no Python runtime and no MCP connection.

### Prompt composer

The Python CLI can compile task JSON + a template + selected profiles + a thin model adapter into a standalone structured prompt.

The composer is useful for explicit prompt pipelines, testing, and portability. It is not required for ordinary skill use.

### Local proof engine

The optional stdio MCP stores a workspace-local acceptance contract and evidence ledger.

It provides only proof-specific operations. It does not replace editing, shell, browser, deployment, or generic Git tooling.

## Proof workflow

1. Define a task and observable acceptance criteria.
2. Capture initial source state.
3. Perform normal engineering work with host-native tools.
4. Attach server-observed source/check evidence where practical.
5. Record external observations as agent-reported evidence.
6. Re-evaluate evidence freshness as the repository changes.
7. Compute criterion states and overall readiness.
8. Generate JSON and Markdown proof reports before consequential completion claims.

For trivial work, MCP use is optional and often unnecessary.

## MCP tools

### `proveit.start`

Create or replace a proof session, capture initial source state, and define acceptance criteria.

### `proveit.add_criterion`

Add one uniquely identified acceptance criterion.

### `proveit.record_source`

Verify a file and optional line range/expected text inside the workspace, record SHA-256, and attach server-observed evidence.

### `proveit.record_evidence`

Record evidence observed through the host, an external system, a browser, or a human. Provenance remains agent-reported.

### `proveit.run_check`

Run one bounded, allowlisted argv command without a shell. Record exit code, duration, output digest/excerpt, and a Git worktree fingerprint where available.

### `proveit.set_criterion_state`

Mark a criterion blocked or waived with a reason, or clear the override. Verified/contradicted states remain evidence-derived.

### `proveit.status`

Return current criterion states, source state, evidence freshness, and readiness.

### `proveit.report`

Return the complete report and optionally persist `.prove-it/PROOF.md`.

## MCP resources

- `proveit://proof/current` — current proof ledger JSON.
- `proveit://proof/report` — rendered proof report.

## Evidence semantics

### Provenance

- **server-observed** — the local proof process directly inspected the evidence or executed the check;
- **agent-reported** — evidence was observed elsewhere and reported into the ledger.

### Freshness

- **fresh** — current local state still matches the recorded server observation;
- **stale** — the relevant file/worktree has changed since observation;
- **unknown** — freshness cannot be recomputed safely;
- **not_applicable** — agent-reported evidence is not locally freshness-checked.

Stale server-observed evidence is historical evidence but no longer determines VERIFIED or CONTRADICTED state.

## Criterion states

- **VERIFIED** — current server-observed verified support exists and no current server-observed contradiction exists.
- **PARTIAL** — supporting evidence exists but not at current server-observed verified strength.
- **CONTRADICTED** — current server-observed contradicting evidence exists.
- **PENDING** — no current meaningful support exists.
- **BLOCKED** — completion depends on an unavailable external condition, with reason.
- **WAIVED** — the acceptance criterion was explicitly waived, with reason.

Overall readiness:

- **READY** — all criteria are VERIFIED or WAIVED, with at least one VERIFIED criterion;
- **CONDITIONAL** — no criterion is contradicted, but one or more remain partial, pending, or blocked;
- **NOT_READY** — any criterion is contradicted.

## Persistence

Default workspace state:

```text
.prove-it/
├── proof.json
└── PROOF.md
```

Writes are atomic. Proof state is intentionally ignored by this repository and should normally remain local because excerpts and verification output can contain sensitive material.

## Runtime and compatibility

- Python: 3.10+
- MCP transport: local stdio
- MCP SDK: official Python SDK stable v2 line (`mcp>=2,<3`)
- Cloud service: none required
- Authentication: none for local stdio

## Non-goals

Prove It does not provide:

- generic file editing;
- generic shell access;
- browser automation;
- deployment orchestration;
- autonomous background agents;
- remote MCP hosting;
- a security sandbox;
- a universal guarantee that READY means the entire system is correct.

## Acceptance criteria for the product

- Skill content remains usable independently of the Python tooling.
- The plugin follows current Claude Code plugin layout conventions.
- Composer resources work from an installed wheel outside a checkout.
- Static evals work both from source and installed resources.
- Proof ledgers are structurally validated before use.
- Source/check evidence can become stale after relevant repository changes.
- Path escapes are rejected for source evidence and verification cwd.
- Proof writes are atomic.
- Readiness is deterministic from the recorded contract and current usable evidence.
- Documentation states security and verification limitations precisely.
- Due-diligence mode evaluates both material risks and technical asset value without forcing exhaustive/transformational ceremony onto focused tasks.
