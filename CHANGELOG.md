# Changelog

All notable changes to Prove It are documented here.

## [0.4.0] - 2026-08-20

### Added

- Dedicated `technical-due-diligence` profile for corpus-accounted executive assessments across architecture, engineering, security, reliability, data, performance, operations, product/UX, and governance.
- Technical due-diligence task template and static eval fixture.
- Explicit asset/capability inventory, risk-and-value discovery, opportunity portfolio, and decision-oriented report structure for broad assessments.

### Changed

- Strengthened consolidation guidance around hidden/unfinished capabilities, feature parity, institutional-knowledge preservation, migration sequencing, and rollback.
- Kept exhaustive traversal, peer benchmarking, and transformational opportunity discovery conditional instead of making them universal requirements.
- Removed the package maturity classifier so release metadata does not overstate or understate behavioral maturity while benchmarking remains ongoing.

## [0.3.0] - 2026-08-19

### Added
- Evidence freshness tracking for server-observed source and verification evidence.
- Workspace fingerprints for Git-backed verification checks so proof can become stale after relevant code changes.
- Ledger integrity validation with bidirectional criterion/evidence cross-reference checks.
- Canonical Claude plugin layout under `skills/prove-it/` with ChatGPT skill metadata colocated inside the skill.
- Repository-hygiene tests that enforce version sync, canonical layout, valid MCP example configuration, and resolvable local documentation links.
- Durable product specification and release-process documentation.

### Changed
- Made `skills/prove-it/` the single source of truth for skill instructions, profiles, and templates.
- Generate wheel resource mirrors only at build time instead of committing duplicate source trees.
- Generate the standalone master prompt under `build/generated/` instead of committing `dist/` artifacts.
- Hardened proof-session input validation, custom IDs, override reasons, and task-input validation.
- Hardened bounded verification-command resolution and made missing optional MCP SDK failures explicit.
- Reworked README, design, security, proof-engine, evaluation, and contribution documentation around the final plugin architecture.
- Updated the package and plugin metadata to version 0.3.0.

### Removed
- Historical `.claude/skills/prove-it` mirror.
- Committed `src/prove_it/resources` mirror.
- Committed generated master prompt and compiled example prompts.
- Stale release snapshot document and obsolete resource-sync scripts.
- Root-level duplicate `SKILL.md`, protocol/profile/template trees, and plugin-level `agents/` metadata.

## [0.2.0] - 2026-08-19

### Added
- Local stdio MCP proof engine with `proveit.*` tools and proof resources.
- Durable acceptance-criteria ledger in `.prove-it/proof.json`.
- Server-observed source hashing and bounded verification checks.
- Deterministic READY / CONDITIONAL / NOT_READY reporting and `.prove-it/PROOF.md`.
- Proof schema and proof-engine documentation.
- Claude plugin metadata and generated Claude skill bundle.
- `prove-it-mcp`, `prove-it-proof`, and `prove-it mcp-config` entrypoints.
- Packaged protocol resources so installed wheels work outside a checkout.

### Changed
- Prove It skill integrates with the proof engine when available while retaining a no-MCP fallback.
- Project description and README distinguish Prove It Lite, full Prove It, and Prove It + MCP.

## [0.1.0] - 2026-08-19

### Added
- Core evidence-driven engineering protocol.
- Conditional profiles, task templates, model adapters, prompt composer, static eval fixtures, examples, and generated universal master prompt.
