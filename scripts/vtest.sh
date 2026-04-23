#!/usr/bin/env bash
# vtest.sh — run pytest inside the project's .venv.
#
# Usage: scripts/vtest.sh [--tail=N] [--grep=PATTERN] [pytest-args...]
#
# --tail=N       Show only the last N lines of output (replaces `| tail -n N`).
# --grep=PATTERN Show only lines matching PATTERN (replaces `| grep PATTERN`).
#
# Remaining arguments are forwarded to pytest. Exit code is pytest's.

set -euo pipefail

here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(dirname -- "$here")"

venv="$root/.venv"
if [[ ! -d "$venv" ]]; then
    echo "vtest.sh: no virtualenv at $venv" >&2
    echo "vtest.sh: create one with: python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'" >&2
    exit 2
fi

# shellcheck disable=SC1091
source "$venv/bin/activate"

tail_n=""
grep_pat=""
pytest_args=()

for arg in "$@"; do
    case "$arg" in
        --tail=*)
            tail_n="${arg#--tail=}"
            ;;
        --grep=*)
            grep_pat="${arg#--grep=}"
            ;;
        *)
            pytest_args+=("$arg")
            ;;
    esac
done

# Translate pytest's "no tests collected" (exit 5) to success, so an empty
# test suite is not a CI failure during bootstrap.
normalize_status() {
    if [[ "$1" -eq 5 ]]; then
        echo 0
    else
        echo "$1"
    fi
}

if [[ -z "$tail_n" && -z "$grep_pat" ]]; then
    set +e
    pytest ${pytest_args[@]+"${pytest_args[@]}"}
    status=$?
    set -e
    exit "$(normalize_status "$status")"
fi

tmp="$(mktemp -t vtest.XXXXXX)"
trap 'rm -f "$tmp"' EXIT

set +e
pytest ${pytest_args[@]+"${pytest_args[@]}"} >"$tmp" 2>&1
status=$?
set -e
status="$(normalize_status "$status")"

if [[ -n "$grep_pat" ]]; then
    filtered="$(mktemp -t vtest-grep.XXXXXX)"
    trap 'rm -f "$tmp" "$filtered"' EXIT
    grep -E -- "$grep_pat" "$tmp" >"$filtered" || true
    src="$filtered"
else
    src="$tmp"
fi

if [[ -n "$tail_n" ]]; then
    tail -n "$tail_n" "$src"
else
    cat "$src"
fi

exit "$status"
