# Template: Planning & Architecture

<task_mode>planning_architecture</task_mode>

<planning_requirements>
- Ground the plan in the actual current system and constraints.
- Define invariants, boundaries, interfaces, and acceptance criteria before sequencing implementation.
- Identify prerequisites, dependencies, blockers, parallelizable work, irreversible steps, rollback points, and validation gates.
- Prefer implementable slices that produce observable value and preserve system coherence.
- Record meaningful alternatives only when the choice affects correctness, risk, cost, compatibility, or maintainability.
</planning_requirements>

<planning_output>
Produce an executable dependency-aware plan with explicit verification for each phase. Avoid enterprise ceremony that does not help execution.
</planning_output>
