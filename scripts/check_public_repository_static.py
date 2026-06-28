#!/usr/bin/env python3
"""Static public-repository readiness check for OPS-0003."""
from __future__ import annotations

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
    "LICENSE",
    "NOTICE.md",
    "THIRD_PARTY_NOTICES.md",
    "SECURITY.md",
    "docs/97_public_repository_hardening.md",
    "operations/public_repository_policy.toml",
    "scripts/check_public_repository_static.py",
    ".github/dependabot.yml",
]

REQUIRED_TERMS = {
    "NOTICE.md": ["OpenTaiko", "does not include", "GitHub Actions", "OPENAI_API_KEY"],
    "THIRD_PARTY_NOTICES.md": ["OpenTaiko", "does not contain copied", "User-selected assets"],
    "SECURITY.md": ["Do not commit secrets", "pull_request_target", "block", "OPENAI_API_KEY"],
    "docs/97_public_repository_hardening.md": [
        "Status: canonical",
        "Public Repository Hardening",
        "operations/public_repository_policy.toml",
        "scripts/check_public_repository_static.py",
        "pull_request_target is forbidden",
        "GitHub Actions is a verifier",
        "GATE-OPS-0000",
    ],
    "operations/public_repository_policy.toml": [
        "status = \"canonical\"",
        "openai_api_key_required = false",
        "github_actions_ai_worker_allowed = false",
        "pull_request_target_allowed = false",
        "scripts/check_public_repository_static.py",
    ],
    ".github/pull_request_template.md": ["Public repository safety", "No secrets", "No private Drive", "No AI worker in GitHub Actions"],
    "README.md": ["OPS-0003", "Public repository hardening", "GitHub Actions remains a verifier"],
    "AGENTS.md": ["OPS-0003", "Public repository hardening", "Do not add `OPENAI_API_KEY`"],
    "docs/02_document_index.md": ["docs/97_public_repository_hardening.md", "operations/public_repository_policy.toml", "scripts/check_public_repository_static.py"],
    "scripts/ci_local_equivalent.sh": ["scripts/check_public_repository_static.py"],
    "scripts/check_bootstrap_consistency.sh": ["docs/97_public_repository_hardening.md", "scripts/check_public_repository_static.py"],
}

FORBIDDEN_WORKFLOW_TERMS = [
    "pull_request_target",
    "openai/codex-action@v1",
    "secrets.OPENAI_API_KEY",
    "secrets.CODEX_API_KEY",
    "OPENAI_API_KEY:",
    "CODEX_API_KEY:",
]

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
]

FORBIDDEN_SUFFIXES = {".mp3", ".wav", ".ogg", ".flac", ".mp4", ".avi", ".osz"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_IMAGE_PREFIXES = ("docs/", "reports/", "fixtures/synthetic/")
ALLOWED_CHART_PREFIXES = ("fixtures/synthetic/",)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check_required_files() -> None:
    for item in REQUIRED_FILES:
        if not (ROOT / item).is_file():
            fail(f"missing required file: {item}")
    mode = (ROOT / "scripts/check_public_repository_static.py").stat().st_mode
    if not (mode & stat.S_IXUSR):
        fail("scripts/check_public_repository_static.py must be executable")


def check_required_terms() -> None:
    for path, terms in REQUIRED_TERMS.items():
        text = read(path)
        for term in terms:
            if term not in text:
                fail(f"{path} missing required term: {term}")


def check_policy_toml() -> None:
    if tomllib is None:
        return
    data = tomllib.loads(read("operations/public_repository_policy.toml"))
    required_false = [
        "openai_api_key_required",
        "codex_api_key_required",
        "github_actions_ai_worker_allowed",
        "openai_codex_action_allowed",
        "pull_request_target_allowed",
        "privileged_workflow_may_execute_pr_head",
    ]
    for key in required_false:
        if data.get(key) is not False:
            fail(f"operations/public_repository_policy.toml must set {key} = false")
    if data.get("required_static_check") != "scripts/check_public_repository_static.py":
        fail("public policy required_static_check mismatch")


def check_workflows() -> None:
    workflow_dir = ROOT / ".github/workflows"
    for path in sorted(workflow_dir.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        path_rel = rel(path)
        for term in FORBIDDEN_WORKFLOW_TERMS:
            if term in text:
                fail(f"{path_rel} contains forbidden workflow term: {term}")
        if "permissions:" not in text:
            fail(f"{path_rel} must define explicit permissions")
        if "actions/checkout@" in text and "persist-credentials: false" not in text and "loop-controller.yml" not in path_rel:
            fail(f"{path_rel} checkout must set persist-credentials: false for public-readiness")
    controller = read(".github/workflows/loop-controller.yml")
    for term in ["contents: write", "pull-requests: write", "actions: read", "checks: read"]:
        if term not in controller:
            fail(f"loop-controller permissions missing: {term}")


def check_repository_paths() -> None:
    if (ROOT / "source_context").exists():
        fail("source_context/ must not exist in public-ready package")
    if (ROOT / ".external_assets").exists():
        fail(".external_assets/ must not be committed")
    if list(ROOT.glob("STEP*.md")):
        fail("root-level STEP*.md files must not exist")
    for forbidden in [".env", ".env.local"]:
        if (ROOT / forbidden).exists():
            fail(f"forbidden path exists: {forbidden}")


def check_no_secret_literals() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        path_rel = rel(path)
        if path_rel.startswith(".git/") or path_rel.startswith("target/"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"possible secret literal in {path_rel}: {pattern.pattern}")


def check_no_asset_payloads() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        path_rel = rel(path)
        suffix = path.suffix.lower()
        if suffix in FORBIDDEN_SUFFIXES:
            fail(f"forbidden binary/media asset payload: {path_rel}")
        if suffix in IMAGE_SUFFIXES and not path_rel.startswith(ALLOWED_IMAGE_PREFIXES):
            fail(f"image asset outside allowed generated/docs paths: {path_rel}")
        if suffix == ".tja" and not path_rel.startswith(ALLOWED_CHART_PREFIXES):
            fail(f"chart asset outside synthetic fixtures: {path_rel}")


def main() -> int:
    check_required_files()
    check_required_terms()
    check_policy_toml()
    check_workflows()
    check_repository_paths()
    check_no_secret_literals()
    check_no_asset_payloads()
    print("public repository static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
