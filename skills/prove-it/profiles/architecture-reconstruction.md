# Profile: Architecture Reconstruction

Activate for architecture analysis, architecture maps, system cartography, knowledge graphs, or machine-readable system models.

<architecture_profile>
Perform as needed:
1. **Topology discovery** — applications, services, packages, entrypoints, infrastructure, persistence, major boundaries.
2. **Runtime tracing** — route registration, calls, dependency injection, HTTP/RPC, events/queues, persistence, configuration, integrations.
3. **End-to-end flows** — trace important real journeys from true entrypoint to logical completion.
4. **Evidence reconciliation** — important nodes, edges, flows, and claims require source evidence.
5. **Architectural abstraction** — merge low-level details into meaningful components without erasing important boundaries.
6. **Consistency validation** — every representation must describe the same canonical system.

Preserve relationship semantics instead of generic `depends_on` edges: static dependency, control flow, data flow, persistence, messaging, deployment, trust, external integration, and operational relationship.

For important boundaries, capture protocol/mechanism, payload/type, direction, validation/auth boundary, persistence implications, and synchronous/asynchronous behavior where evidence supports them.

<canonical_model>
When multiple artifacts represent the architecture, build one canonical model first and derive all artifacts from it. Validate IDs, edge endpoints, flow references/order, evidence, and semantics across artifacts.
</canonical_model>

Do not invent architecture to make a visualization prettier.
</architecture_profile>
