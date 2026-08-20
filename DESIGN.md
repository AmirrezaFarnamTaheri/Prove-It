# Design

Prove It is built around one idea: engineering claims should resolve to evidence, but the amount of process should still match the risk.

## 1. One canonical skill tree

Human-maintained skill content lives under `skills/prove-it/`:

```text
skills/prove-it/
├── SKILL.md
├── agents/openai.yaml
├── protocols/core.md
├── profiles/
└── templates/
```

The repository does not commit generated Claude skill mirrors or copied Python package resources. Claude Code discovers the canonical `skills/` tree directly. Python wheel resources are copied from that same tree during package build.

This keeps one editable source of truth while still supporting both plugin and Python distribution.

## 2. Core vs conditional profiles

A rule belongs in `protocols/core.md` only when it is broadly useful across engineering work: source truth, evidence discipline, proportional rigor, contradiction search, verification honesty, and completion gates.

A rule belongs in `profiles/` only when its value depends on context. Examples include migration rollback, queue backpressure, fuzz testing, TUI cell-width handling, state-machine discipline, or architecture canonical models.

Specialized rigor is opt-in because irrelevant rigor is noise.

## 3. Templates describe task shape

Templates describe intent: implementation, research, planning, audit, consolidation, architecture reconstruction, or universal routing.

Profiles describe specialist constraints.

A security audit therefore uses an `audit` template plus the `security` profile. A secure feature implementation uses the `implementation` template plus the same security profile.

## 4. Adapters stay thin

Provider/model adapters contain presentation guidance only. They must not fork engineering policy.

If an adapter accumulates engineering rules, those rules belong in core or a conditional profile instead.

## 5. Evidence before confidence

Prompt-level reasoning distinguishes:

- Verified
- Strongly Inferred
- Assumed
- Unknown

The local proof engine adds provenance and freshness:

- server-observed vs agent-reported;
- fresh vs stale vs unknown.

The distinction is deliberate. A check that passed before a later code change should not remain conclusive forever.

## 6. Acceptance criteria are the proof boundary

The proof engine does not claim to prove an entire system. It proves the explicit acceptance contract recorded for one task.

That keeps READY meaningful and bounded.

A useful criterion is observable. "Improve quality" is not. "The unauthenticated request returns 401 and the regression test passes" is.

## 7. The MCP is a proof service, not an agent runtime

The MCP does not provide generic file editing, generic shell access, browser automation, Git mutation, deployment orchestration, or an alternative planner.

The host already owns those capabilities.

The MCP records and evaluates evidence around them.

It is optional by design. The Agent Skill remains useful when no Python runtime or MCP host is available.

## 8. Freshness is conservative

Source evidence records a file hash. If the file changes, that evidence becomes stale.

Verification checks in Git workspaces record a fingerprint over HEAD, tracked staged/unstaged changes, and untracked file contents. If that worktree fingerprint changes, the check becomes stale.

Non-Git check freshness may be unknown. Unknown is reported honestly rather than treated as a new observation.

## 9. Command restrictions are guardrails, not sandboxing

`proveit.run_check` removes shell interpolation, bounds cwd/time/output, restricts command names, and blocks mutating Git subcommands.

That is not equivalent to sandboxing. Test runners, interpreters, build tools, and package scripts execute code. Host security controls remain authoritative.

## 10. Generated artifacts stay generated

Compiled prompts, package-resource mirrors, wheel trees, proof reports, bytecode, and test caches are outputs, not source.

The repository should be reconstructable from canonical sources with:

```bash
make check
make wheel
make dist
```

## 11. Evaluation over rhetoric

Static evals protect composition invariants. Behavioral evaluation asks the more important question: does Prove It improve real engineering outcomes without unacceptable regressions or cost?

Material protocol changes should be compared on the same tasks against baseline and, where relevant, Prove It Lite. Record failures as well as wins.

## 12. Non-goals

Prove It is not:

- a jailbreak;
- a claim of autonomous perfection;
- a replacement for project-specific instructions;
- a substitute for tests, observability, review, or deployment controls;
- a universal architecture prescription;
- a security sandbox;
- a benchmark claim without data.

## Due diligence is a conditional operating mode

Broad technical due diligence has different information needs than ordinary implementation or code review. Prove It treats it as a dedicated profile/template pair rather than making executive assessment machinery universal.

The mode adds corpus accounting for whole-system claims, a nine-dimension technical asset lens, asset/capability inventory, risk-and-value discovery, knowledge preservation, selective peer benchmarking, and opportunity prioritization. It avoids arbitrary health scores and unsupported “10x” claims. Exhaustive traversal is required only when the requested scope and resulting claims actually demand it.

This preserves the central product rule: **rigor scales with consequence and claim breadth**.
