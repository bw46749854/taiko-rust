#!/usr/bin/env python3
"""Validate Step18 role-based path policy.

The policy is intentionally conservative and Python-only. It can run in static
mode without git, or in PR mode using CHANGED_FILES / git diff.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except Exception:  # pragma: no cover
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "operations/path_policy.toml"
REQUIRED_ROLES = ["impl", "qa", "review", "control", "test-infra", "spec"]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def load_policy() -> dict:
    if not POLICY.is_file():
        fail("missing operations/path_policy.toml")
    if tomllib is None:
        fail("Python tomllib is required; use Python 3.11+ for role path policy validation")
    try:
        data = tomllib.loads(POLICY.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid operations/path_policy.toml: {exc}")
    roles = data.get("roles", {})
    for role in REQUIRED_ROLES:
        if role not in roles:
            fail(f"path policy missing role: {role}")
        for field in ["allow_prefixes", "deny_prefixes", "deny_exact", "may_write_code", "may_write_qa_verdict", "may_merge"]:
            if field not in roles[role]:
                fail(f"path policy role {role} missing field: {field}")
    return roles


def changed_files() -> list[str]:
    env_files = os.environ.get("CHANGED_FILES")
    if env_files:
        return [line.strip() for line in env_files.splitlines() if line.strip()]
    base = os.environ.get("GITHUB_BASE_REF")
    if not base:
        return []
    for spec in [f"origin/{base}...HEAD", f"{base}...HEAD"]:
        try:
            out = subprocess.check_output(["git", "diff", "--name-only", spec], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
            return [line for line in out.splitlines() if line]
        except Exception:
            continue
    return []


def infer_role(explicit: str | None) -> str:
    if explicit:
        return explicit
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


def violates(role_policy: dict, file_path: str) -> str | None:
    for exact in role_policy.get("deny_exact", []):
        if file_path == exact:
            return f"denied exact path: {exact}"
    for prefix in role_policy.get("deny_prefixes", []):
        if file_path.startswith(prefix):
            return f"denied prefix: {prefix}"
    allow = role_policy.get("allow_prefixes", [])
    if allow and not any(file_path.startswith(prefix) for prefix in allow):
        return "not covered by allow_prefixes"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=REQUIRED_ROLES)
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--pr-gate", action="store_true")
    args = parser.parse_args()

    roles = load_policy()
    if not args.pr_gate and not args.role and not args.changed_file:
        print("role path policy static check passed")
        return 0

    role = infer_role(args.role)
    files = args.changed_file or changed_files()
    if not role:
        print("role path policy check skipped: no role inferred")
        return 0
    if role not in roles:
        fail(f"unknown role: {role}")
    if not files:
        print(f"role path policy check passed for {role}: no changed files")
        return 0

    issues = []
    for file_path in files:
        if file_path.startswith("worktrees/"):
            issues.append(f"worktree path must not be committed: {file_path}")
            continue
        reason = violates(roles[role], file_path)
        if reason:
            issues.append(f"{file_path}: {reason}")
    if issues:
        fail("role path policy check failed:\n" + "\n".join(f"- {issue}" for issue in issues))
    print(f"role path policy check passed for {role}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
