#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/doctor.sh
python3 scripts/bookflow.py sync
python3 scripts/bookflow.py audit
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  git config core.hooksPath .githooks
fi
echo 'Setup complete. Authentication is per user: codex login; never store credentials in this repository.'
