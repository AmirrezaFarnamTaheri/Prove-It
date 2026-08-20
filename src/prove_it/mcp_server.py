from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from . import proof_engine


def _server():
    try:
        from mcp.server import MCPServer
    except ImportError as exc:  # pragma: no cover - exercised only when dependency is missing
        raise RuntimeError(
            "The Prove It MCP server requires the official MCP Python SDK v2. "
            "Install with: pip install 'prove-it-protocol[mcp]'"
        ) from exc

    mcp = MCPServer(
        "Prove It",
        instructions=(
            "Use these tools only to establish and report evidence for engineering completion claims. "
            "Use host-native tools for ordinary file editing, browsing, git, and shell work. "
            "For consequential tasks, start a proof session, attach server-observed evidence where possible, "
            "and call proveit.report before claiming completion."
        ),
    )

    @mcp.tool(name="proveit.start")
    def start(
        task: str,
        acceptance_criteria: list[str],
        workspace: str | None = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Start a proof session, capture source state, and define acceptance criteria."""
        return proof_engine.start_proof(task, acceptance_criteria, workspace=workspace, overwrite=overwrite)

    @mcp.tool(name="proveit.add_criterion")
    def add_criterion(statement: str, criterion_id: str | None = None, workspace: str | None = None) -> dict[str, Any]:
        """Add one acceptance criterion to the current proof session."""
        return proof_engine.add_criterion(statement, workspace=workspace, criterion_id=criterion_id)

    @mcp.tool(name="proveit.record_source")
    def record_source(
        criterion_ids: list[str],
        path: str,
        summary: str,
        workspace: str | None = None,
        line_start: int | None = None,
        line_end: int | None = None,
        expected_text: str | None = None,
        relation: str = "supports",
    ) -> dict[str, Any]:
        """Verify a workspace source file/line range and attach server-observed evidence."""
        return proof_engine.record_source(
            criterion_ids,
            path,
            summary,
            workspace=workspace,
            line_start=line_start,
            line_end=line_end,
            expected_text=expected_text,
            relation=relation,
        )

    @mcp.tool(name="proveit.record_evidence")
    def record_evidence(
        criterion_ids: list[str],
        kind: str,
        summary: str,
        workspace: str | None = None,
        relation: str = "supports",
        strength: str = "strongly_inferred",
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Record host/agent-observed evidence; this remains explicitly agent-reported."""
        return proof_engine.record_evidence(
            criterion_ids,
            kind,
            summary,
            workspace=workspace,
            relation=relation,
            strength=strength,
            details=details,
        )

    @mcp.tool(name="proveit.run_check")
    def run_check(
        criterion_ids: list[str],
        argv: list[str],
        summary: str,
        workspace: str | None = None,
        cwd: str | None = None,
        timeout_seconds: int = 120,
        kind: str = "check",
    ) -> dict[str, Any]:
        """Run one bounded allowlisted verification command without a shell and record server-observed evidence."""
        return proof_engine.run_check(
            criterion_ids,
            argv,
            summary,
            workspace=workspace,
            cwd=cwd,
            timeout_seconds=timeout_seconds,
            kind=kind,
        )

    @mcp.tool(name="proveit.set_criterion_state")
    def set_criterion_state(
        criterion_id: str,
        state: str,
        reason: str,
        workspace: str | None = None,
    ) -> dict[str, Any]:
        """Mark a criterion blocked/waived, or clear the override with pending. Verified states stay evidence-derived."""
        return proof_engine.set_criterion_state(criterion_id, state, reason, workspace=workspace)

    @mcp.tool(name="proveit.status")
    def status(workspace: str | None = None) -> dict[str, Any]:
        """Return deterministic criterion states and overall readiness."""
        return proof_engine.status(workspace=workspace)

    @mcp.tool(name="proveit.report")
    def report(workspace: str | None = None, write_markdown: bool = True) -> dict[str, Any]:
        """Generate the complete proof report and optionally persist .prove-it/PROOF.md."""
        return proof_engine.report(workspace=workspace, write_markdown=write_markdown)

    @mcp.resource("proveit://proof/current")
    def current_proof() -> str:
        """Current proof ledger as JSON."""
        ledger, _ = proof_engine.load_ledger()
        return json.dumps(ledger, indent=2)

    @mcp.resource("proveit://proof/report")
    def current_report() -> str:
        """Current rendered proof report."""
        return proof_engine.report(write_markdown=False)["markdown"]

    return mcp


def main() -> None:
    try:
        server = _server()
    except RuntimeError as exc:  # pragma: no cover - depends on optional install state
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    server.run()


if __name__ == "__main__":
    main()
