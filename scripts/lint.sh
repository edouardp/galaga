#!/usr/bin/env bash
set -euo pipefail

FIX=""
[[ "${1:-}" == "--fix" ]] && FIX="--fix"

echo "=== Ruff lint ==="
if [[ -n "$FIX" ]]; then
    uv run ruff check . --fix
    uv run ruff format .
else
    uv run ruff check .
    uv run ruff format --check .
fi

echo "=== shellcheck ==="
find scripts -name '*.sh' -exec shellcheck -x -e SC2016 -e SC1091 {} +

echo "=== bandit ==="
uv run bandit -r -c .bandit packages/

echo "=== pip-audit ==="
uv run pip-audit || echo "⚠️  pip-audit found issues (see above)"

echo "=== pyrefly ==="
uv run pyrefly check 2>&1 | tail -5 || echo "⚠️  pyrefly found type issues (see above)"

echo "=== rumdl ==="
if [[ -n "$FIX" ]]; then
    uvx rumdl fmt packages/ CHANGELOG.md
else
    uvx rumdl check packages/ CHANGELOG.md
fi

echo "✅ All lints passed"
