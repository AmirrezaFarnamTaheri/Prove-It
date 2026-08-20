from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import prove_it


ROOT = Path(__file__).resolve().parents[1]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_versions_are_synchronized() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    expected = pyproject["project"]["version"]
    assert _json("manifest.json")["version"] == expected
    assert _json(".claude-plugin/plugin.json")["version"] == expected
    marketplace = _json(".claude-plugin/marketplace.json")
    assert marketplace["plugins"][0]["version"] == expected
    assert prove_it.__version__ == expected
    assert f"## [{expected}]" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")


def test_plugin_and_skill_layout_is_canonical() -> None:
    assert (ROOT / "skills/prove-it/SKILL.md").is_file()
    assert (ROOT / "skills/prove-it/agents/openai.yaml").is_file()
    assert not (ROOT / "SKILL.md").exists()
    assert not (ROOT / ".claude").exists()
    assert not (ROOT / "agents").exists()
    assert not (ROOT / "src/prove_it/resources").exists()
    assert not (ROOT / "dist").exists()
    assert not list(ROOT.glob("examples/**/compiled-prompt.md"))
    assert len((ROOT / "skills/prove-it/SKILL.md").read_text(encoding="utf-8").splitlines()) < 500


def test_mcp_example_is_valid_json() -> None:
    config = _json(".mcp.json.example")
    assert config["mcpServers"]["prove-it"]["command"] == "prove-it-mcp"


def test_relative_markdown_links_resolve() -> None:
    markdown_files = [
        ROOT / "README.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "DESIGN.md",
        ROOT / "SECURITY.md",
        *sorted((ROOT / "docs").glob("*.md")),
        *sorted((ROOT / "evals").glob("*.md")),
        *sorted((ROOT / "examples").glob("**/*.md")),
        *sorted((ROOT / "skills/prove-it").glob("**/*.md")),
    ]
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    missing: list[str] = []
    for document in markdown_files:
        text = document.read_text(encoding="utf-8")
        for raw_target in pattern.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith(("mailto:", "#", "<")):
                continue
            candidate = (document.parent / target).resolve()
            if not candidate.exists():
                missing.append(f"{document.relative_to(ROOT)} -> {raw_target}")
    assert missing == []
