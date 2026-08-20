# Template: Production Implementation

<task_mode>production_implementation</task_mode>

<implementation_requirements>
- Establish current behavior and relevant repository conventions before changing code.
- Identify directly affected layers and integration points.
- Implement the requested behavior completely; do not stop at a local patch if other layers are required for real operation.
- Preserve unrelated behavior.
- Add or update regression protection that proves the requested behavior and important failure paths.
- Run the strongest practical verification available for the changed surface.
</implementation_requirements>

<implementation_output>
Lead with the implementation/artifacts. Summarize changed files, validation actually run, and any genuine remaining limitation.
</implementation_output>
