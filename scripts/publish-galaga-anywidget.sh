#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/publish-guard.sh"

PKG="$ROOT/packages/galaga_anywidget"
PUBLISH_URL="https://upload.pypi.org/legacy/"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --test) PUBLISH_URL="https://test.pypi.org/legacy/"; shift ;;
        *) echo "Usage: $0 [--test]"; exit 1 ;;
    esac
done

echo "==> Testing galaga-anywidget with Python 3.11"
TMPVENV=$(mktemp -d)/gaw-publish-test
uv venv "$TMPVENV" --python 3.11
uv pip install --python "$TMPVENV/bin/python" -e "$ROOT/packages/galaga" -e "$PKG" pytest
"$TMPVENV/bin/pytest" "$PKG/tests" -v
rm -rf "$TMPVENV"

echo "==> Building galaga-anywidget"
rm -rf "$PKG/dist"
cd "$ROOT"
uv build --package galaga-anywidget --out-dir "$PKG/dist"

echo "==> Checking with twine"
uvx twine check "$PKG/dist"/galaga_anywidget-*

echo "==> Publishing galaga-anywidget to $PUBLISH_URL"
uv publish --publish-url "$PUBLISH_URL" --keyring-provider subprocess --username __token__ "$PKG/dist"/galaga_anywidget-*
