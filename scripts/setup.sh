#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/doctor.sh
python3 scripts/bookflow.py sync
python3 scripts/bookflow.py audit
if [ "$(git rev-parse --show-toplevel 2>/dev/null || true)" = "$PWD" ]; then
  git config core.hooksPath .githooks
else
  echo 'No repository at this exact root; setup has not changed any parent repository hooks.'
fi
echo 'Setup complete. Authentication is per user: codex login; never store credentials in this repository.'
