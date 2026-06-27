#!/usr/bin/env python3
"""Validate OPS-0005 GitHub Actions gate normalization.

This check is intentionally static and network-free. It verifies that GitHub
Actions remains a deterministic verifier/gate/controller, not an AI worker.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

REQUIRED_FILES = [
    "docs/53_ci_commands.md",
    "docs/84_github_pr_loop_contract.md",
    "docs/85_rust_enabled_preflight_gate.md",
    "docs/93_github_actions_auto_merge_controller.md",
    "operations/auto_merge_policy.toml",
    ".github/workflows/loop-pr-gate.yml",
    ".github/workflows/rust-preflight.yml",
    ".github/workflows/phase1-loop.yml",
    ".github/workflows/phase1-gameplay-entry.yml",
    ".github/workflows/e2e-smoke-loop.yml",
    ".github/workflows/loop-controller.yml",
    "scripts/check_github_actions_gate_static.py",
]

EXPECTED_REQUIRED_CHECKS = [
    "loop-pr-gate / loop-pr-gate",
    "rust-preflight / rust-preflight",
    "phase1-loop / phase1-loop",
    "phase1-gameplay-entry / phase1-gameplay-entry",
]

FORBIDDEN_WORKFLOW_TERMS = [
    "pull_request_target",
    "openai/codex-action@v1",
    "secrets.OPENAI_API_KEY",
    "secrets.CODEX_API_KEY",
    "OPENAI_API_KEY:",
    "CODEX_API_KEY:",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def check_required_files() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")
    mode = (ROOT / "scripts/check_github_actions_gate_static.py").stat().st_mode
    if mode & 0o111 == 0:
        fail("scripts/check_github_actions_gate_static.py must be executable")


def check_policy() -> None:
    if tomllib is None:
        text = read("operations/auto_merge_policy.toml")
        for check in EXPECTED_REQUIRED_CHECKS:
            if check not in text:
                fail(f"operations/auto_merge_policy.toml missing required check: {check}")
        return
    policy = tomllib.loads(read("operations/auto_merge_policy.toml"))
    if policy.get("api_key_required") is not False:
        fail("auto_merge_policy.toml must set api_key_required = false")
    if policy.get("ai_workers_in_github_actions") is not False:
        fail("auto_merge_policy.toml must set ai_workers_in_github_actions = false")
    checks = policy.get("required_checks") or []
    missing = [item for item in EXPECTED_REQUIRED_CHECKS if item not in checks]
    if missing:
        fail("auto_merge_policy.toml missing required checks: " + ", ".join(missing))
    if policy.get("workflow_run_success_guard_required") is not True:
        fail("auto_merge_policy.toml must set workflow_run_success_guard_required = true")
    if policy.get("privileged_workflow_may_checkout_pr_head") is not False:
        fail("auto_merge_policy.toml must set privileged_workflow_may_checkout_pr_head = false")


def check_workflows() -> None:
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for term in FORBIDDEN_WORKFLOW_TERMS:
            if term in text:
                fail(f"{rel} contains forbidden workflow term: {term}")
        if "permissions:" not in text:
            fail(f"{rel} must define explicit permissions")
        if "actions/checkout@v4" in text and "persist-credentials: false" not in text and rel != ".github/workflows/loop-controller.yml":
            fail(f"{rel} must use persist-credentials: false")

    expected = {
        ".github/workflows/loop-pr-gate.yml": ["name: loop-pr-gate", "loop-pr-gate:", "Check GitHub Actions gate normalization"],
        ".github/workflows/rust-preflight.yml": ["name: rust-preflight", "rust-preflight:", "timeout-minutes:"],
        ".github/workflows/phase1-loop.yml": ["name: phase1-loop", "phase1-loop:", "timeout-minutes:"],
        ".github/workflows/phase1-gameplay-entry.yml": ["name: phase1-gameplay-entry", "phase1-gameplay-entry:", "timeout-minutes:"],
        ".github/workflows/e2e-smoke-loop.yml": ["name: e2e-smoke-loop", "workflow_run:", "github.event.workflow_run.conclusion == 'success'"],
        ".github/workflows/loop-controller.yml": [
            "name: loop-controller",
            "concurrency:",
            "group: loop-controller-main",
            "workflow_run:",
            "github.event.workflow_run.conclusion == 'success'",
            "contents: write",
            "pull-requests: write",
            "actions: read",
            "checks: read",
            "scripts/check_github_actions_gate_static.py",
        ],
    }
    for rel, terms in expected.items():
        text = read(rel)
        for term in terms:
            if term not in text:
                fail(f"{rel} missing required term: {term}")


def check_docs_and_scripts() -> None:
    required_terms = {
        "docs/53_ci_commands.md": ["OPS-0005 GitHub Actions gate normalization", "loop-controller-main", "scripts/check_github_actions_gate_static.py"],
        "docs/84_github_pr_loop_contract.md": ["OPS-0005 GitHub Actions gate normalization", "loop-pr-gate / loop-pr-gate"],
        "docs/85_rust_enabled_preflight_gate.md": ["OPS-0005", "rust-preflight / rust-preflight"],
        "docs/93_github_actions_auto_merge_controller.md": ["OPS-0005", "workflow_run success guard", "privileged workflow must not checkout PR head code"],
        "scripts/ci_local_equivalent.sh": ["scripts/check_github_actions_gate_static.py"],
        "scripts/check_bootstrap_consistency.sh": ["scripts/check_github_actions_gate_static.py", "TKT-0005.md"],
        "README.md": ["OPS-0005", "GitHub Actions gate normalization"],
        "AGENTS.md": ["OPS-0005 GitHub Actions gate normalization"],
    }
    for rel, terms in required_terms.items():
        text = read(rel)
        for term in terms:
            if term not in text:
                fail(f"{rel} missing required term: {term}")


def main() -> int:
    check_required_files()
    check_policy()
    check_workflows()
    check_docs_and_scripts()
    print("github actions gate static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
