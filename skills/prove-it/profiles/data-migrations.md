# Profile: Data, Persistence & Migrations

Activate for persistent-state changes, schema evolution, storage changes, cache semantics, or data movement.

<data_profile>
Define:
- source of truth and ownership;
- schema and validation;
- read/write/update/delete semantics;
- migration and compatibility window;
- partial-failure behavior;
- rollback/recovery;
- cache invalidation where relevant;
- observability and verification.

Protect against schema drift, incompatible serialization, invalid defaults, precision loss, partial writes, corruption, stale caches, and divergent in-memory/persisted/displayed state.

Prefer reversible, staged migrations when practical. Verify migrations against realistic data paths rather than assuming compilation proves safety.
</data_profile>
