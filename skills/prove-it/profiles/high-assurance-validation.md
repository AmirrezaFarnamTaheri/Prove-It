# Profile: High-Assurance Validation

Activate for correctness-critical, parser/protocol-heavy, security-sensitive, safety-sensitive, or high-cost failure domains.

<high_assurance_profile>
Selectively use stronger validation methods when they fit the risk model:
- property-based testing for invariant-rich behavior;
- fuzzing for parsers/protocols/untrusted inputs;
- differential/reference-oracle testing when a simple trusted implementation can exist;
- mutation testing to measure whether tests detect incorrect logic;
- fault injection or chaos testing for availability/recovery behavior.

Do not apply expensive techniques ceremonially. State what each validation method proves and what it does not prove.
</high_assurance_profile>
