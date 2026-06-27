#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if find fixtures/user_selected -type f \( \
  -iname '*.tja' -o -iname '*.ogg' -o -iname '*.wav' -o -iname '*.mp3' -o \
  -iname '*.mp4' -o -iname '*.avi' -o -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \
\) | grep .; then
  echo "user-selected asset payload found under fixtures/user_selected" >&2
  exit 1
fi

echo "no user-selected asset payload found"
