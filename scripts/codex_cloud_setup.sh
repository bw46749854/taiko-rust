#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

run_static=true
for arg in "$@"; do
  case "$arg" in
    --skip-static)
      run_static=false
      ;;
    -h|--help)
      cat <<'HELP'
Usage: scripts/codex_cloud_setup.sh [--skip-static]

Provision a Codex Cloud / CI container for the OpenTaiko Phase1 loop package.
The script intentionally performs setup-only network work, then leaves runtime
verification to scripts/run_rust_preflight.sh.
HELP
      exit 0
      ;;
    *)
      echo "unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

section() {
  printf '\n==> %s\n' "$1"
}

section "Repository root"
pwd

section "Rust toolchain contract"
if [ ! -f rust-toolchain.toml ]; then
  echo "missing rust-toolchain.toml" >&2
  exit 1
fi
rust_channel=$(awk -F'"' '/^[[:space:]]*channel[[:space:]]*=/ {print $2; exit}' rust-toolchain.toml)
if [ -z "${rust_channel:-}" ]; then
  echo "rust-toolchain.toml must declare [toolchain].channel" >&2
  exit 1
fi
echo "channel=${rust_channel}"

section "Install rustup if needed"
if ! command -v rustup >/dev/null 2>&1; then
  echo "rustup not found; installing rustup with minimal profile"
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain none
  # shellcheck disable=SC1091
  source "$HOME/.cargo/env"
fi

if ! command -v rustup >/dev/null 2>&1; then
  echo "rustup installation failed or rustup is not on PATH" >&2
  exit 1
fi

section "Install pinned Rust toolchain"
rustup toolchain install "$rust_channel" --profile minimal --component rustfmt --component clippy
rustup default "$rust_channel"
rustc --version
cargo --version
cargo fmt --version
cargo clippy --version

section "Static environment validation"
if [ "$run_static" = true ]; then
  scripts/check_codex_cloud_env_static.py
  scripts/check_bootstrap_consistency.sh
else
  echo "skipped by --skip-static"
fi

section "Setup complete"
echo "Run scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest for runtime evidence."
