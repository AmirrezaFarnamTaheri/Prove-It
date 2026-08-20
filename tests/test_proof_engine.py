from __future__ import annotations

import json
from pathlib import Path

import pytest

from prove_it.proof_engine import (
    ProofError,
    add_criterion,
    load_ledger,
    record_evidence,
    record_source,
    report,
    run_check,
    set_criterion_state,
    start_proof,
    status,
)


def test_start_and_source_evidence_can_reach_ready(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text("def answer():\n    return 42\n", encoding="utf-8")
    started = start_proof("Prove the answer", ["Source returns 42"], workspace=tmp_path)
    assert started["readiness"] == "CONDITIONAL"
    evidence = record_source(
        ["AC-01"],
        "app.py",
        "Implementation returns the expected value",
        workspace=tmp_path,
        line_start=1,
        line_end=2,
        expected_text="return 42",
    )
    assert evidence["provenance"] == "server-observed"
    current = status(workspace=tmp_path)
    assert current["readiness"] == "READY"
    assert current["criteria"][0]["status"] == "verified"


def test_agent_reported_evidence_is_only_partial(tmp_path: Path) -> None:
    start_proof("Task", ["Behavior works"], workspace=tmp_path)
    record_evidence(["AC-01"], "manual", "Agent says it worked", workspace=tmp_path, strength="verified")
    current = status(workspace=tmp_path)
    assert current["readiness"] == "CONDITIONAL"
    assert current["criteria"][0]["status"] == "partial"


def test_failed_check_contradicts_criterion(tmp_path: Path) -> None:
    start_proof("Task", ["Check passes"], workspace=tmp_path)
    result = run_check(
        ["AC-01"],
        ["python", "-c", "import sys; sys.exit(3)"],
        "Deterministic failure",
        workspace=tmp_path,
    )
    assert result["exit_code"] == 3
    assert result["relation"] == "contradicts"
    assert status(workspace=tmp_path)["readiness"] == "NOT_READY"


def test_successful_check_is_server_observed(tmp_path: Path) -> None:
    start_proof("Task", ["Check passes"], workspace=tmp_path)
    result = run_check(
        ["AC-01"],
        ["python", "-c", "print('ok')"],
        "Smoke check",
        workspace=tmp_path,
    )
    assert result["exit_code"] == 0
    assert result["provenance"] == "server-observed"
    assert "ok" in result["output_excerpt"]
    assert status(workspace=tmp_path)["readiness"] == "READY"


def test_disallowed_command_and_path_escape_are_rejected(tmp_path: Path) -> None:
    start_proof("Task", ["Safe"], workspace=tmp_path)
    with pytest.raises(ProofError):
        run_check(["AC-01"], ["sh", "-c", "echo nope"], "bad", workspace=tmp_path)
    outside = tmp_path.parent / "outside-proof.txt"
    outside.write_text("x", encoding="utf-8")
    with pytest.raises(ProofError):
        record_source(["AC-01"], str(outside), "outside", workspace=tmp_path)


def test_git_mutating_subcommands_are_rejected(tmp_path: Path) -> None:
    start_proof("Task", ["Safe git"], workspace=tmp_path)
    with pytest.raises(ProofError):
        run_check(["AC-01"], ["git", "reset", "--hard"], "bad git", workspace=tmp_path)


def test_blocked_and_waived_states_are_explicit(tmp_path: Path) -> None:
    start_proof("Task", ["A", "B"], workspace=tmp_path)
    set_criterion_state("AC-01", "blocked", "Needs external service", workspace=tmp_path)
    set_criterion_state("AC-02", "waived", "User waived it", workspace=tmp_path)
    current = status(workspace=tmp_path)
    assert current["criteria"][0]["status"] == "blocked"
    assert current["criteria"][1]["status"] == "waived"
    assert current["readiness"] == "CONDITIONAL"


def test_report_persists_markdown_and_json_ledger(tmp_path: Path) -> None:
    (tmp_path / "file.txt").write_text("proof\n", encoding="utf-8")
    start_proof("Task", ["File proves it"], workspace=tmp_path)
    record_source(["AC-01"], "file.txt", "Proof file", workspace=tmp_path)
    result = report(workspace=tmp_path)
    report_path = Path(result["report_file"])
    ledger_path = Path(result["proof_file"])
    assert report_path.is_file()
    assert "READY" in report_path.read_text(encoding="utf-8")
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["schema_version"] == "1.0"


def test_add_criterion_uses_next_id(tmp_path: Path) -> None:
    start_proof("Task", ["A"], workspace=tmp_path)
    added = add_criterion("B", workspace=tmp_path)
    assert added["criterion"]["id"] == "AC-02"
    ledger, _ = load_ledger(tmp_path)
    assert len(ledger["criteria"]) == 2


def _init_git_repo(path: Path) -> None:
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "prove-it@example.invalid"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Prove It Tests"], cwd=path, check=True)
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=path, check=True)


