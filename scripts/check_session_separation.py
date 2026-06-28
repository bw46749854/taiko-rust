#!/usr/bin/env python3
"""Validate session separation-separation metadata.

Default invocation performs static package validation. Use --metadata or --ticket
for a concrete PR/run metadata file. --pr-gate validates changed metadata files
and blocks implementation/QA/review PRs that omit them.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except Exception:  # pragma: no cover
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "docs/90_session_metadata_and_path_policy.md",
    "operations/path_policy.toml",
    "schemas/session_metadata_schema.md",
    "templates/session_run_metadata_template.toml",
    "reports/session_metadata/README.md",
]

QA_REQUIRED_FIELDS = [
    "ticket_id",
    "run_id",
    "qa_session_id",
    "source_worktree",
    "verdict",
    "next_action",
    "evidence_inputs",
    "failure_route",
]
VALID_QA_VERDICTS = {"pass", "reject", "block"}


def qa_field_present(data: dict, field: str) -> bool:
    value = data.get(field)
    if value in (None, ""):
        return False
    if isinstance(value, list) and not value:
        return False
    return True


def validate_qa_verdict_payload(qa: dict, meta: dict | None = None) -> list[str]:
    issues: list[str] = []
    missing = [field for field in QA_REQUIRED_FIELDS if not qa_field_present(qa, field)]
    issues.extend(f"qa verdict missing or empty field: {field}" for field in missing)

    verdict = str(qa.get("verdict", ""))
    if verdict and verdict not in VALID_QA_VERDICTS:
        issues.append(f"qa verdict must be one of pass/reject/block, got {verdict}")

    if meta is not None:
        comparisons = [
            ("ticket_id", "ticket_id", "qa verdict ticket_id differs from metadata ticket_id"),
            ("run_id", "run_id", "qa verdict run_id differs from metadata run_id"),
            ("qa_session_id", "qa_session_id", "qa verdict qa_session_id differs from metadata qa_session_id"),
            ("source_worktree", "qa_worktree", "qa verdict source_worktree differs from metadata qa_worktree"),
        ]
        for qa_key, meta_key, message in comparisons:
            if qa.get(qa_key) and meta.get(meta_key) and str(qa.get(qa_key)) != str(meta.get(meta_key)):
                issues.append(message)
        legacy_session = qa.get("session_id")
        if legacy_session and meta.get("qa_session_id") and str(legacy_session) != str(meta.get("qa_session_id")):
            issues.append("qa verdict session_id differs from metadata qa_session_id")

    failure_route = qa.get("failure_route") if isinstance(qa.get("failure_route"), dict) else {}
    if verdict == "reject":
        for field in ["classification_path", "materialization_path", "repair_ticket_id"]:
            if not failure_route.get(field):
                issues.append(f"reject qa verdict requires failure_route.{field}")
    if verdict == "block":
        missing_evidence = qa.get("missing_evidence")
        if not isinstance(missing_evidence, list) or not missing_evidence:
            issues.append("block qa verdict requires non-empty missing_evidence list")
        for field in ["blocker_ticket_id", "blocker_route"]:
            if not failure_route.get(field):
                issues.append(f"block qa verdict requires failure_route.{field}")
    return issues

REQUIRED_FIELDS = [
    "schema_version",
    "run_id",
    "ticket_id",
    "implementation_session_id",
    "review_session_id",
    "qa_session_id",
    "implementation_branch",
    "implementation_worktree",
    "review_worktree",
    "qa_worktree",
    "qa_verdict_path",
    "plan_path",
    "command_log_path",
    "preflight_report_path",
    "gate_report_path",
    "implementation_may_write_code",
    "review_may_write_code",
    "qa_may_write_code",
    "control_may_merge",
]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def load_toml(path: Path) -> dict:
    if tomllib is None:
        fail("Python tomllib is required; use Python 3.11+ for session metadata validation")
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid TOML in {path}: {exc}")


def validate_metadata(path: Path, require_qa_verdict: bool = False) -> list[str]:
    issues: list[str] = []
    if not path.is_file():
        return [f"missing metadata file: {path}"]
    data = load_toml(path)
    missing = [field for field in REQUIRED_FIELDS if field not in data or data.get(field) in ("", None)]
    issues.extend(f"missing or empty field: {field}" for field in missing)

    ticket = str(data.get("ticket_id", ""))
    impl_session = str(data.get("implementation_session_id", ""))
    review_session = str(data.get("review_session_id", ""))
    qa_session = str(data.get("qa_session_id", ""))
    sessions = {
        "implementation_session_id": impl_session,
        "review_session_id": review_session,
        "qa_session_id": qa_session,
    }
    nonempty_sessions = {name: value for name, value in sessions.items() if value}
    if len(set(nonempty_sessions.values())) != len(nonempty_sessions):
        issues.append("implementation/review/qa session IDs must be distinct")

    expected_impl = f"worktrees/impl/{ticket}"
    expected_review = f"worktrees/review/{ticket}"
    expected_qa = f"worktrees/qa/{ticket}"
    if ticket and data.get("implementation_worktree") != expected_impl:
        issues.append(f"implementation_worktree must be {expected_impl}")
    if ticket and data.get("review_worktree") != expected_review:
        issues.append(f"review_worktree must be {expected_review}")
    if ticket and data.get("qa_worktree") != expected_qa:
        issues.append(f"qa_worktree must be {expected_qa}")

    branch = str(data.get("implementation_branch", ""))
    if ticket and ticket not in branch:
        issues.append("implementation_branch must contain ticket_id")

    qa_path = ROOT / str(data.get("qa_verdict_path", ""))
    if require_qa_verdict and not qa_path.is_file():
        issues.append(f"qa verdict path does not exist: {qa_path.relative_to(ROOT) if qa_path.is_absolute() and ROOT in qa_path.parents else qa_path}")
    if qa_path.is_file():
        try:
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(f"qa verdict JSON is invalid: {exc}")
        else:
            issues.extend(validate_qa_verdict_payload(qa, data))
    return issues


def changed_files() -> list[str]:
    env_files = os.environ.get("CHANGED_FILES")
    if env_files:
        return [line.strip() for line in env_files.splitlines() if line.strip()]
    base = os.environ.get("GITHUB_BASE_REF")
    if not base:
        return []
    candidates = [f"origin/{base}...HEAD", f"{base}...HEAD"]
    for spec in candidates:
        try:
            out = subprocess.check_output(["git", "diff", "--name-only", spec], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
            return [line for line in out.splitlines() if line]
        except Exception:
            continue
    return []


def infer_pr_role() -> str:
    ref = os.environ.get("GITHUB_HEAD_REF", "")
    if ref.startswith("impl/"):
        return "impl"
    if ref.startswith("qa/"):
        return "qa"
    if ref.startswith("review/"):
        return "review"
    if ref.startswith("loop/"):
        return "control"
    if ref.startswith("test/"):
        return "test-infra"
    if ref.startswith("spec/"):
        return "spec"
    return ""


def static_check() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required session separation file: {rel}")
    template = ROOT / "templates/session_run_metadata_template.toml"
    issues = validate_metadata(template, require_qa_verdict=False)
    allowed_template_issues = [issue for issue in issues if not issue.startswith("implementation_worktree must be")]
    if allowed_template_issues:
        fail("template metadata failed validation: " + "; ".join(allowed_template_issues))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", help="Path to a concrete metadata TOML file")
    parser.add_argument("--ticket", help="Ticket ID; validates reports/session_metadata/<ticket>.toml")
    parser.add_argument("--require-qa-verdict", action="store_true")
    parser.add_argument("--pr-gate", action="store_true")
    args = parser.parse_args()

    static_check()

    paths: list[Path] = []
    if args.metadata:
        paths.append(ROOT / args.metadata)
    if args.ticket:
        paths.append(ROOT / f"reports/session_metadata/{args.ticket}.toml")
    if args.pr_gate:
        files = changed_files()
        paths.extend(ROOT / rel for rel in files if rel.startswith("reports/session_metadata/") and rel.endswith(".toml"))
        role = infer_pr_role()
        if role in {"impl", "qa", "review"} and not paths:
            fail(f"{role} PR is missing reports/session_metadata/<ticket-id>.toml")

    all_issues: list[str] = []
    for path in sorted(set(paths)):
        display_path = path.relative_to(ROOT) if path.is_absolute() and path.is_relative_to(ROOT) else path
        all_issues.extend(f"{display_path}: {issue}" for issue in validate_metadata(path, args.require_qa_verdict))
    if all_issues:
        fail("session separation check failed:\n" + "\n".join(f"- {issue}" for issue in all_issues))

    print("session separation check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
