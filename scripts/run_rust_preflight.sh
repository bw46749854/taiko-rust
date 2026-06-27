#!/usr/bin/env bash
set -u -o pipefail

cd "$(dirname "$0")/.."

scope="current-package"
out_dir="reports/preflight/latest"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --scope)
      [ "$#" -ge 2 ] || { echo "--scope requires a value" >&2; exit 2; }
      scope="$2"
      shift 2
      ;;
    --out)
      [ "$#" -ge 2 ] || { echo "--out requires a value" >&2; exit 2; }
      out_dir="$2"
      shift 2
      ;;
    --help|-h)
      cat <<'EOF'
usage: scripts/run_rust_preflight.sh [--scope loop-cli|current-package] [--out reports/preflight/latest]

Runs Rust-enabled dynamic verification and writes JSON/Markdown evidence.
EOF
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

case "$scope" in
  loop-cli|current-package) ;;
  *) echo "unsupported --scope: $scope" >&2; exit 2 ;;
esac

mkdir -p "$out_dir/logs" "$out_dir/generated"
: > "$out_dir/commands.tsv"

run_cmd() {
  local id="$1"
  local phase="$2"
  local command="$3"
  local stdout_log="$out_dir/logs/${id}.stdout.log"
  local stderr_log="$out_dir/logs/${id}.stderr.log"
  local start_ms end_ms duration_ms exit_code status

  printf '==> [%s] %s\n' "$id" "$command" >&2
  start_ms=$(python3 - <<'PY'
import time
print(int(time.time() * 1000))
PY
)
  bash -lc "$command" >"$stdout_log" 2>"$stderr_log"
  exit_code=$?
  end_ms=$(python3 - <<'PY'
import time
print(int(time.time() * 1000))
PY
)
  duration_ms=$((end_ms - start_ms))
  if [ "$exit_code" -eq 0 ]; then
    status="pass"
  else
    status="fail"
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$id" "$phase" "$command" "$status" "$exit_code" "$duration_ms" "$stdout_log" "$stderr_log" \
    >> "$out_dir/commands.tsv"
}

run_cmd cargo_version environment "cargo --version"
run_cmd rustc_version environment "rustc --version"
run_cmd cargo_fmt cargo "cargo fmt --all --check"
run_cmd cargo_clippy cargo "cargo clippy --workspace --all-targets -- -D warnings"
run_cmd cargo_test cargo "cargo test --workspace"
run_cmd rust_workspace_static static "scripts/check_rust_workspace_static.py"
run_cmd loop_inspect_tickets loop_cli "cargo run -p taiko_cli --bin taiko_cli -- loop inspect tickets --format json"
run_cmd loop_inspect_gates loop_cli "cargo run -p taiko_cli --bin taiko_cli -- loop inspect gates --format json"
run_cmd loop_next loop_cli "cargo run -p taiko_cli --bin taiko_cli -- loop next --format json"
run_cmd loop_gate_0000 loop_cli "cargo run -p taiko_cli --bin taiko_cli -- loop gate GATE-0000 --dry-run --format json"
run_cmd loop_report_status loop_cli "cargo run -p taiko_cli --bin taiko_cli -- loop report status --format json"

if [ "$scope" = "current-package" ]; then
  run_cmd fixture_validate fixture "cargo run -p taiko_cli --bin taiko_cli -- fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --format json"
  run_cmd fixture_inspect fixture "cargo run -p taiko_cli --bin taiko_cli -- fixture inspect fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --format json"
  run_cmd headless_autoplay headless "cargo run -p taiko_cli --bin taiko_cli -- headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json"
  run_cmd timing_analyze timing "cargo run -p taiko_cli --bin taiko_cli -- timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json"
  run_cmd failure_ingest failure_feedback "cargo run -p taiko_cli --bin taiko_cli -- loop failure ingest reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json"
  run_cmd ticket_propose failure_feedback "cargo run -p taiko_cli --bin taiko_cli -- loop ticket propose --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json"
  run_cmd ticket_validate failure_feedback "cargo run -p taiko_cli --bin taiko_cli -- loop ticket validate .loop/tickets/TKT-0040.md --format json"
  run_cmd qa_run qa "mkdir -p '$out_dir/generated' && cargo run -p taiko_cli --bin taiko_cli -- qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json > '$out_dir/generated/phase1_loop.qa.json'"
  run_cmd qa_verdict qa "cargo run -p taiko_cli --bin taiko_cli -- qa verdict --input '$out_dir/generated/phase1_loop.qa.json' --format json"
  run_cmd phase1_feature_validate phase1 "cargo run -p taiko_cli --bin taiko_cli -- phase1 feature validate --manifest operations/phase1_feature_ticket_manifest.toml --format json"
  run_cmd phase1_feature_plan phase1 "cargo run -p taiko_cli --bin taiko_cli -- phase1 feature plan --manifest operations/phase1_feature_ticket_manifest.toml --format json"
