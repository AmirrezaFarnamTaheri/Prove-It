from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .composer import (
    ProveItError,
    compose,
    default_repo_root,
    load_manifest,
    load_task,
    run_static_case,
    validate_prompt,
)


def _root(value: str | None) -> Path:
    return Path(value).resolve() if value else default_repo_root()


def cmd_list(args: argparse.Namespace) -> int:
    root = _root(args.root)
    manifest = load_manifest(root)
    print(f"{manifest.get('name', 'prove-it')} v{manifest.get('version', '?')}")
    for group in ("templates", "profiles", "adapters"):
        print(f"\n{group.title()}:")
        for name, meta in sorted(manifest[group].items()):
            print(f"  {name:28} {meta.get('description', '')}")
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    root = _root(args.root)
    task = load_task(Path(args.task))
    composition = compose(
        root,
        task,
        template=args.template,
        profiles=args.profile or [],
        adapter=args.adapter,
    )
    errors = validate_prompt(composition.text)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(composition.text, encoding="utf-8")
        print(f"Wrote {output}")
    else:
        sys.stdout.write(composition.text)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.prompt)
    if not path.is_file():
        print(f"ERROR: prompt not found: {path}", file=sys.stderr)
        return 2
    errors = validate_prompt(path.read_text(encoding="utf-8"), allow_placeholders=args.allow_placeholders)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {path}")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    root = _root(args.root)
    cases_dir = Path(args.cases) if args.cases else root / "evals" / "cases"
    case_paths = sorted(cases_dir.glob("*.json"))
    if not case_paths:
        print(f"ERROR: no eval cases found in {cases_dir}", file=sys.stderr)
        return 2
    failures = 0
    for case_path in case_paths:
        errors = run_static_case(root, case_path)
        if errors:
            failures += 1
            print(f"FAIL {case_path.name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {case_path.name}")
    print(f"\n{len(case_paths) - failures}/{len(case_paths)} static eval cases passed")
    return 1 if failures else 0


def cmd_mcp_config(args: argparse.Namespace) -> int:
    import json

    env = {}
    if args.workspace:
        env["PROVE_IT_WORKSPACE"] = str(Path(args.workspace).expanduser().resolve())
    config = {
        "mcpServers": {
            "prove-it": {
                "command": "prove-it-mcp",
                "args": [],
                "env": env,
            }
        }
    }
    print(json.dumps(config, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prove-it",
        description="Compose and statically validate Prove It prompts.",
    )
    parser.add_argument("--root", help="Repository root containing manifest.json")
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List templates, profiles, and adapters")
    list_parser.set_defaults(func=cmd_list)

    compose_parser = sub.add_parser("compose", help="Compose a task-specific prompt")
    compose_parser.add_argument("--task", required=True, help="Path to task JSON")
    compose_parser.add_argument("--template", default="implementation")
    compose_parser.add_argument("--profile", action="append", help="Profile to activate; repeatable")
    compose_parser.add_argument("--adapter", default="generic")
    compose_parser.add_argument("-o", "--output", help="Write composed prompt to this path")
    compose_parser.set_defaults(func=cmd_compose)

    validate_parser = sub.add_parser("validate", help="Validate a compiled prompt")
    validate_parser.add_argument("--prompt", required=True)
    validate_parser.add_argument("--allow-placeholders", action="store_true")
    validate_parser.set_defaults(func=cmd_validate)

    eval_parser = sub.add_parser("eval", help="Run static composition eval fixtures")
    eval_parser.add_argument("--cases", help="Directory containing eval case JSON files")
    eval_parser.set_defaults(func=cmd_eval)

    mcp_parser = sub.add_parser("mcp-config", help="Print a local stdio MCP configuration snippet")
    mcp_parser.add_argument("--workspace", help="Optional workspace to pin in PROVE_IT_WORKSPACE")
    mcp_parser.set_defaults(func=cmd_mcp_config)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ProveItError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
