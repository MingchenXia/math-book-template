#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
missing=0
backend=$(python3 -c 'import json; print(json.load(open("bookflow.json"))["bibliography_backend"])')
texengine=$(python3 -c 'import json; print(json.load(open("bookflow.json"))["engine"])')
for tool in python3 git make latexmk "$texengine" "$backend" makeindex pdfinfo pdftotext pdftoppm pdfseparate pdfunite; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing dependency: $tool" >&2
    missing=1
  fi
done
if command -v "$backend" >/dev/null 2>&1 && ! "$backend" --version >/dev/null 2>&1; then
  echo "Bibliography backend cannot execute: $backend" >&2
  missing=1
fi
for package in biblatex.sty cleveref.sty lmodern.sty; do
  if ! command -v kpsewhich >/dev/null 2>&1 || ! kpsewhich "$package" >/dev/null 2>&1; then
    echo "Missing TeX package: $package" >&2
    missing=1
  fi
done
if [ "$missing" = 1 ]; then
  echo 'Use Codespaces / Dev Containers or see docs/environment.md.' >&2
  exit 1
fi
if command -v codex >/dev/null 2>&1; then
  codex --version
else
  echo 'Book builds are available. To run agents, install @openai/codex@0.157.1 and authenticate.'
fi
echo 'TeX and workflow dependencies are ready.'
