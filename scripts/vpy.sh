#!/usr/bin/env bash
# vpy.sh — run Python inside the project's .venv, forwarding all arguments.
#
# Usage: scripts/vpy.sh [python-args...]

set -euo pipefail

here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(dirname -- "$here")"

venv="$root/.venv"
if [[ ! -d "$venv" ]]; then
    echo "vpy.sh: no virtualenv at $venv" >&2
    echo "vpy.sh: create one with: python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'" >&2
    exit 2
fi

# shellcheck disable=SC1091
source "$venv/bin/activate"

exec python "$@"
