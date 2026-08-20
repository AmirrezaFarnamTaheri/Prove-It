# Prompt-engineering rationale

Prove It uses prompt-engineering techniques conservatively. The design goal is reliable engineering behavior, not maximal prompt complexity.

## Clear instruction hierarchy

The core protocol states precedence explicitly so generic Prove It defaults cannot override platform, user, project, or verified system constraints.

## Stable instructions vs dynamic task input

The composer keeps reusable protocol text separate from the final `<task>` block. This makes task input easier to inspect and reduces accidental mixing of instructions and dynamic context.

## Structured delimiters

XML-like tags provide semantic boundaries for complex prompts. They are organizational delimiters, not a demand that normal user-facing output be XML.

## Conditional depth

Specialist profiles activate only when relevant. This implements proportional rigor structurally instead of relying on a model to ignore large irrelevant instruction sections.

## Explicit acceptance criteria

The task schema and completion gate encourage observable success conditions. The optional proof engine makes those criteria durable and evidence-addressable.

## Evidence states

Prompt-level reasoning distinguishes verified, strongly inferred, assumed, and unknown. The MCP adds server-observed vs agent-reported provenance and current-vs-stale evidence.

## Tool use

The protocol tells agents to establish mutable facts with tools rather than memory when practical, while distinguishing actual tool observations from suggested checks.

Independent reads/searches/checks may be parallelized; dependent writes and synthesis remain ordered.

## Adversarial verification

For consequential conclusions, the agent is instructed to search for evidence that could falsify its current hypothesis. This is narrower and more useful than generic requests to "think harder".

## Output discipline

The requested artifact/result remains primary. Process narration and metadata are subordinate to the work itself.

## Evaluation over intuition

Static fixtures protect composition structure. Behavioral evaluation should compare outcomes under controlled tasks rather than reward prompts for sounding stricter or longer.

The framework should delete or weaken rules that do not improve measured behavior enough to justify their context and execution cost.