def test_source_evidence_becomes_stale_after_file_change(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text("value = 1\n", encoding="utf-8")
    start_proof("Task", ["Source is verified"], workspace=tmp_path)
    record_source(["AC-01"], "app.py", "Current source", workspace=tmp_path)
    assert status(workspace=tmp_path)["readiness"] == "READY"

    source.write_text("value = 2\n", encoding="utf-8")
    current = status(workspace=tmp_path)
    assert current["readiness"] == "CONDITIONAL"
    assert current["criteria"][0]["status"] == "pending"
    assert current["criteria"][0]["stale_evidence_count"] == 1
    assert current["evidence_freshness"]["stale"] == 1


def test_git_check_remains_fresh_after_ledger_write_then_stales_on_code_change(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text("value = 1\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    start_proof("Task", ["Verification passes"], workspace=tmp_path)
    run_check(
        ["AC-01"],
        ["python", "-c", "print('ok')"],
        "Smoke check",
        workspace=tmp_path,
    )
    assert status(workspace=tmp_path)["readiness"] == "READY"

    source.write_text("value = 2\n", encoding="utf-8")
    current = status(workspace=tmp_path)
    assert current["readiness"] == "CONDITIONAL"
    assert current["criteria"][0]["status"] == "pending"
    assert current["evidence_freshness"]["stale"] == 1


def test_start_accepts_one_string_criterion_without_splitting_characters(tmp_path: Path) -> None:
    current = start_proof("Task", "One criterion", workspace=tmp_path)
    assert [criterion["statement"] for criterion in current["criteria"]] == ["One criterion"]


def test_blocked_and_waived_require_reasons(tmp_path: Path) -> None:
    start_proof("Task", ["A"], workspace=tmp_path)
    with pytest.raises(ProofError):
        set_criterion_state("AC-01", "blocked", "", workspace=tmp_path)


def test_corrupt_ledger_cross_reference_is_rejected(tmp_path: Path) -> None:
    start_proof("Task", ["A"], workspace=tmp_path)
    ledger, paths = load_ledger(tmp_path)
    ledger["evidence"].append(
        {
            "id": "EV-001",
            "criterion_ids": ["AC-01"],
            "kind": "manual",
            "relation": "supports",
            "strength": "verified",
            "provenance": "agent-reported",
            "summary": "orphan evidence",
            "observed_at": "2026-08-19T00:00:00+00:00",
        }
    )
    paths.ledger.write_text(json.dumps(ledger), encoding="utf-8")
    with pytest.raises(ProofError, match="inconsistent cross-references"):
        load_ledger(tmp_path)


def test_git_source_state_marks_git_true(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text("value = 1\n", encoding="utf-8")
    _init_git_repo(tmp_path)
    current = start_proof("Task", ["A"], workspace=tmp_path)
    assert current["source_state"]["git"] is True


def test_explicit_path_cannot_borrow_allowlisted_basename(tmp_path: Path) -> None:
    fake_python = tmp_path / "python"
    fake_python.write_text("#!/bin/sh\necho fake\n", encoding="utf-8")
    fake_python.chmod(0o755)
    start_proof("Task", ["Safe executable"], workspace=tmp_path)
    with pytest.raises(ProofError, match="PATH-resolved"):
        run_check(["AC-01"], ["./python"], "must reject fake python", workspace=tmp_path)
