# Profile: Performance & Scalability

Activate when performance is an explicit requirement, a measured problem, or a material operational constraint.

<performance_profile>
Use the sequence:
1. measure;
2. profile;
3. form a falsifiable hypothesis;
4. optimize the binding bottleneck;
5. remeasure and regression-test.

Investigate algorithmic complexity, repeated scans/calls, N+1 queries, blocking I/O, contention, serialization/copying, allocation pressure, batching, cache behavior, queue pressure, startup/build/test time, and capacity ceilings.

Do not add complexity for hypothetical speed. Qualify performance claims that are not measured.
</performance_profile>
