# Profile: Consolidation, Migration & Capability Absorption

Activate when comparing, merging, migrating, or modernizing projects, branches, versions, or platforms.

<consolidation_profile>
Establish source and target boundaries, then inventory current, hidden, partial, experimental, disabled, legacy, and internal capabilities; reusable modules; automation; stronger abstractions; domain rules; operational procedures; workarounds; tests/fixtures that encode intent; and historical lessons. Include inactive or unfinished paths when they may contain reusable behavior or institutional knowledge, but do not preserve dead complexity merely because it exists.

Trace material dependencies, integration points, data/control paths, configuration paths, and feature parity deeply enough to understand what would be lost, duplicated, or broken by convergence. For whole-repository consolidation claims, account for the relevant corpus and state any areas not inspected.

For each material candidate classify:
- adopt directly;
- merge;
- adapt/modernize;
- refactor before adoption;
- supersede;
- preserve as knowledge only;
- archive;
- discard.

Record evidence, technical rationale, user/business value, dependencies, compatibility implications, risks, effort, expected benefit, and validation method.

Before migration, explicitly identify feature/capability gaps between source and target and capture business rules, domain expertise, operational procedures, conventions, workarounds, lessons learned, and historical decisions that would otherwise disappear.

Sequence the migration using dependency-aware port/refactor/integration order, compatibility windows where needed, validation gates, rollback/recovery strategy, and final removal criteria for superseded paths.

Preserve valuable behavior and knowledge without preserving accidental complexity.
</consolidation_profile>
