#!/usr/bin/env python3
"""Select an auto-merge PR candidate from GitHub PR JSON.

This script is deterministic and network-free. `loop_controller_github.sh` is
responsible for collecting `gh pr list --json ...` output; this script only
classifies that JSON into pass/reject/block/ignored candidate records.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "operations" / "auto_merge_policy.toml"
TICKET_RE = re.compile(r"\b(?:OPS|TKT)-\d{4}\b")
METADATA_RE = re.compile(r"reports/session_metadata/[A-Za-z0-9_.\-/]+\.(?:toml|json|md)")
QA_RE = re.compile(r"reports/qa/[A-Za-z0-9_.\-/]+\.(?:json|md)")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_policy(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing policy: {path}")
    if tomllib is None:
        # Minimal fallback for this policy's scalar/list usage.
        text = path.read_text(encoding="utf-8")
        label = re.search(r'required_label\s*=\s*"([^"]+)"', text)
        base = re.search(r'base_branch\s*=\s*"([^"]+)"', text)
        checks = re.findall(r'"([^"]+ / [^"]+)"', text)
        return {
            "required_label": label.group(1) if label else "loop:automerge",
            "base_branch": base.group(1) if base else "main",
            "required_checks": checks,
            "max_merge_candidates_per_run": 1,
        }
    return tomllib.loads(path.read_text(encoding="utf-8"))


def labels_of(pr: dict) -> set[str]:
    labels = set()
    for label in pr.get("labels") or []:
        if isinstance(label, str):
            labels.add(label)
        elif isinstance(label, dict) and label.get("name"):
            labels.add(str(label["name"]))
    return labels


def rollup_by_name(pr: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in pr.get("statusCheckRollup") or []:
        if not isinstance(item, dict):
            continue
        name = item.get("context") or item.get("name") or item.get("checkName")
        if not name:
            continue
        conclusion = item.get("conclusion") or item.get("state") or item.get("status") or "UNKNOWN"
        result[str(name)] = str(conclusion).upper()
    return result


def check_state_ok(state: str) -> bool:
    return state in {"SUCCESS", "COMPLETED", "NEUTRAL", "SKIPPED", "PASS", "PASSED"}


def check_state_pending(state: str) -> bool:
    return state in {"PENDING", "QUEUED", "IN_PROGRESS", "REQUESTED", "WAITING", "UNKNOWN", "EXPECTED"}


def extract_first(pattern: re.Pattern[str], text: str) -> str | None:
    m = pattern.search(text or "")
    return m.group(0) if m else None


def classify_pr(pr: dict, policy: dict) -> dict:
    number = pr.get("number")
    body = pr.get("body") or ""
    base_branch = policy.get("base_branch", "main")
    required_label = policy.get("required_label", "loop:automerge")
    required_checks = list(policy.get("required_checks") or [])
    labels = labels_of(pr)

    record = {
        "number": number,
        "title": pr.get("title"),
        "baseRefName": pr.get("baseRefName"),
        "headRefName": pr.get("headRefName"),
        "headRefOid": pr.get("headRefOid"),
        "labels": sorted(labels),
        "ticket_id": extract_first(TICKET_RE, body) or extract_first(TICKET_RE, pr.get("headRefName") or "") or extract_first(TICKET_RE, pr.get("title") or ""),
        "metadata_path": extract_first(METADATA_RE, body),
        "qa_verdict_path": extract_first(QA_RE, body),
        "verdict": "ignored",
        "reasons": [],
        "required_checks": {},
    }

    if required_label not in labels:
        record["reasons"].append("missing required label loop:automerge")
        return record

    reject: list[str] = []
    block: list[str] = []

    if pr.get("isDraft") is True:
        block.append("pull request is draft")
    if pr.get("baseRefName") != base_branch:
        reject.append(f"base branch is {pr.get('baseRefName')!r}, expected {base_branch!r}")
    if not record["ticket_id"]:
        reject.append("ticket id not found in PR body, title, or branch")
    if not record["metadata_path"]:
        reject.append("session metadata path not found in PR body")
    if not record["qa_verdict_path"]:
        reject.append("QA verdict path not found in PR body")
    if not record["headRefOid"]:
        reject.append("PR head SHA is missing")

    rollup = rollup_by_name(pr)
    for check in required_checks:
        state = rollup.get(check)
        record["required_checks"][check] = state or "MISSING"
        if state is None:
            block.append(f"required check missing: {check}")
        elif check_state_ok(state):
            continue
        elif check_state_pending(state):
            block.append(f"required check pending: {check}={state}")
        else:
            reject.append(f"required check failed: {check}={state}")

    if reject:
        record["verdict"] = "reject"
        record["reasons"] = reject + block
    elif block:
        record["verdict"] = "block"
        record["reasons"] = block
    else:
        record["verdict"] = "pass"
        record["reasons"] = []
    return record


def overall_verdict(records: list[dict], policy: dict) -> tuple[str, dict | None, list[str]]:
    labeled = [r for r in records if r["verdict"] != "ignored"]
    passed = [r for r in records if r["verdict"] == "pass"]
    blocked = [r for r in records if r["verdict"] == "block"]
    rejected = [r for r in records if r["verdict"] == "reject"]
    max_candidates = int(policy.get("max_merge_candidates_per_run", 1) or 1)

    if len(passed) == 1 and len(passed) <= max_candidates:
        return "pass", passed[0], ["exactly one passing auto-merge candidate found"]
    if len(passed) > max_candidates:
        return "block", None, [f"multiple passing candidates found: {[r['number'] for r in passed]}"]
    if blocked:
        return "block", None, ["one or more labeled candidates are waiting for evidence or required checks"]
    if rejected:
        return "reject", None, ["labeled candidates exist, but all are rejected by policy"]
    if not labeled:
        return "block", None, ["no open PR has the required loop:automerge label"]
    return "block", None, ["no passing candidate found"]


def write_markdown(path: Path, plan: dict) -> None:
    lines = [
        "# Auto-Merge Candidate Plan",
        "",
        f"- verdict: `{plan['verdict']}`",
        f"- selected_pr: `{plan['selected_pr']['number'] if plan.get('selected_pr') else 'none'}`",
        f"- required_label: `{plan['required_label']}`",
        f"- base_branch: `{plan['base_branch']}`",
        "",
        "## Reasons",
        "",
    ]
    for reason in plan.get("reasons") or []:
        lines.append(f"- {reason}")
    lines += ["", "## Candidates", ""]
    for rec in plan.get("candidates") or []:
        lines.append(f"- PR #{rec.get('number')}: `{rec.get('verdict')}` ticket=`{rec.get('ticket_id')}` head=`{rec.get('headRefOid')}`")
        for reason in rec.get("reasons") or []:
            lines.append(f"  - {reason}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to gh pr list JSON, or '-' for stdin")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--out", required=True, help="Candidate plan JSON output path")
    parser.add_argument("--markdown", help="Candidate plan Markdown output path")
    parser.add_argument("--expect", choices=["pass", "reject", "block", "ignored"])
    parser.add_argument("--require-pass", action="store_true", help="Exit non-zero unless verdict is pass")
    args = parser.parse_args()

    raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
    try:
        prs = json.loads(raw or "[]")
    except json.JSONDecodeError as exc:
        fail(f"invalid PR JSON: {exc}")
    if not isinstance(prs, list):
        fail("PR JSON must be a list")

    policy = load_policy(Path(args.policy))
    records = [classify_pr(pr, policy) for pr in prs]
    verdict, selected, reasons = overall_verdict(records, policy)
    plan = {
        "schema": "schemas/auto_merge_candidate_schema.md",
        "verdict": verdict,
        "selected_pr": selected,
        "required_label": policy.get("required_label", "loop:automerge"),
        "base_branch": policy.get("base_branch", "main"),
        "required_checks": list(policy.get("required_checks") or []),
        "max_merge_candidates_per_run": int(policy.get("max_merge_candidates_per_run", 1) or 1),
        "reasons": reasons,
        "candidates": records,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        md = Path(args.markdown)
        md.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(md, plan)

    print(json.dumps({"verdict": verdict, "selected_pr": selected.get("number") if selected else None, "reasons": reasons}, ensure_ascii=False))
    if args.expect and verdict != args.expect:
        fail(f"expected verdict {args.expect}, got {verdict}")
    if args.require_pass and verdict != "pass":
        fail(f"candidate plan is not pass: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
