# Release process

This document is the durable release procedure. Per-release verification output belongs in the release artifact or hosting platform, not as a stale checked-in `RELEASE.md` snapshot.

## 1. Choose the version

Update the same SemVer value in:

- `pyproject.toml`
- `manifest.json`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `CHANGELOG.md`

The repository test suite checks version agreement.

## 2. Clean generated state

```bash
make clean
```

Confirm no committed-source candidate includes:

- `build/`
- `dist/`
- `wheelhouse/`
- `.pytest_cache/`
- `__pycache__/`
- `.prove-it/`
- compiled example prompts
- generated package-resource mirrors

## 3. Run deterministic gates

```bash
python -m pip install -e '.[dev,mcp]'
make check
pytest -q
```

The second pytest invocation ensures the optional MCP SDK integration test is exercised when the dependency is installed.

If the environment cannot install the optional MCP dependency, record that limitation explicitly and do not claim the SDK integration test ran.

## 4. Validate plugin packaging

When Claude Code is available, run its plugin validator against the repository.

Confirm:

- `.claude-plugin/plugin.json` parses;
- `skills/prove-it/SKILL.md` and support files are discoverable;
- no unrelated root `agents/`, `hooks/`, or other plugin component directory exists accidentally;
- `.mcp.json.example` is documentation only unless the release intentionally auto-registers an MCP server.

## 5. Build and smoke-test the wheel

```bash
make wheel
```

Install the wheel into a clean temporary directory or environment. From outside the repository checkout verify at minimum:

```bash
prove-it list
prove-it eval
prove-it mcp-config
prove-it-proof --help
```

If `mcp` is installed, also verify:

```bash
prove-it-mcp
```

through an MCP client/inspector rather than by expecting terminal output from stdio.

## 6. Generate optional artifacts

```bash
make dist
```

The standalone master prompt is written to `build/generated/PROVE_IT_MASTER_PROMPT.md`. It is a release artifact, not canonical source.

## 7. Package source releases

Build clean `.zip` and `.tar.gz` archives from the verified source tree. Generate SHA-256 checksums.

Keep the installable Agent Skill as a separate `skill.zip` containing `skills/prove-it/` only.

## 8. Record evidence

The release note should state only checks that actually ran. Include:

- test counts;
- static eval counts;
- optional MCP integration status;
- wheel smoke result;
- plugin validation status;
- known limitations.

## 9. Tag and publish

Tag the verified commit with the release version only after the archive contents and version metadata agree.
