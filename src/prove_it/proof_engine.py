"""Public facade for the Prove It proof engine."""

from ._proof_state import (
    ProofError,
    ProofPaths,
    add_criterion,
    capture_source_state,
    load_ledger,
    proof_paths,
    save_ledger,
    validate_ledger,
    workspace_fingerprint,
)
from ._proof_actions import (
    criterion_status,
    evidence_freshness,
    record_evidence,
    record_source,
    report,
    run_check,
    set_criterion_state,
    start_proof,
    status,
    summarize,
)

__all__ = [
    "ProofError", "ProofPaths", "add_criterion", "capture_source_state",
    "criterion_status", "evidence_freshness", "load_ledger", "proof_paths",
    "record_evidence", "record_source", "report", "run_check", "save_ledger",
    "set_criterion_state", "start_proof", "status", "summarize",
    "validate_ledger", "workspace_fingerprint",
]
