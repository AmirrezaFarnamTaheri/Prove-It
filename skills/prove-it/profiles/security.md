# Profile: Security & Trust Boundaries

Activate when the task involves untrusted input, authentication, authorization, secrets, files, external integrations, privileged operations, or sensitive data.

<security_profile>
Treat trust boundaries as hostile. Apply as appropriate:
- explicit schema/input validation and allow-list parsing;
- safe deserialization and bounded payload sizes;
- authorization checks at the actual resource/action boundary;
- least privilege and secure defaults;
- secret isolation and sensitive-log redaction;
- safe file/path/command handling;
- timeouts, rate/resource limits, and deterministic rejection paths;
- dependency and supply-chain hygiene.

Investigate concrete attack paths rather than inventing hypothetical vulnerabilities. Tie security findings to real code/configuration paths or clearly label them as inferred/unknown.

Never expose discovered secret values in output.
</security_profile>
