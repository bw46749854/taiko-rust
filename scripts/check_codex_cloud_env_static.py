#!/usr/bin/env python3
"""Static validation for Step16 Codex Cloud / CI hardening files."""
from __future__ import annotations

import os
import re
import stat
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "rust-toolchain.toml",
    ".codex/config.toml",
    ".cargo/config.toml",
    "docs/86_codex_cloud_environment_setup.md",
    "docs/87_secret_and_network_policy.md",
    "scripts/codex_cloud_setup.sh",
    "scripts/ci_local_equivalent.sh",
    "scripts/check_codex_cloud_env_static.py",
]

REQUIRED_DOC_TERMS = {
    "docs/86_codex_cloud_environment_setup.md": [
        "Codex Cloud",
        "scripts/codex_cloud_setup.sh",
        "scripts/run_rust_preflight.sh",
        "rust-toolchain.toml",
        "agent internet access",
        "TKT-0001",
        "GATE-0030",
    ],
    "docs/87_secret_and_network_policy.md": [
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
        "job-level environment variable",
        "agent internet access",
        "setup script",
        "commercial song",
        "user-selected",
    ],
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def require_executable(rel: str) -> None:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing executable script: {rel}")
    if not (path.stat().st_mode & stat.S_IXUSR):
        fail(f"script is not executable: {rel}")


def check_required_files() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")


def check_rust_toolchain() -> None:
    if tomllib is None:
        fail("Python tomllib is required to parse rust-toolchain.toml")
    data = tomllib.loads(read_text("rust-toolchain.toml"))
    toolchain = data.get("toolchain")
    if not isinstance(toolchain, dict):
        fail("rust-toolchain.toml must contain [toolchain]")
    channel = toolchain.get("channel")
    if not isinstance(channel, str) or not re.fullmatch(r"\d+\.\d+\.\d+", channel):
        fail("rust-toolchain.toml [toolchain].channel must be a pinned x.y.z Rust version")
    profile = toolchain.get("profile")
    if profile != "minimal":
        fail("rust-toolchain.toml [toolchain].profile must be minimal")
    components = toolchain.get("components")
    if not isinstance(components, list):
        fail("rust-toolchain.toml [toolchain].components must be a list")
    for component in ("rustfmt", "clippy"):
        if component not in components:
            fail(f"rust-toolchain.toml must include component: {component}")


def check_codex_config() -> None:
    text = read_text(".codex/config.toml")
    if "danger-full-access" in text:
        fail(".codex/config.toml must not use danger-full-access")
    if re.search(r"approval_policy\s*=\s*\"never\"", text):
        fail(".codex/config.toml must not set approval_policy = \"never\"")
    required = [
        'sandbox_mode = "workspace-write"',
        'default_permissions = "opentaiko-loop"',
        "[shell_environment_policy]",
        "[permissions.opentaiko-loop]",
        "[permissions.opentaiko-loop.network]",
        "enabled = false",
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
        "fixtures/user_selected/**",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        fail(".codex/config.toml missing required terms: " + ", ".join(missing))
    if tomllib is not None:
        data = tomllib.loads(text)
        if data.get("default_permissions") != "opentaiko-loop":
            fail(".codex/config.toml default_permissions mismatch")


def check_docs() -> None:
    for rel, terms in REQUIRED_DOC_TERMS.items():
        text = read_text(rel)
        lower = text.lower()
        missing = [term for term in terms if term.lower() not in lower]
        if missing:
            fail(f"{rel} missing required terms: {', '.join(missing)}")


def check_scripts() -> None:
    for rel in ["scripts/codex_cloud_setup.sh", "scripts/ci_local_equivalent.sh"]:
        require_executable(rel)
        text = read_text(rel)
        if "set -euo pipefail" not in text:
            fail(f"{rel} must use set -euo pipefail")
    setup = read_text("scripts/codex_cloud_setup.sh")
    for term in ["rust-toolchain.toml", "rustup toolchain install", "scripts/check_bootstrap_consistency.sh"]:
        if term not in setup:
            fail(f"scripts/codex_cloud_setup.sh missing term: {term}")
    ci = read_text("scripts/ci_local_equivalent.sh")
    for term in ["--static-only", "scripts/run_rust_preflight.sh", "scripts/check_runtime_evidence_files.py", "scripts/check_codex_cloud_env_static.py"]:
        if term not in ci:
            fail(f"scripts/ci_local_equivalent.sh missing term: {term}")


def check_workflows_and_docs_wiring() -> None:
    for rel in [
        ".github/workflows/phase1-loop.yml",
        ".github/workflows/loop-pr-gate.yml",
        ".github/workflows/rust-preflight.yml",
    ]:
        text = read_text(rel)
        if "check_codex_cloud_env_static.py" not in text:
            fail(f"{rel} must run check_codex_cloud_env_static.py")
        if "codex_cloud_setup.sh" not in text and rel != ".github/workflows/loop-pr-gate.yml":
            fail(f"{rel} must run codex_cloud_setup.sh")
    bootstrap = read_text("scripts/check_bootstrap_consistency.sh")
    for term in [
        "rust-toolchain.toml",
        ".codex/config.toml",
        "docs/86_codex_cloud_environment_setup.md",
        "docs/87_secret_and_network_policy.md",
        "scripts/check_codex_cloud_env_static.py",
    ]:
        if term not in bootstrap:
            fail(f"check_bootstrap_consistency.sh missing Step16 term: {term}")
    for rel in ["README.md", "AGENTS.md", "scripts/README.md", "docs/53_ci_commands.md", "docs/80_codex_execution_checklist.md"]:
        text = read_text(rel)
        if "Step16" not in text and "canonical" not in text:
            fail(f"{rel} must mention Step16/canonical")


def main() -> int:
    check_required_files()
    check_rust_toolchain()
    check_codex_config()
    check_docs()
    check_scripts()
    check_workflows_and_docs_wiring()
    print("Codex Cloud / CI environment static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
