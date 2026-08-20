from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class ProveItError(RuntimeError):
    """Raised for invalid repository configuration or composition input."""


@dataclass(frozen=True)
class Composition:
    text: str
    adapter: str
    template: str
    profiles: tuple[str, ...]


def default_repo_root() -> Path:
    """Find protocol resources in a checkout or an installed wheel."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "manifest.json").is_file():
            return parent
    cwd = Path.cwd()
    if (cwd / "manifest.json").is_file():
        return cwd
    packaged = here.parent / "resources"
    if (packaged / "manifest.json").is_file():
        return packaged
    raise ProveItError("Could not locate Prove It protocol resources; pass --root PATH.")


def load_manifest(root: Path) -> dict[str, Any]:
    path = root / "manifest.json"
    if not path.is_file():
        raise ProveItError(f"Manifest not found: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProveItError(f"Invalid manifest JSON: {exc}") from exc
    for key in ("core", "profiles", "templates", "adapters"):
        if key not in manifest:
            raise ProveItError(f"Manifest missing required key: {key}")
    return manifest


def read_fragment(root: Path, relative_path: str) -> str:
    path = (root / relative_path).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ProveItError(f"Fragment escapes repository root: {relative_path}") from exc
    if not path.is_file():
        raise ProveItError(f"Fragment not found: {relative_path}")
    return path.read_text(encoding="utf-8").strip()


def load_task(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ProveItError(f"Task file not found: {path}")
    try:
        task = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProveItError(f"Invalid task JSON: {exc}") from exc
    if not isinstance(task, dict):
        raise ProveItError("Task JSON must be an object.")
    objective = task.get("objective")
    if not isinstance(objective, str) or not objective.strip():
        raise ProveItError("Task must contain a non-empty string 'objective'.")
    allowed = {
        "objective",
        "target",
        "context",
        "deliverables",
        "constraints",
        "acceptance_criteria",
        "source_state",
        "notes",
    }
    extra = sorted(set(task) - allowed)
    if extra:
        raise ProveItError(f"Unsupported task fields: {', '.join(extra)}")
    for key in ("target", "source_state", "notes"):
        value = task.get(key)
        if value is not None and not isinstance(value, str):
            raise ProveItError(f"Task field '{key}' must be a string when provided.")
    for key in ("context", "deliverables", "constraints", "acceptance_criteria"):
        value = task.get(key)
        if value is None or isinstance(value, str):
            continue
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ProveItError(f"Task field '{key}' must be a string or an array of strings.")
    return task


def _render_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        if not value:
            return ""
        return "\n".join(f"- {item}" for item in value)
    return str(value).strip()


def render_task(task: dict[str, Any]) -> str:
    fields = [
        ("Objective", "objective"),
        ("Target", "target"),
        ("Context", "context"),
        ("Desired Deliverables", "deliverables"),
        ("Constraints / Boundaries", "constraints"),
        ("Acceptance Criteria", "acceptance_criteria"),
        ("Requested Source State", "source_state"),
        ("Notes", "notes"),
    ]
    sections: list[str] = ["<task>"]
    for title, key in fields:
        value = _render_value(task.get(key))
        if value:
            sections.extend((f"## {title}", value, ""))
    sections.append("</task>")
    return "\n".join(sections).strip()


def _resolve_named_entry(manifest: dict[str, Any], group: str, name: str) -> str:
    entries = manifest[group]
    if name not in entries:
        choices = ", ".join(sorted(entries))
        raise ProveItError(f"Unknown {group[:-1]} '{name}'. Available: {choices}")
    entry = entries[name]
    if not isinstance(entry, dict) or "path" not in entry:
        raise ProveItError(f"Invalid manifest entry: {group}.{name}")
    return str(entry["path"])


def compose(
    root: Path,
    task: dict[str, Any],
    *,
    template: str = "implementation",
    profiles: Iterable[str] = (),
    adapter: str = "generic",
) -> Composition:
    root = root.resolve()
    manifest = load_manifest(root)
    profile_names = tuple(dict.fromkeys(profiles))

    adapter_text = read_fragment(root, _resolve_named_entry(manifest, "adapters", adapter))
    core_text = read_fragment(root, str(manifest["core"]))
    template_text = read_fragment(root, _resolve_named_entry(manifest, "templates", template))
    profile_texts = [
        read_fragment(root, _resolve_named_entry(manifest, "profiles", name))
        for name in profile_names
    ]

    parts = [
        "<!-- Generated by Prove It. Canonical sources: manifest.json + protocols/profiles/templates/adapters. -->",
        adapter_text,
        core_text,
    ]
    if profile_texts:
        parts.append("# Activated Conditional Profiles")
        parts.extend(profile_texts)
    parts.extend((template_text, render_task(task)))
    text = "\n\n".join(part.strip() for part in parts if part.strip()) + "\n"
    return Composition(text=text, adapter=adapter, template=template, profiles=profile_names)


def validate_prompt(text: str, *, allow_placeholders: bool = False) -> list[str]:
    errors: list[str] = []
    required_markers = [
        "<role>",
        "<instruction_priority>",
        "<primary_directive>",
        "<evidence_model>",
        "<verification>",
        "<completion_gate>",
        "<task>",
        "</task>",
    ]
    for marker in required_markers:
        if marker not in text:
            errors.append(f"missing required marker: {marker}")
    if len(re.findall(r"(?m)^<task>\s*$", text)) != 1 or len(re.findall(r"(?m)^</task>\s*$", text)) != 1:
        errors.append("prompt must contain exactly one <task> block")
    if not allow_placeholders:
        for token in ("[INSERT", "[TASK_OR_GOAL]", "[PATH_OR_URL]"):
            if token in text:
                errors.append(f"unresolved placeholder: {token}")
    if "## Objective" not in text:
        errors.append("task block is missing an Objective section")
    return errors


def run_static_case(root: Path, case_path: Path) -> list[str]:
    case = json.loads(case_path.read_text(encoding="utf-8"))
    task = case["task"]
    composition = compose(
        root,
        task,
        template=case.get("template", "implementation"),
        profiles=case.get("profiles", []),
        adapter=case.get("adapter", "generic"),
    )
    errors = validate_prompt(composition.text)
    for needle in case.get("required_substrings", []):
        if needle not in composition.text:
            errors.append(f"missing expected substring: {needle}")
    for needle in case.get("forbidden_substrings", []):
        if needle in composition.text:
            errors.append(f"forbidden substring present: {needle}")
    return errors
