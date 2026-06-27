#!/usr/bin/env python3
"""Static validation for canonical Phase1 gameplay loop start."""
from __future__ import annotations

import json
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/95_phase1_gameplay_loop_start.md",
    "operations/phase1_gameplay_loop_policy.toml",
    "prompts/72_phase1_gameplay_ticket_runner.md",
    "reports/phase1_gameplay_loop/README.md",
    "scripts/render_phase1_gameplay_ticket_prompt.py",
    "scripts/check_phase1_gameplay_start_static.py",
    ".github/workflows/phase1-gameplay-entry.yml",
    "operations/phase1_feature_ticket_manifest.toml",
    ".loop/tickets/TKT-0005.md",
]

REQUIRED_TERMS = {
    "docs/95_phase1_gameplay_loop_start.md": [
        "Status: canonical",
        "TKT-0005",
        "GATE-0090",
        "scripts/render_phase1_gameplay_ticket_prompt.py",
        "force-preview",
        "OPENAI_API_KEY",
        "QA verdict",
    ],
    "operations/phase1_gameplay_loop_policy.toml": [
        "status = \"canonical\"",
        "first_gameplay_ticket = \"TKT-0005\"",
        "phase1_gameplay_allowed_in_bootstrap = true",
        "api_key_required = false",
        "github_actions_may_call_ai = false",
    ],
    "prompts/72_phase1_gameplay_ticket_runner.md": [
        "Status: canonical",
        "TKT-0005",
        "Do not start gameplay implementation unless the rendered start packet says `verdict = ready`",
        "Do not write `reports/qa/*.json`",
        "OPENAI_API_KEY",
    ],
    "reports/phase1_gameplay_loop/README.md": [
        "Status: canonical",
        "phase1_gameplay_start.json",
        "phase1_ticket_prompt.md",
    ],
    ".github/workflows/phase1-gameplay-entry.yml": [
        "phase1-gameplay-entry",
        "scripts/check_phase1_gameplay_start_static.py",
        "scripts/check_phase1_entry_state_consistency.py",
        "render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run",
        "--force-preview",
    ],
    "scripts/render_phase1_gameplay_ticket_prompt.py": [
        "phase1-gameplay-start/v1",
        "wait_for_phase1_entry_evidence",
        "start_phase1_gameplay_ticket_worker",
        "render_prompt",
        "force-preview",
        "OPENAI_API_KEY",
    ],
    "README.md": [
        "Status: canonical",
                "docs/95_phase1_gameplay_loop_start.md",
        "scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run",
    ],
    "AGENTS.md": [
                "scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run",
        "verdict = ready",
        "TKT-0005",
    ],
    "operations/manifest.md": [
        "Status: canonical",
        "Phase1 Gameplay Loop Start canonical files",
        "docs/95_phase1_gameplay_loop_start.md",
    ],
    "scripts/README.md": [
        "render_phase1_gameplay_ticket_prompt.py",
        "check_phase1_gameplay_start_static.py",
    ],
}

FORBIDDEN_TERMS = [
    "openai/codex-action@v1 as the Phase1 gameplay worker",
    "OPENAI_API_KEY is required for Phase1 gameplay",
]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing: {rel}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")

    for rel, terms in REQUIRED_TERMS.items():
        text = read(rel)
        for term in terms:
            if term not in text:
                fail(f"{rel} missing required term: {term}")
        for term in FORBIDDEN_TERMS:
            if term in text:
                fail(f"{rel} contains forbidden term: {term}")

    mode = (ROOT / "scripts/render_phase1_gameplay_ticket_prompt.py").stat().st_mode
    if mode & stat.S_IXUSR == 0:
        fail("scripts/render_phase1_gameplay_ticket_prompt.py must be executable")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/render_phase1_gameplay_ticket_prompt.py"),
            "--ticket",
            "TKT-0005",
            "--dry-run",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail(f"renderer dry-run failed: {result.stderr}")
    try:
        packet = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"renderer did not emit JSON: {exc}")
    if packet.get("ticket_id") != "TKT-0005":
        fail("renderer did not select TKT-0005")
    if packet.get("verdict") == "ready":
        if packet.get("next_action") != "start_phase1_gameplay_ticket_worker":
            fail("ready verdict must start the gameplay worker")
        if packet.get("missing_prerequisites"):
            fail(f"ready packet must not have missing prerequisites: {packet.get('missing_prerequisites')}")
        if packet.get("ticket_status") != "Ready":
            fail(f"ready packet requires TKT-0005 Ready, got: {packet.get('ticket_status')}")
    elif packet.get("verdict") == "block":
        if packet.get("next_action") != "wait_for_phase1_entry_evidence":
            fail("blocked verdict must wait for Phase1 entry evidence")
        if not packet.get("missing_prerequisites"):
            fail("blocked packet must list missing prerequisites")
    else:
        fail(f"renderer must emit ready or block, got: {packet.get('verdict')}")

    preview = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/render_phase1_gameplay_ticket_prompt.py"),
            "--ticket",
            "TKT-0005",
            "--force-preview",
            "--dry-run",
            "--format",
            "prompt",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if preview.returncode != 0:
        fail(f"renderer force-preview failed: {preview.stderr}")
    for term in ["Phase1 Gameplay Ticket Worker", "TKT-0005", "Required commands"]:
        if term not in preview.stdout:
            fail(f"preview prompt missing term: {term}")

    ci = read("scripts/ci_local_equivalent.sh")
    if "scripts/check_phase1_gameplay_start_static.py" not in ci:
        fail("ci_local_equivalent.sh must run check_phase1_gameplay_start_static.py")
    bootstrap = read("scripts/check_bootstrap_consistency.sh")
    for term in [
        "docs/95_phase1_gameplay_loop_start.md",
        "operations/phase1_gameplay_loop_policy.toml",
        "prompts/72_phase1_gameplay_ticket_runner.md",
        "scripts/render_phase1_gameplay_ticket_prompt.py",
        "scripts/check_phase1_gameplay_start_static.py",
        "scripts/check_phase1_entry_state_consistency.py",
    ]:
        if term not in bootstrap:
            fail(f"check_bootstrap_consistency.sh missing Phase1 gameplay start term: {term}")

    print("phase1 gameplay start static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