fi

python3 - "$scope" "$out_dir" <<'PY'
from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

scope = sys.argv[1]
out_dir = Path(sys.argv[2])
commands_path = out_dir / 'commands.tsv'
commands = []

for line in commands_path.read_text(encoding='utf-8').splitlines():
    command_id, phase, command, status, exit_code, duration_ms, stdout_log, stderr_log = line.split('\t')
    commands.append({
        'id': command_id,
        'phase': phase,
        'command': command,
        'status': status,
        'exit_code': int(exit_code),
        'duration_ms': int(duration_ms),
        'stdout_log': stdout_log,
        'stderr_log': stderr_log,
    })

cargo_ok = next((c['status'] == 'pass' for c in commands if c['id'] == 'cargo_version'), False)
rustc_ok = next((c['status'] == 'pass' for c in commands if c['id'] == 'rustc_version'), False)
failed = [c for c in commands if c['status'] != 'pass']

if not cargo_ok or not rustc_ok:
    verdict = 'block'
elif failed:
    verdict = 'reject'
else:
    verdict = 'pass'

summary = {
    'total': len(commands),
    'passed': sum(1 for c in commands if c['status'] == 'pass'),
    'failed': sum(1 for c in commands if c['status'] == 'fail'),
    'blocked': 1 if verdict == 'block' else 0,
}

def first_line(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        return ''
    for value in p.read_text(encoding='utf-8', errors='replace').splitlines():
        value = value.strip()
        if value:
            return value[:300]
    return ''

try:
    git_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
except Exception:
    git_sha = ''

report = {
    'schema_version': 'rust-preflight.v1',
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'scope': scope,
    'verdict': verdict,
    'summary': summary,
    'environment': {
        'runner_os': platform.platform(),
        'python_version': platform.python_version(),
        'git_sha': git_sha,
        'cargo_version': first_line(next(c['stdout_log'] for c in commands if c['id'] == 'cargo_version')),
        'rustc_version': first_line(next(c['stdout_log'] for c in commands if c['id'] == 'rustc_version')),
    },
    'commands': commands,
    'required_evidence': [
        'rust_preflight_report.json',
        'rust_preflight_report.md',
        'commands.tsv',
        'logs/<command-id>.stdout.log',
        'logs/<command-id>.stderr.log',
    ],
}

(out_dir / 'rust_preflight_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

lines = [
    '# Rust Preflight Report',
    '',
    f'- Schema: `{report["schema_version"]}`',
    f'- Generated UTC: `{report["generated_at_utc"]}`',
    f'- Scope: `{scope}`',
    f'- Verdict: `{verdict}`',
    f'- Summary: {summary["passed"]}/{summary["total"]} passed, {summary["failed"]} failed, {summary["blocked"]} blocked',
    '',
    '## Commands',
    '',
    '| ID | Phase | Status | Exit | Duration ms |',
    '|---|---|---:|---:|---:|',
]
for c in commands:
    lines.append(f'| `{c["id"]}` | `{c["phase"]}` | `{c["status"]}` | {c["exit_code"]} | {c["duration_ms"]} |')
lines += [
    '',
    '## Transition rule',
    '',
]
if verdict == 'pass':
    lines.append('Preflight passed. `TKT-0001` may proceed to detached review and `GATE-0030` evaluation.')
elif verdict == 'block':
    lines.append('Preflight blocked. Fix the Rust-enabled environment before accepting the ticket.')
else:
    lines.append('Preflight rejected. Route the failing command logs through failure feedback and create or select a repair ticket.')

(out_dir / 'rust_preflight_report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps({'verdict': verdict, 'scope': scope, 'summary': summary}, ensure_ascii=False))
PY

scripts/check_runtime_evidence_files.py --path "$out_dir/rust_preflight_report.json" --require-scope "$scope"
report_status=$(python3 - "$out_dir/rust_preflight_report.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding='utf-8'))['verdict'])
PY
)

if [ "$report_status" = "pass" ]; then
  exit 0
fi
exit 1
