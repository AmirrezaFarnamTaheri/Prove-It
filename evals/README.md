# Evals

Prove It uses two evaluation layers.

## 1. Static composition evals

`prove-it eval` verifies prompt assembly invariants:

- core/profile/template ordering;
- required markers;
- profile activation;
- forbidden leakage;
- installed resource availability.

These tests catch packaging and prompt-construction regressions. They do not prove the prompt improves model behavior.

## 2. Behavioral model evals

Behavioral evals compare actual agent outcomes on the same task under controlled conditions.

Recommended conditions:

1. baseline agent instructions;
2. Prove It Lite;
3. full Prove It;
4. full Prove It + proof engine where the task benefits from a durable acceptance contract.

Repeat stochastic runs when the cost is justified.

## Suggested rubric

Score each dimension 0–2:

- **Task completion** — was the requested artifact/result actually produced?
- **Correctness** — does it satisfy deterministic tests or other objective criteria?
- **Evidence discipline** — are factual claims grounded and uncertainty separated?
- **Scope control** — did the agent avoid both under-solving and unnecessary rewrites?
- **Verification honesty** — are checks actually run distinguished from checks merely suggested?
- **Defect discovery** — for audit tasks, are findings reproducible and material?
- **Regression resistance** — do fixes include meaningful proof against recurrence?
- **Operational realism** — are failure/recovery/deployment implications handled when relevant?
- **Efficiency** — is added rigor worth the token/tool/time overhead?

## Deterministic grading first

Prefer executable or structural graders before an LLM judge:

- tests;
- build/type/lint status;
- exact files or API behavior;
- repository diff constraints;
- expected command output;
- schema validation;
- proof-report readiness.

Use model-based judging only for dimensions that cannot be measured directly, and preserve the rubric and judge version.

## Run record

For each behavioral run capture:

```text
case:
condition:
model/version:
date:
tool environment:
seed/settings if available:
result:
objective score:
subjective score:
tokens:
wall time:
material failure notes:
```

Publish losses as well as wins. A protocol change should not ship merely because its wording sounds stronger.
