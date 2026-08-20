# Profile: Concurrency & Runtime Lifecycle

Activate for asynchronous, concurrent, local-system, daemon, worker, queue, or high-throughput behavior.

<concurrency_profile>
Every worker/task/process/queue should have appropriate:
- ownership;
- bounded lifecycle;
- cancellation and shutdown behavior;
- failure reporting;
- resource limits;
- backpressure where needed.

Protect against orphaned work, runaway retries, unbounded queues, starvation, deadlocks, races, leaked resources, and unsafe shutdown.

Prefer ordinary synchronization and simple process boundaries before exotic lock-free or multi-process designs. Use zero-copy, lock-free structures, daemon/client splits, and specialized IPC only when requirements or measurements justify them.
</concurrency_profile>
