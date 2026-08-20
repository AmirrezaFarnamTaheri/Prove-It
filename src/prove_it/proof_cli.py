from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .proof_engine import ProofError, report, start_proof, status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prove-it-proof", description="Inspect Prove It proof state without an MCP host.")
    parser.add_argument("--workspace", help="Workspace containing .prove-it/proof.json")
    sub = parser.add_subparsers(dest="command", required=True)

    status_parser = sub.add_parser("status", help="Print proof readiness and criterion states")
    status_parser.add_argument("--json", action="store_true")

    report_parser = sub.add_parser("report", help="Generate .prove-it/PROOF.md")
    report_parser.add_argument("--json", action="store_true")

    start_parser = sub.add_parser("start", help="Start a proof session from a JSON task file")
    start_parser.add_argument("--task", required=True, help="JSON file with objective and acceptance_criteria")
    start_parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "start":
            data = json.loads(Path(args.task).read_text(encoding="utf-8"))
            criteria = data.get("acceptance_criteria") or []
            if isinstance(criteria, str):
                criteria = [criteria]
            if not isinstance(criteria, list) or not all(isinstance(item, str) for item in criteria):
                raise ValueError("acceptance_criteria must be a string or an array of strings")
            result = start_proof(
                str(data["objective"]),
                criteria,
                workspace=args.workspace,
                overwrite=args.overwrite,
            )
            print(json.dumps(result, indent=2))
            return 0
        if args.command == "status":
            result = status(workspace=args.workspace)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"{result['readiness']}: {result['counts']}")
                for criterion in result["criteria"]:
                    print(f"{criterion['id']:8} {criterion['status']:14} {criterion['statement']}")
            return 0
        result = report(workspace=args.workspace)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result["markdown"])
        return 0
    except (ProofError, KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
