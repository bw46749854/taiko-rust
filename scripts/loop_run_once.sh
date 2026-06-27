#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mode="plan"
format="json"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      mode="$2"
      shift 2
      ;;
    --format)
      format="$2"
      shift 2
      ;;
    -h|--help)
      cat <<'HELP'
Usage: scripts/loop_run_once.sh [--mode plan|apply] [--format json|markdown]

Runs the Step17 controller once. plan mode has no side effects. apply mode
writes controller artifacts under reports/loop/<run_id>/.
HELP
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [ "$mode" != "plan" ] && [ "$mode" != "apply" ]; then
  echo "--mode must be plan or apply" >&2
  exit 2
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "cargo is required to execute taiko_cli loop run-once; run scripts/ci_local_equivalent.sh --static-only for no-Rust validation" >&2
  exit 1
fi

cargo run -p taiko_cli --bin taiko_cli -- loop run-once --mode "$mode" --format "$format"
