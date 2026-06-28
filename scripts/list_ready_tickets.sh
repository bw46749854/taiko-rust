#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
grep -R "^Status: Ready" -n .loop/tickets | sed 's#^#/#'
