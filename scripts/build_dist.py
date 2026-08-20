from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from prove_it.composer import compose, validate_prompt  # noqa: E402


ALL_PROFILES = [
    "security",
    "data-migrations",
    "concurrency-runtime",
    "performance",
    "stateful-systems",
    "ui-ux",
    "cli-tui",
    "consolidation",
    "architecture-reconstruction",
    "high-assurance-validation",
    "peer-benchmarking",
    "audit-remediation",
    "technical-due-diligence",
]

TASK = {
    "objective": "Perform the engineering task supplied by the user in the surrounding conversation or appended task context.",
    "target": "Use the files, repository, system, documents, links, and other context supplied with the task.",
    "deliverables": ["The user's requested artifact or completed result"],
    "constraints": [
        "Apply only the conditional profiles relevant to the actual task.",
        "Follow higher-priority platform/system/user instructions over this protocol.",
    ],
    "acceptance_criteria": [
        "The requested work is actually performed.",
        "Material claims and completion status are evidence-grounded.",
        "Verification is proportional to risk and honestly reported.",
    ],
}

composition = compose(
    ROOT,
    TASK,
    template="universal",
    profiles=ALL_PROFILES,
    adapter="generic",
)
errors = validate_prompt(composition.text)
if errors:
    raise SystemExit("\n".join(errors))
output = ROOT / "build" / "generated" / "PROVE_IT_MASTER_PROMPT.md"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(composition.text, encoding="utf-8")
print(f"Wrote {output}")
