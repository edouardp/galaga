#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$SCRIPT_DIR/.."
PKG="$ROOT/packages/galaga"
DIST="$ROOT/dist"

PUBLISH_URL="https://upload.pypi.org/legacy/"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --test) PUBLISH_URL="https://test.pypi.org/legacy/"; shift ;;
        *) echo "Usage: $0 [--test]"; exit 1 ;;
    esac
done

echo "==> Running tests"
uv run pytest "$PKG/tests/" -v

echo "==> Cleaning old builds"
rm -rf "$DIST"/galaga-*

echo "==> Building galaga"
cd "$PKG" && uv build

echo "==> Checking with twine"
uvx twine check "$DIST"/galaga-*

echo "==> Publishing to $PUBLISH_URL"
uv publish --publish-url "$PUBLISH_URL" --keyring-provider subprocess --username __token__ "$DIST"/galaga-*

echo "==> Done"
