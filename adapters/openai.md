# Adapter: OpenAI

<adapter>
Use this protocol as high-level instructions when the host supports instruction/input separation. Keep dynamic task data in the final `<task>` block rather than mixing it into the protocol. Use tools to verify mutable facts and report tool-backed results without claiming unexecuted actions.
</adapter>
