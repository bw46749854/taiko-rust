#!/usr/bin/env python3
"""Validate session separation role-based path policy.

The policy is intentionally conservative and Python-only. It can run in static
mode without git, or in PR mode using CHANGED_FILES / git diff.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import re
from pathlib import Path

try:
    import tomllib
except Exception:  # pragma: no cover
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "operations/path_policy.toml"
REQUIRED_ROLES = ["impl", "qa", "review", "control", "test-infra", "spec"]
GATE_STATUS_RE = re.compile(r"^\.loop/gates/.*(?:status|state).*\.(?:toml|json|md)$")
GATE_SESSION_LOG_RE = re.compile(r"^\.loop/session_logs/.*GATE.*\.md$")


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
        for field in ["branch_prefixes", "required_worktree_prefix", "allow_prefixes", "deny_prefixes", "deny_exact", "may_write_code", "may_write_qa_verdict", "may_merge"]:
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


def parse_simple_toml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def metadata_files(files: list[str]) -> list[str]:
    return [f for f in files if f.startswith("reports/session_metadata/") and f.endswith(".toml")]


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
    if ref.startswith("control/"):
        return "control"
    if ref.startswith("test-infra/"):
        return "test-infra"
    if ref.startswith("loop/") or ref.startswith("test/"):
        return ""
    if ref.startswith("spec/"):
        return "spec"
    return ""


def role_from_branch(roles: dict, branch: str) -> str:
    matches = [role for role, policy in roles.items() if any(branch.startswith(prefix) for prefix in policy.get("branch_prefixes", []))]
    if len(matches) == 1:
        return matches[0]
    return ""


def validate_context(roles: dict, role: str, branch: str, worktree: str, metadata: dict[str, str] | None) -> list[str]:
    issues: list[str] = []
    policy = roles[role]
    if branch:
        expected_prefixes = policy.get("branch_prefixes", [])
        if not any(branch.startswith(prefix) for prefix in expected_prefixes):
            issues.append(f"branch {branch!r} does not match role {role} prefixes: {', '.join(expected_prefixes)}")
        branch_role = role_from_branch(roles, branch)
        if branch_role and branch_role != role:
            issues.append(f"branch {branch!r} maps to role {branch_role}, not {role}")
    if worktree:
        required = str(policy.get("required_worktree_prefix", ""))
        if required and not worktree.startswith(required):
            issues.append(f"worktree {worktree!r} does not start with {required!r} for role {role}")
    if metadata:
        ticket = metadata.get("ticket_id", "")
        impl_branch = metadata.get("implementation_branch", "")
        if impl_branch and not impl_branch.startswith(f"impl/{ticket}-"):
            issues.append("implementation_branch must use impl/<ticket-id>-... prefix")
        role_branch_key = {"impl": "implementation_branch", "qa": "qa_branch", "review": "review_branch", "control": "control_branch"}.get(role)
        if role_branch_key and metadata.get(role_branch_key) and branch and metadata[role_branch_key] != branch:
            issues.append(f"metadata {role_branch_key} does not match branch {branch!r}")
        role_worktree_key = {"impl": "implementation_worktree", "qa": "qa_worktree", "review": "review_worktree", "control": "control_worktree"}.get(role)
        if role_worktree_key and metadata.get(role_worktree_key) and worktree and metadata[role_worktree_key] != worktree:
            issues.append(f"metadata {role_worktree_key} does not match worktree {worktree!r}")
    return issues


def violates(role_policy: dict, file_path: str) -> str | None:
    if role_policy.get("name") == "impl":
        if GATE_SESSION_LOG_RE.match(file_path):
            return "implementation role may not write gate session logs"
        if GATE_STATUS_RE.match(file_path):
            return "implementation role may not mutate gate status"
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
    parser.add_argument("--branch")
    parser.add_argument("--worktree")
    parser.add_argument("--metadata")
    parser.add_argument("--pr-gate", action="store_true")
    args = parser.parse_args()

    roles = load_policy()
    if not args.pr_gate and not args.role and not args.changed_file:
        print("role path policy static check passed")
        return 0

    role = infer_role(args.role)
    branch = args.branch or os.environ.get("GITHUB_HEAD_REF", "")
    files = args.changed_file or changed_files()
    metadata = None
    metadata_arg = args.metadata
    if not metadata_arg and args.pr_gate:
        mfiles = metadata_files(files)
        if len(mfiles) == 1:
            metadata_arg = mfiles[0]
    if metadata_arg:
        metadata_path = ROOT / metadata_arg
        if not metadata_path.is_file():
            fail(f"missing metadata file: {metadata_arg}")
        metadata = parse_simple_toml(metadata_path)
        if not role and metadata.get("implementation_branch") == branch:
            role = "impl"
    if not role and branch:
        role = role_from_branch(roles, branch)
    if not role and args.pr_gate:
        fail(f"could not infer role from branch {branch!r}")
    if not role:
        print("role path policy check skipped: no role inferred")
        return 0
    if role not in roles:
        fail(f"unknown role: {role}")
    for r, policy in roles.items():
        policy["name"] = r
    issues = validate_context(roles, role, branch, args.worktree or "", metadata)
    if not files and not issues:
        print(f"role path policy check passed for {role}: no changed files")
        return 0
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
