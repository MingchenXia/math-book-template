#!/usr/bin/env bash
# Run from the checked-out repository, in Codex Cloud's Install script.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "${1:-}" != "--verify-only" ]]; then
  if [[ -n "${1:-}" ]]; then
    echo 'Usage: bash scripts/setup-codex-cloud.sh [--verify-only]' >&2
    exit 2
  fi
  if ! command -v apt-get >/dev/null || ! command -v dpkg-query >/dev/null; then
    echo 'Installation requires Debian/Ubuntu. On a prepared machine use --verify-only.' >&2
    exit 1
  fi
  packages=()
  while IFS= read -r package; do
    [[ -z "$package" ]] || packages+=("$package")
  done < .devcontainer/tex-packages.txt
  needs_install=0
  for package in "${packages[@]}"; do
    if [[ "$(dpkg-query -W -f='${Status}' "$package" 2>/dev/null || true)" != 'install ok installed' ]]; then
      needs_install=1
    fi
  done
  if [[ "$needs_install" == 1 ]]; then
    elevated=()
    if [[ "$(id -u)" != 0 ]]; then
      if ! command -v sudo >/dev/null || ! sudo -n true; then
        echo 'Dependency installation needs root or passwordless sudo in the cloud setup.' >&2
        exit 1
      fi
      elevated=(sudo -n)
    fi
    "${elevated[@]}" apt-get update
    "${elevated[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${packages[@]}"
  fi
fi

# The hosted Codex agent is already provided by the cloud service. Its identity
# is not an authentication token for a nested CLI process.
bash scripts/setup.sh
make test
make check
make build
echo 'Cloud book environment verified. Use the hosted agent; see docs/codex-cloud.md for independent review.'
