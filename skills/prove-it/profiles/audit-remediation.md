# Profile: Audit & Remediation

Activate for code review, implementation auditing, readiness review, roadmap verification, or authorized remediation. For executive/portfolio technical due diligence, also load `technical-due-diligence.md`.

<audit_profile>
Treat prior completion claims as untrusted until evidenced. Do not assume file presence proves behavior, a patch proves a bug is fixed, passing tests prove sufficient coverage, polished documentation is correct, or a compiled migration is operationally safe.

For material items establish objective, intended outcome, evidence inspected, implementation status, correctness, completeness, architectural impact, defects, risks, test gaps, configuration/documentation alignment, and verdict.

Statuses: Fully Correct | Correct but Needs Refinement | Mostly Correct With Defects | Partially Implemented | Incorrectly Implemented | Missing | Regressed | Unverifiable.
Verdicts: Pass | Conditional Pass | Fail | Blocked / Unverifiable.

When repair is authorized: reproduce/prove the defect where practical, identify root cause, fix it, update affected layers, add regression protection, rerun validation, and reconcile related documentation/configuration.
</audit_profile>
