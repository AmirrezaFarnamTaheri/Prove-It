# References

These sources inform Prove It's host integration, prompt architecture, and MCP packaging choices. They are design references, not runtime dependencies, and no provider endorsement is implied.

Last reviewed: 2026-08-19.

## OpenAI

- Prompt engineering: https://developers.openai.com/api/docs/guides/prompt-engineering
- Codex use cases (including reusable Skills workflows): https://developers.openai.com/codex/use-cases
- Skills API reference: https://developers.openai.com/api/reference/go/resources/skills

Applied principles:

- keep high-level behavior separate from task-specific input;
- make instructions and output contracts explicit;
- package reusable workflows as Skills rather than repeating large prompts manually;
- keep plugin capabilities composable rather than forcing every capability into one always-on instruction block.

## Anthropic / Claude Code

- Claude Code plugins: https://code.claude.com/docs/en/plugins
- Claude Code plugin reference: https://code.claude.com/docs/en/plugins-reference
- Prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Applied principles:

- keep the plugin manifest under `.claude-plugin/`;
- keep plugin components such as `skills/` and `.mcp.json` at plugin root;
- use clear, direct, structured instructions;
- keep optional machinery optional so the skill remains useful without the MCP runtime.

## Google

- Gemini prompt design strategies: https://ai.google.dev/gemini-api/docs/prompting-strategies

Applied principles:

- make instructions specific;
- separate context from requested behavior;
- constrain output when deterministic structure matters.

## Model Context Protocol

- MCP specification: https://modelcontextprotocol.io/specification/2026-07-28
- Official MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Python SDK documentation: https://py.sdk.modelcontextprotocol.io/

Applied principles:

- use local stdio for the optional proof server;
- expose narrowly scoped proof tools rather than duplicating general filesystem/shell capabilities;
- keep tool inputs explicit and structured;
- keep the proof engine useful independently of any single host.

The Python integration targets the stable MCP Python SDK v2 API line with `mcp>=2,<3`.

## Maintenance rule

Provider behavior changes over time. Keep adapters and packaging metadata small, verify them periodically, and change the core engineering protocol only when product evidence or evaluation results justify the change.
