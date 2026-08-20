from __future__ import annotations

import functools
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"
CRITERION_STATES = {"pending", "verified", "partial", "contradicted", "blocked", "waived"}
EVIDENCE_RELATIONS = {"supports", "contradicts", "context"}
EVIDENCE_STRENGTHS = {"verified", "strongly_inferred", "assumed", "unknown"}
AGENT_REPORTED = "agent-reported"
SERVER_OBSERVED = "server-observed"
DEFAULT_CHECK_COMMANDS = {
    "pytest", "python", "python3", "uv", "npm", "pnpm", "yarn", "bun",
    "cargo", "go", "dotnet", "make", "cmake", "ninja", "mvn", "gradle", "gradlew", "git",
}
READ_ONLY_GIT_SUBCOMMANDS = {"status", "diff", "rev-parse", "show", "log", "branch"}
MAX_OUTPUT_CHARS = 32_000
_STATE_LOCK = threading.RLock()
CRITERION_ID_RE = re.compile(r"^AC-(?:[A-Za-z0-9._-]+|[0-9]{2,})$")
EVIDENCE_ID_RE = re.compile(r"^EV-[0-9]{3,}$")


def _state_mutation(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        with _STATE_LOCK:
            return fn(*args, **kwargs)
    return wrapped


class ProofError(RuntimeError):
    """Raised when proof state or verification input is invalid."""


@dataclass(frozen=True)
class ProofPaths:
    workspace: Path
    state_dir: Path
    ledger: Path
    report: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _resolve_workspace(workspace: str | Path | None = None) -> Path:
    value = workspace or os.environ.get("PROVE_IT_WORKSPACE") or os.getcwd()
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise ProofError(f"Workspace is not a directory: {path}")
    return path


def proof_paths(workspace: str | Path | None = None) -> ProofPaths:
    root = _resolve_workspace(workspace)
    override = os.environ.get("PROVE_IT_STATE_DIR")
    state_dir = Path(override).expanduser().resolve() if override else root / ".prove-it"
    return ProofPaths(root, state_dir, state_dir / "proof.json", state_dir / "PROOF.md")


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.chmod(tmp_name, 0o600)
        except OSError:
            pass
        os.replace(tmp_name, path)
    finally:
        try:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        except OSError:
            pass


def _run_git(workspace: Path, args: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=workspace, capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return 127, ""
    return proc.returncode, proc.stdout.strip()


def capture_source_state(workspace: Path, state_dir: Path | None = None) -> dict[str, Any]:
    root_rc, root = _run_git(workspace, ["rev-parse", "--show-toplevel"])
    if root_rc != 0 or not root:
        return {
            "kind": "directory",
            "workspace": str(workspace),
            "captured_at": utc_now(),
            "git": False,
        }
    git_root = Path(root).resolve()
    _, commit = _run_git(git_root, ["rev-parse", "HEAD"])
    _, branch = _run_git(git_root, ["branch", "--show-current"])
    status_rc, status = _run_git(git_root, ["status", "--porcelain"])
    return {
        "kind": "git",
        "workspace": str(workspace),
        "git": True,
        "git_root": str(git_root),
        "commit": commit or None,
        "branch": branch or None,
        "dirty": bool(status) if status_rc == 0 else None,
        "fingerprint": workspace_fingerprint(
            git_root,
            exclude_paths=[state_dir] if state_dir is not None else [],
        ),
        "captured_at": utc_now(),
    }


def workspace_fingerprint(workspace: Path, *, exclude_paths: Iterable[Path] = ()) -> str | None:
    """Hash the current Git worktree state for evidence freshness checks.

    The fingerprint covers HEAD, tracked staged/unstaged changes, and untracked
    file contents. Non-Git workspaces return None rather than pretending a
    complete snapshot exists.
    """
    root_rc, root = _run_git(workspace, ["rev-parse", "--show-toplevel"])
    if root_rc != 0 or not root:
        return None
    git_root = Path(root).resolve()
    excluded_relatives: set[str] = set()
    for excluded in exclude_paths:
        try:
            relative = excluded.resolve().relative_to(git_root)
        except (OSError, ValueError):
            continue
        excluded_relatives.add(relative.as_posix().rstrip("/"))

    _, head = _run_git(git_root, ["rev-parse", "HEAD"])
    diff_args = ["diff", "--binary", "--no-ext-diff", "HEAD", "--", "."]
    diff_args.extend(f":(exclude){relative}/**" for relative in sorted(excluded_relatives))
    diff_rc, diff = _run_git(git_root, diff_args)
    if diff_rc not in {0, 1}:
        return None
    untracked_rc, untracked = _run_git(git_root, ["ls-files", "--others", "--exclude-standard"])
    if untracked_rc != 0:
        return None

    digest = hashlib.sha256()
    digest.update((head or "<no-head>").encode("utf-8", errors="replace"))
    digest.update(b"\0")
    digest.update(diff.encode("utf-8", errors="replace"))
    for relative in sorted(line for line in untracked.splitlines() if line):
        if any(relative == excluded or relative.startswith(excluded + "/") for excluded in excluded_relatives):
            continue
        path = (git_root / relative).resolve()
        try:
            path.relative_to(git_root)
        except ValueError:
            continue
        digest.update(b"\0")
        digest.update(relative.encode("utf-8", errors="surrogateescape"))
        if path.is_file():
            try:
                digest.update(_hash_file(path).encode("ascii"))
            except OSError:
                digest.update(b"<unreadable>")
        else:
            digest.update(b"<missing-or-nonfile>")
    return digest.hexdigest()


def _criterion(idx: int, statement: str, criterion_id: str | None = None) -> dict[str, Any]:
    statement = statement.strip()
    if not statement:
        raise ProofError("Acceptance criteria must be non-empty strings.")
    resolved_id = criterion_id or f"AC-{idx:02d}"
    if not CRITERION_ID_RE.fullmatch(resolved_id):
        raise ProofError(f"Invalid acceptance criterion id: {resolved_id!r}")
    return {
        "id": resolved_id,
        "statement": statement,
        "override_state": None,
        "override_reason": None,
        "evidence_ids": [],
    }


def load_ledger(workspace: str | Path | None = None) -> tuple[dict[str, Any], ProofPaths]:
    paths = proof_paths(workspace)
    if not paths.ledger.is_file():
        raise ProofError(f"No proof session exists at {paths.ledger}. Call proveit.start first.")
    try:
        ledger = json.loads(paths.ledger.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProofError(f"Invalid proof ledger: {exc}") from exc
    validate_ledger(ledger)
    return ledger, paths


def validate_ledger(ledger: dict[str, Any]) -> None:
    """Validate ledger structure and cross-references without third-party deps."""
    if not isinstance(ledger, dict):
        raise ProofError("Proof ledger must be a JSON object.")
    if ledger.get("schema_version") != SCHEMA_VERSION:
        raise ProofError(f"Unsupported proof schema: {ledger.get('schema_version')!r}")
    for key in ("session_id", "task", "workspace"):
        if not isinstance(ledger.get(key), str) or not ledger[key].strip():
            raise ProofError(f"Proof ledger field {key!r} must be a non-empty string.")
    if not isinstance(ledger.get("source_state"), dict):
        raise ProofError("Proof ledger source_state must be an object.")
    criteria = ledger.get("criteria")
    evidence = ledger.get("evidence")
    if not isinstance(criteria, list) or not criteria:
        raise ProofError("Proof ledger must contain at least one criterion.")
    if not isinstance(evidence, list):
        raise ProofError("Proof ledger evidence must be an array.")

    criterion_ids: set[str] = set()
    criteria_by_id: dict[str, dict[str, Any]] = {}
    for item in criteria:
        if not isinstance(item, dict):
            raise ProofError("Each criterion must be an object.")
        criterion_id = item.get("id")
        if not isinstance(criterion_id, str) or not CRITERION_ID_RE.fullmatch(criterion_id):
            raise ProofError(f"Invalid criterion id in ledger: {criterion_id!r}")
        if criterion_id in criterion_ids:
            raise ProofError(f"Duplicate criterion id in ledger: {criterion_id}")
        criterion_ids.add(criterion_id)
        criteria_by_id[criterion_id] = item
        if not isinstance(item.get("statement"), str) or not item["statement"].strip():
            raise ProofError(f"Criterion {criterion_id} has an empty statement.")
        if item.get("override_state") not in {None, "blocked", "waived"}:
            raise ProofError(f"Criterion {criterion_id} has an invalid override state.")
        if not isinstance(item.get("evidence_ids", []), list):
            raise ProofError(f"Criterion {criterion_id} evidence_ids must be an array.")

    evidence_ids: set[str] = set()
    evidence_by_id: dict[str, dict[str, Any]] = {}
    for item in evidence:
        if not isinstance(item, dict):
            raise ProofError("Each evidence item must be an object.")
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not EVIDENCE_ID_RE.fullmatch(evidence_id):
            raise ProofError(f"Invalid evidence id in ledger: {evidence_id!r}")
        if evidence_id in evidence_ids:
            raise ProofError(f"Duplicate evidence id in ledger: {evidence_id}")
        evidence_ids.add(evidence_id)
        evidence_by_id[evidence_id] = item
        ids = item.get("criterion_ids")
        if not isinstance(ids, list) or not ids:
            raise ProofError(f"Evidence {evidence_id} must reference at least one criterion.")
        unknown = sorted(set(ids) - criterion_ids)
        if unknown:
            raise ProofError(f"Evidence {evidence_id} references unknown criteria: {', '.join(unknown)}")
        if item.get("relation") not in EVIDENCE_RELATIONS:
            raise ProofError(f"Evidence {evidence_id} has an invalid relation.")
        if item.get("strength") not in EVIDENCE_STRENGTHS:
            raise ProofError(f"Evidence {evidence_id} has an invalid strength.")
        if item.get("provenance") not in {AGENT_REPORTED, SERVER_OBSERVED}:
            raise ProofError(f"Evidence {evidence_id} has an invalid provenance.")
        if not isinstance(item.get("summary"), str) or not item["summary"].strip():
            raise ProofError(f"Evidence {evidence_id} has an empty summary.")
        for criterion_id in ids:
            if evidence_id not in criteria_by_id[criterion_id].get("evidence_ids", []):
                raise ProofError(
                    f"Evidence {evidence_id} and criterion {criterion_id} have inconsistent cross-references."
                )

    for criterion in criteria:
        criterion_id = criterion["id"]
        refs = criterion.get("evidence_ids", [])
        if len(refs) != len(set(refs)):
            raise ProofError(f"Criterion {criterion_id} contains duplicate evidence references.")
        unknown = sorted(set(refs) - evidence_ids)
        if unknown:
            raise ProofError(f"Criterion {criterion_id} references unknown evidence: {', '.join(unknown)}")
        for evidence_id in refs:
            if criterion_id not in evidence_by_id[evidence_id]["criterion_ids"]:
                raise ProofError(
                    f"Criterion {criterion_id} and evidence {evidence_id} have inconsistent cross-references."
                )


def save_ledger(ledger: dict[str, Any], paths: ProofPaths) -> None:
    with _STATE_LOCK:
        ledger["updated_at"] = utc_now()
        validate_ledger(ledger)
        _atomic_write(paths.ledger, json.dumps(ledger, indent=2, sort_keys=False) + "\n")


def _criterion_by_id(ledger: dict[str, Any], criterion_id: str) -> dict[str, Any]:
    for item in ledger["criteria"]:
        if item["id"] == criterion_id:
            return item
    raise ProofError(f"Unknown acceptance criterion: {criterion_id}")


def _ensure_criterion_ids(ledger: dict[str, Any], criterion_ids: Iterable[str]) -> list[str]:
    ids = list(dict.fromkeys(str(value) for value in criterion_ids))
    if not ids:
        raise ProofError("At least one criterion id is required.")
    for criterion_id in ids:
        _criterion_by_id(ledger, criterion_id)
    return ids


@_state_mutation
def add_criterion(statement: str, *, workspace: str | Path | None = None, criterion_id: str | None = None) -> dict[str, Any]:
    ledger, paths = load_ledger(workspace)
    existing = {item["id"] for item in ledger["criteria"]}
    if criterion_id and criterion_id in existing:
        raise ProofError(f"Criterion already exists: {criterion_id}")
    if criterion_id is None:
        number = 1
        while f"AC-{number:02d}" in existing:
            number += 1
        criterion_id = f"AC-{number:02d}"
    item = _criterion(len(ledger["criteria"]) + 1, statement, criterion_id=criterion_id)
    ledger["criteria"].append(item)
    save_ledger(ledger, paths)
    return {"criterion": item, "status": "pending"}


def _workspace_file(paths: ProofPaths, value: str | Path) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = paths.workspace / candidate
    resolved = candidate.expanduser().resolve()
    try:
        resolved.relative_to(paths.workspace)
    except ValueError as exc:
        raise ProofError(f"Path escapes workspace: {value}") from exc
    return resolved


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _next_evidence_id(ledger: dict[str, Any]) -> str:
    existing = {item["id"] for item in ledger["evidence"]}
    number = 1
    while f"EV-{number:03d}" in existing:
        number += 1
    return f"EV-{number:03d}"
