#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
native=1
for tool in python3 make latexmk codex; do
  command -v "$tool" >/dev/null 2>&1 || native=0
done
if [ "$native" = 1 ] && ! bash scripts/doctor.sh >/dev/null 2>&1; then
  native=0
fi
if [ "$native" = 1 ]; then
  bash scripts/setup.sh
  make build
elif command -v docker >/dev/null 2>&1; then
  docker build -t math-book-template-env .devcontainer
  docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp/book-home -v "$PWD:/workspace" -w /workspace math-book-template-env bash -c 'set -euo pipefail; mkdir -p "$HOME"; bash scripts/setup.sh; make build'
else
  echo 'Open this repository in GitHub Codespaces, or install Docker and run bash start.sh again.' >&2
  exit 1
fi
echo 'Environment ready. PDF: build/pdf/main.pdf. Run codex login, then make review.'
