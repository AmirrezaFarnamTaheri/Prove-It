# Profile: Stateful Systems

Activate for materially complex state machines, workflows, long-lived sessions, or persisted lifecycle state.

<state_profile>
Define as needed:
- states;
- events/inputs;
- allowed transitions;
- invalid transitions;
- invariants;
- recovery states;
- terminal states;
- persistence semantics;
- observability.

Use finite state machines, reducers, typed unions, or workflow engines only when they improve correctness and comprehension. Do not force formal state machinery onto trivial stateless components.
</state_profile>
