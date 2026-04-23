#!/usr/bin/env bash
# vlint.sh — run ruff inside the project's .venv, forwarding all arguments.
#
# Usage: scripts/vlint.sh [ruff-args...]
# Default (no args): `ruff check .`

set -euo pipefail

here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(dirname -- "$here")"

venv="$root/.venv"
if [[ ! -d "$venv" ]]; then
    echo "vlint.sh: no virtualenv at $venv" >&2
    echo "vlint.sh: create one with: python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'" >&2
    exit 2
fi

# shellcheck disable=SC1091
source "$venv/bin/activate"

cd -- "$root"

if [[ $# -eq 0 ]]; then
    exec ruff check .
fi

exec ruff "$@"
