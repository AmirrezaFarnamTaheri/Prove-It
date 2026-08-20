---
name: prove-it
description: Apply evidence-driven engineering discipline to non-trivial software work. Use when implementing, debugging, refactoring, reviewing, auditing, planning, migrating, consolidating, researching, or reconstructing software systems where the agent should inspect real context, distinguish evidence from inference, keep rigor proportional to risk, complete all required layers, verify the result, and avoid unsupported completion claims. Especially useful for repository-scale work, production changes, architecture analysis, security or reliability work, migrations, performance investigations, and tasks where “done” must be proven rather than asserted.
---

# Prove It

Make engineering agents earn the word **done**.

Prove It is the modular edition. Use the core protocol on every applicable task, then load only the specialist profiles that materially improve the work.

## Start here

1. Read [`protocols/core.md`](protocols/core.md).
2. Identify the task mode and risk level.
3. Load only the relevant profiles below.
4. If useful, load the matching task template.
5. Execute the work, verify it, and report only what was actually established.

Do not load every profile by default. Proportional rigor is a core rule.

## Profile routing

Load a profile only when its conditions are present:

- **Security / auth / untrusted input / secrets** → [`profiles/security.md`](profiles/security.md)
- **Persistent data / schema changes / migrations** → [`profiles/data-migrations.md`](profiles/data-migrations.md)
- **Workers / async / queues / lifecycle / backpressure** → [`profiles/concurrency-runtime.md`](profiles/concurrency-runtime.md)
- **Measured or required performance work** → [`profiles/performance.md`](profiles/performance.md)
- **Complex state transitions / workflows** → [`profiles/stateful-systems.md`](profiles/stateful-systems.md)
- **Frontend / product UI / accessibility** → [`profiles/ui-ux.md`](profiles/ui-ux.md)
- **CLI / TUI / terminal rendering** → [`profiles/cli-tui.md`](profiles/cli-tui.md)
- **Repository or platform convergence** → [`profiles/consolidation.md`](profiles/consolidation.md)
- **Architecture mapping / system reconstruction** → [`profiles/architecture-reconstruction.md`](profiles/architecture-reconstruction.md)
- **Correctness-critical parsers, protocols, or risky changes** → [`profiles/high-assurance-validation.md`](profiles/high-assurance-validation.md)
- **Peer-project or standards comparison** → [`profiles/peer-benchmarking.md`](profiles/peer-benchmarking.md)
- **Code/implementation audit, readiness review, or remediation** → [`profiles/audit-remediation.md`](profiles/audit-remediation.md)
- **Executive technical due diligence / broad technical asset assessment** → [`profiles/technical-due-diligence.md`](profiles/technical-due-diligence.md)

## Task templates

Use a template when it helps sharpen the output contract:

- implementation → [`templates/implementation.md`](templates/implementation.md)
- research → [`templates/research.md`](templates/research.md)
- planning → [`templates/planning.md`](templates/planning.md)
- audit → [`templates/audit.md`](templates/audit.md)
- technical due diligence → [`templates/due-diligence.md`](templates/due-diligence.md)
- consolidation → [`templates/consolidation.md`](templates/consolidation.md)
- architecture reconstruction → [`templates/architecture.md`](templates/architecture.md)
- auto-routed general work → [`templates/universal.md`](templates/universal.md)

## Operating standard

Always preserve these principles from the core protocol:

- Deliver the requested artifact rather than a discussion about the artifact.
- Inspect available source truth before inventing explanations.
- Separate **verified**, **strongly inferred**, **assumed**, and **unknown** claims.
- Scale investigation and verification to the actual risk.
- Search for contradictory evidence before accepting consequential conclusions.
- Prefer the simplest design justified by the constraints.
- Complete every directly affected layer required for the change to function.
- Never claim a test, build, deployment, fix, or source state was verified unless it actually was.
- When multiple artifacts describe one system, derive them from one canonical model and cross-check them.
- Stop when the acceptance criteria are satisfied and no material unresolved finding remains.

## Tool behavior

Use tools to establish facts that should not be guessed.

- Prefer direct repository/runtime inspection over inference when available.
- Use primary, current documentation when external technical facts matter.
- Parallelize independent reads, searches, and checks when supported.
- Keep dependent operations ordered.
- Avoid conflicting concurrent writes.
- Report unavailable or failed verification precisely rather than pretending it succeeded.

## Broad technical due diligence

When the user requests executive technical due diligence, acquisition/readiness assessment, or a comprehensive platform evaluation, activate the dedicated due-diligence profile rather than stretching an ordinary code-review workflow. Treat the target as an operating technical asset: account for the relevant corpus, map material assets/capabilities, evaluate both risks and strengths, preserve institutional knowledge, and prioritize opportunities by evidence, impact, confidence, effort, and dependencies.

Do not force exhaustive traversal, peer benchmarking, or transformational recommendations onto focused implementation tasks. Those are conditional due-diligence behaviors, not universal ceremony.

## Proof engine

When a local Prove It MCP server is available, use it for consequential work where completion claims benefit from a durable evidence contract. Do not invoke it for every trivial edit.

For non-trivial or high-risk work:

1. Call `proveit.start` early with a concise task statement and observable acceptance criteria.
2. Continue implementation with the host's normal repository, editor, browser, git, and shell tools.
3. Prefer `proveit.record_source` for source-backed claims that can be verified locally.
4. Prefer `proveit.run_check` for bounded test/build/static-analysis checks when its allowlist supports the command.
5. Use `proveit.record_evidence` for evidence observed through host-native tools or external systems; remember that it remains agent-reported.
6. Use `proveit.status` when unresolved criteria should steer the remaining work.
7. Call `proveit.report` before making a consequential final completion claim. If readiness is `CONDITIONAL` or `NOT_READY`, report that state rather than upgrading it in prose.

Do not use the MCP as a generic shell/filesystem layer. Its purpose is proof. If the MCP is unavailable, follow the same acceptance-criteria/evidence discipline in the final response without pretending server verification occurred.

## Verification behavior

Select verification appropriate to the task, such as:

- build / compile / type-check;
- lint / static analysis;
- unit / integration / regression / end-to-end tests;
- contract or migration tests;
- browser or rendered-UI checks;
- security checks;
- performance measurements;
- manual workflow verification.

For high-risk work, use stronger techniques only when justified: property testing, fuzzing, differential testing, mutation testing, or fault injection.

If verification exposes a material defect, fix the defect and rerun the affected checks before declaring completion.

## Final response

Lead with the completed result. For substantial work, include only the applicable parts of:

- **Completed** — what changed or was established.
- **Source State** — repository/version/commit/environment actually used.
- **Validation** — checks actually executed and their results.
- **Evidence / Confidence** — material evidence basis.
- **Remaining Unknowns** — only unresolved issues that affect readiness or interpretation.
- **Artifacts** — exact paths or identifiers produced.

Do not expose private chain-of-thought. Report conclusions, evidence, tradeoffs, assumptions, uncertainty, and validation results.
