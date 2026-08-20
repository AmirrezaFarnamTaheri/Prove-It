from __future__ import annotations

import hashlib
import os
import shlex
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Iterable

from ._proof_state import (
    AGENT_REPORTED,
    CRITERION_STATES,
    DEFAULT_CHECK_COMMANDS,
    EVIDENCE_RELATIONS,
    EVIDENCE_STRENGTHS,
    MAX_OUTPUT_CHARS,
    READ_ONLY_GIT_SUBCOMMANDS,
    SERVER_OBSERVED,
    SCHEMA_VERSION,
    _STATE_LOCK,
    ProofError,
    ProofPaths,
    _atomic_write,
    _criterion,
    _criterion_by_id,
    _ensure_criterion_ids,
    _hash_file,
    _next_evidence_id,
    _state_mutation,
    _workspace_file,
    capture_source_state,
    load_ledger,
    proof_paths,
    save_ledger,
    utc_now,
    workspace_fingerprint,
)

def start_proof(
    task: str,
    acceptance_criteria: Iterable[str],
    *,
    workspace: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    with _STATE_LOCK:
        return _start_proof_locked(task, acceptance_criteria, workspace=workspace, overwrite=overwrite)


def _start_proof_locked(task: str, acceptance_criteria: Iterable[str], *, workspace: str | Path | None = None, overwrite: bool = False) -> dict[str, Any]:
    task = task.strip()
    if not task:
        raise ProofError("Task must be non-empty.")
    raw_criteria = [acceptance_criteria] if isinstance(acceptance_criteria, str) else list(acceptance_criteria)
    if not all(isinstance(item, str) for item in raw_criteria):
        raise ProofError("Acceptance criteria must be strings.")
    criteria_values = [item.strip() for item in raw_criteria if item.strip()]
    if not criteria_values:
        raise ProofError("At least one acceptance criterion is required.")
    if len(set(criteria_values)) != len(criteria_values):
        raise ProofError("Acceptance criteria must be unique within a proof session.")
    paths = proof_paths(workspace)
    if paths.ledger.exists() and not overwrite:
        raise ProofError(f"Proof session already exists: {paths.ledger}. Pass overwrite=true to replace it.")
    now = utc_now()
    ledger = {
        "schema_version": SCHEMA_VERSION,
        "session_id": str(uuid.uuid4()),
        "task": task,
        "workspace": str(paths.workspace),
        "created_at": now,
        "updated_at": now,
        "source_state": capture_source_state(paths.workspace, paths.state_dir),
        "criteria": [_criterion(i, value) for i, value in enumerate(criteria_values, start=1)],
        "evidence": [],
    }
    save_ledger(ledger, paths)
    return summarize(ledger, paths)


def _append_evidence(ledger: dict[str, Any], evidence: dict[str, Any], paths: ProofPaths) -> dict[str, Any]:
    ledger["evidence"].append(evidence)
    for criterion_id in evidence["criterion_ids"]:
        criterion = _criterion_by_id(ledger, criterion_id)
        if evidence["id"] not in criterion["evidence_ids"]:
            criterion["evidence_ids"].append(evidence["id"])
    save_ledger(ledger, paths)
    return evidence


@_state_mutation
def record_source(
    criterion_ids: Iterable[str],
    path: str,
    summary: str,
    *,
    workspace: str | Path | None = None,
    line_start: int | None = None,
    line_end: int | None = None,
    expected_text: str | None = None,
    relation: str = "supports",
) -> dict[str, Any]:
    if relation not in EVIDENCE_RELATIONS:
        raise ProofError(f"Invalid evidence relation: {relation}")
    if not summary.strip():
        raise ProofError("Evidence summary must be non-empty.")
    ledger, paths = load_ledger(workspace)
    ids = _ensure_criterion_ids(ledger, criterion_ids)
    source = _workspace_file(paths, path)
    if not source.is_file():
        raise ProofError(f"Source file not found: {source}")
    if (line_start is None) ^ (line_end is None):
        raise ProofError("line_start and line_end must be provided together.")
    excerpt = None
    if line_start is not None and line_end is not None:
        if line_start < 1 or line_end < line_start:
            raise ProofError("Invalid line range.")
        lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
        if line_end > len(lines):
            raise ProofError(f"Line range exceeds file length ({len(lines)} lines).")
        excerpt = "\n".join(lines[line_start - 1:line_end])
        if expected_text is not None and expected_text not in excerpt:
            raise ProofError("expected_text was not found in the verified line range.")
    elif expected_text is not None:
        text = source.read_text(encoding="utf-8", errors="replace")
        if expected_text not in text:
            raise ProofError("expected_text was not found in the verified source file.")
    evidence = {
        "id": _next_evidence_id(ledger),
        "criterion_ids": ids,
        "kind": "source",
        "relation": relation,
        "strength": "verified",
        "provenance": SERVER_OBSERVED,
        "summary": summary.strip(),
        "observed_at": utc_now(),
        "path": str(source.relative_to(paths.workspace)),
        "line_start": line_start,
        "line_end": line_end,
        "sha256": _hash_file(source),
        "excerpt": excerpt,
    }
    return _append_evidence(ledger, evidence, paths)


@_state_mutation
def record_evidence(
    criterion_ids: Iterable[str],
    kind: str,
    summary: str,
    *,
    workspace: str | Path | None = None,
    relation: str = "supports",
    strength: str = "strongly_inferred",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if relation not in EVIDENCE_RELATIONS:
        raise ProofError(f"Invalid evidence relation: {relation}")
    if strength not in EVIDENCE_STRENGTHS:
        raise ProofError(f"Invalid evidence strength: {strength}")
    if not summary.strip():
        raise ProofError("Evidence summary must be non-empty.")
    ledger, paths = load_ledger(workspace)
    ids = _ensure_criterion_ids(ledger, criterion_ids)
    evidence = {
        "id": _next_evidence_id(ledger),
        "criterion_ids": ids,
        "kind": kind.strip() or "observation",
        "relation": relation,
        "strength": strength,
        "provenance": AGENT_REPORTED,
        "summary": summary.strip(),
        "observed_at": utc_now(),
        "details": details or {},
    }
    return _append_evidence(ledger, evidence, paths)


def _allowed_commands() -> set[str]:
    raw = os.environ.get("PROVE_IT_ALLOWED_CHECKS")
    if not raw:
        return set(DEFAULT_CHECK_COMMANDS)
    return {part.strip() for part in raw.split(",") if part.strip()}


def _validate_check(argv: list[str], paths: ProofPaths, cwd: str | None) -> tuple[list[str], Path]:
    if not argv or not all(isinstance(part, str) and part for part in argv):
        raise ProofError("argv must be a non-empty list of strings.")
    raw_command = argv[0]
    command = Path(raw_command).name
    if command not in _allowed_commands():
        allowed = ", ".join(sorted(_allowed_commands()))
        raise ProofError(f"Verification command '{command}' is not allowed. Allowed: {allowed}")

    check_cwd = _workspace_file(paths, cwd or ".")
    if not check_cwd.is_dir():
        raise ProofError(f"Verification cwd is not a directory: {check_cwd}")

    has_separator = any(sep and sep in raw_command for sep in (os.sep, os.altsep))
    if has_separator or Path(raw_command).is_absolute():
        executable = _workspace_file(paths, raw_command if Path(raw_command).is_absolute() else check_cwd / raw_command)
        if not executable.is_file():
            raise ProofError(f"Verification executable not found: {executable}")
        if command != "gradlew":
            path_executable = shutil.which(command)
            if not path_executable or Path(path_executable).resolve() != executable:
                raise ProofError(
                    f"Verification executable path is not the PATH-resolved '{command}': {executable}"
                )
        resolved_argv = [str(executable), *argv[1:]]
    else:
        executable = shutil.which(raw_command)
        if not executable:
            raise ProofError(f"Verification command not found on PATH: {raw_command}")
        resolved_argv = [executable, *argv[1:]]

    if command == "git":
        if len(argv) < 2 or argv[1] not in READ_ONLY_GIT_SUBCOMMANDS:
            allowed_git = ", ".join(sorted(READ_ONLY_GIT_SUBCOMMANDS))
            raise ProofError(f"Only read-only git checks are allowed: {allowed_git}")
    return resolved_argv, check_cwd


@_state_mutation
def run_check(
    criterion_ids: Iterable[str],
    argv: list[str],
    summary: str,
    *,
    workspace: str | Path | None = None,
    cwd: str | None = None,
    timeout_seconds: int = 120,
    kind: str = "check",
) -> dict[str, Any]:
    if not summary.strip():
        raise ProofError("Verification summary must be non-empty.")
    ledger, paths = load_ledger(workspace)
    ids = _ensure_criterion_ids(ledger, criterion_ids)
    argv, check_cwd = _validate_check(argv, paths, cwd)
    timeout_seconds = max(1, min(int(timeout_seconds), 1800))
    started = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            argv,
            cwd=check_cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            env=os.environ.copy(),
        )
        exit_code = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
    except OSError as exc:
        raise ProofError(f"Could not execute verification command: {exc}") from exc
    duration_ms = int((time.monotonic() - started) * 1000)
    combined = f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    output_hash = hashlib.sha256(combined.encode("utf-8", errors="replace")).hexdigest()
    excerpt = combined[-MAX_OUTPUT_CHARS:]
    relation = "supports" if exit_code == 0 and not timed_out else "contradicts"
    evidence = {
        "id": _next_evidence_id(ledger),
        "criterion_ids": ids,
        "kind": kind.strip() or "check",
        "relation": relation,
        "strength": "verified",
        "provenance": SERVER_OBSERVED,
        "summary": summary.strip(),
        "observed_at": utc_now(),
        "command": shlex.join(argv),
        "argv": argv,
        "cwd": str(check_cwd.relative_to(paths.workspace)),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
        "output_sha256": output_hash,
        "output_excerpt": excerpt,
        "workspace_fingerprint": workspace_fingerprint(
            paths.workspace,
            exclude_paths=[paths.state_dir],
        ),
    }
    _append_evidence(ledger, evidence, paths)
    return evidence


@_state_mutation
def set_criterion_state(
    criterion_id: str,
    state: str,
    reason: str,
    *,
    workspace: str | Path | None = None,
) -> dict[str, Any]:
    if state not in {"blocked", "waived", "pending"}:
        raise ProofError("Only blocked, waived, or pending may be set manually; proof states are evidence-derived.")
    ledger, paths = load_ledger(workspace)
    criterion = _criterion_by_id(ledger, criterion_id)
    if state in {"blocked", "waived"} and not reason.strip():
        raise ProofError(f"A non-empty reason is required when marking a criterion {state}.")
    criterion["override_state"] = None if state == "pending" else state
    criterion["override_reason"] = None if state == "pending" else reason.strip()
    save_ledger(ledger, paths)
    return {
        "criterion_id": criterion_id,
        "status": criterion_status(ledger, criterion, paths),
        "reason": criterion["override_reason"],
    }


def _evidence_map(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in ledger["evidence"]}


def _criterion_evidence(ledger: dict[str, Any], criterion: dict[str, Any]) -> list[dict[str, Any]]:
    evidence_by_id = _evidence_map(ledger)
    return [
        evidence_by_id[evidence_id]
        for evidence_id in criterion.get("evidence_ids", [])
        if evidence_id in evidence_by_id
    ]


def evidence_freshness(item: dict[str, Any], paths: ProofPaths) -> str:
    """Return fresh, stale, unknown, or not_applicable for an evidence item."""
    if item.get("provenance") != SERVER_OBSERVED:
        return "not_applicable"
    if item.get("kind") == "source" and item.get("path") and item.get("sha256"):
        try:
            source = _workspace_file(paths, item["path"])
        except ProofError:
            return "stale"
        if not source.is_file():
            return "stale"
        try:
            return "fresh" if _hash_file(source) == item["sha256"] else "stale"
        except OSError:
            return "unknown"
    recorded_fingerprint = item.get("workspace_fingerprint")
    if recorded_fingerprint:
        current = workspace_fingerprint(paths.workspace, exclude_paths=[paths.state_dir])
        if current is None:
            return "unknown"
        return "fresh" if current == recorded_fingerprint else "stale"
    return "unknown"


def criterion_status(
    ledger: dict[str, Any], criterion: dict[str, Any], paths: ProofPaths | None = None
) -> str:
    override = criterion.get("override_state")
    if override in {"blocked", "waived"}:
        return override
    evidence = _criterion_evidence(ledger, criterion)
    if paths is not None:
        evidence = [item for item in evidence if evidence_freshness(item, paths) != "stale"]
    observed_contradiction = any(
        item.get("provenance") == SERVER_OBSERVED and item.get("relation") == "contradicts" for item in evidence
    )
    if observed_contradiction:
        return "contradicted"
    observed_support = any(
        item.get("provenance") == SERVER_OBSERVED
        and item.get("relation") == "supports"
        and item.get("strength") == "verified"
        for item in evidence
    )
    if observed_support:
        return "verified"
    reported_support = any(item.get("relation") == "supports" for item in evidence)
    return "partial" if reported_support else "pending"


def summarize(ledger: dict[str, Any], paths: ProofPaths | None = None) -> dict[str, Any]:
    criteria: list[dict[str, Any]] = []
    for item in ledger["criteria"]:
        item_evidence = _criterion_evidence(ledger, item)
        stale_count = 0
        if paths is not None:
            stale_count = sum(evidence_freshness(evidence, paths) == "stale" for evidence in item_evidence)
        criteria.append(
            {
                "id": item["id"],
                "statement": item["statement"],
                "status": criterion_status(ledger, item, paths),
                "evidence_count": len(item_evidence),
                "stale_evidence_count": stale_count,
                "reason": item.get("override_reason"),
            }
        )
    counts = {state: 0 for state in CRITERION_STATES}
    for item in criteria:
        counts[item["status"]] += 1
    if counts["contradicted"]:
        readiness = "NOT_READY"
    elif criteria and counts["verified"] + counts["waived"] == len(criteria) and counts["verified"] > 0:
        readiness = "READY"
    else:
        readiness = "CONDITIONAL"
    result = {
        "session_id": ledger["session_id"],
        "task": ledger["task"],
        "workspace": ledger["workspace"],
        "source_state": ledger["source_state"],
        "readiness": readiness,
        "counts": counts,
        "criteria": criteria,
        "evidence_count": len(ledger["evidence"]),
        "updated_at": ledger["updated_at"],
    }
    if paths is not None:
        result["source_state_current"] = capture_source_state(paths.workspace, paths.state_dir)
        freshness = {"fresh": 0, "stale": 0, "unknown": 0, "not_applicable": 0}
        for item in ledger["evidence"]:
            freshness[evidence_freshness(item, paths)] += 1
        result["evidence_freshness"] = freshness
    return result


def status(*, workspace: str | Path | None = None) -> dict[str, Any]:
    ledger, paths = load_ledger(workspace)
    return summarize(ledger, paths)


def _render_markdown(ledger: dict[str, Any], summary: dict[str, Any]) -> str:
    source = summary["source_state"]
    current_source = summary.get("source_state_current", source)
    lines = [
        "# Prove It Proof Report",
        "",
        f"**Readiness:** {summary['readiness']}",
        f"**Task:** {summary['task']}",
        f"**Session:** `{summary['session_id']}`",
        f"**Workspace:** `{summary['workspace']}`",
        "",
        "## Source State",
        "",
        "### At proof start",
        "",
    ]
    if source.get("kind") == "git":
        lines.extend([
            f"- Commit: `{source.get('commit') or 'unknown'}`",
            f"- Branch: `{source.get('branch') or 'detached/unknown'}`",
            f"- Dirty at capture: `{source.get('dirty')}`",
            f"- Captured: `{source.get('captured_at')}`",
        ])
    else:
        lines.extend(["- Git repository: no", f"- Captured: `{source.get('captured_at')}`"])
    lines.extend(["", "### At report time", ""])
    if current_source.get("kind") == "git":
        lines.extend([
            f"- Commit: `{current_source.get('commit') or 'unknown'}`",
            f"- Branch: `{current_source.get('branch') or 'detached/unknown'}`",
            f"- Dirty: `{current_source.get('dirty')}`",
            f"- Captured: `{current_source.get('captured_at')}`",
        ])
    else:
        lines.extend(["- Git repository: no", f"- Captured: `{current_source.get('captured_at')}`"])
    lines.extend(["", "## Acceptance Criteria", ""])
    evidence_by_id = _evidence_map(ledger)
    for criterion in ledger["criteria"]:
        current = criterion_status(ledger, criterion, proof_paths(summary["workspace"]))
        lines.append(f"### {criterion['id']} — {current.upper()}")
        lines.append(criterion["statement"])
        if criterion.get("override_reason"):
            lines.append(f"\nReason: {criterion['override_reason']}")
        evidence_ids = criterion.get("evidence_ids", [])
        if evidence_ids:
            lines.append("\nEvidence:")
            for evidence_id in evidence_ids:
                item = evidence_by_id.get(evidence_id)
                if not item:
                    continue
                suffix = ""
                if item.get("path"):
                    suffix += f" — `{item['path']}`"
                    if item.get("line_start"):
                        suffix += f":L{item['line_start']}-L{item['line_end']}"
                if item.get("command"):
                    suffix += f" — `{item['command']}` → exit `{item['exit_code']}`"
                freshness = evidence_freshness(item, proof_paths(summary["workspace"]))
                if freshness != "not_applicable":
                    suffix += f" — freshness `{freshness}`"
                lines.append(
                    f"- `{item['id']}` {item['relation']} / {item['provenance']} / {item['strength']}: "
                    f"{item['summary']}{suffix}"
                )
        else:
            lines.append("\nEvidence: none")
        lines.append("")
    lines.extend([
        "## Summary",
        "",
        f"- Verified: {summary['counts']['verified']}",
        f"- Partial: {summary['counts']['partial']}",
        f"- Pending: {summary['counts']['pending']}",
        f"- Blocked: {summary['counts']['blocked']}",
        f"- Waived: {summary['counts']['waived']}",
        f"- Contradicted: {summary['counts']['contradicted']}",
        f"- Evidence items: {summary['evidence_count']}",
        f"- Stale evidence: {summary.get('evidence_freshness', {}).get('stale', 0)}",
        "",
        "> A READY result means the ledger contains server-observed supporting evidence for every non-waived criterion and no server-observed contradiction. It does not prove claims outside the recorded acceptance criteria.",
        "",
    ])
    return "\n".join(lines)


def report(*, workspace: str | Path | None = None, write_markdown: bool = True) -> dict[str, Any]:
    ledger, paths = load_ledger(workspace)
    summary = summarize(ledger, paths)
    markdown = _render_markdown(ledger, summary)
    if write_markdown:
        _atomic_write(paths.report, markdown)
    return {
        **summary,
        "proof_file": str(paths.ledger),
        "report_file": str(paths.report) if write_markdown else None,
        "markdown": markdown,
        "evidence": [
            {**item, "freshness": evidence_freshness(item, paths)} for item in ledger["evidence"]
        ],
    }
