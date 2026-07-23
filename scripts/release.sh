#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/publish-guard.sh"

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <patch|minor|major>" >&2
    echo "       $0 --version <X.Y.Z|X.Y.ZaN|X.Y.ZbN|X.Y.ZrcN>" >&2
    exit 2
fi

# --- Read current version ---
CURRENT=$(grep '^version' "$ROOT/packages/galaga/pyproject.toml" | head -1 | sed 's/.*"\(.*\)"/\1/')
read -r NEW RELEASE_KIND < <(python3 "$SCRIPT_DIR/release_version.py" "$CURRENT" "$@")

echo "==> Bumping $CURRENT -> $NEW"

# --- Update versions in the jointly released packages ---
sed -i '' "s/^version = \"$CURRENT\"/version = \"$NEW\"/" \
    "$ROOT/packages/galaga/pyproject.toml" \
    "$ROOT/packages/galaga_marimo/pyproject.toml" \
    "$ROOT/packages/galaga_matrix/pyproject.toml"

# --- Update galaga dependency floors in every companion package ---
sed -i '' "s/\"galaga>=.*\"/\"galaga>=$NEW\"/" \
    "$ROOT/packages/galaga_marimo/pyproject.toml" \
    "$ROOT/packages/galaga_matrix/pyproject.toml" \
    "$ROOT/packages/galaga_mermaid/pyproject.toml"

# --- Regenerate lockfile to reflect version changes ---
uv lock

# --- Update CHANGELOG ---
DATE=$(date +%Y-%m-%d)
CHANGELOG="$ROOT/CHANGELOG.md"
TMPFILE=$(mktemp)
cat > "$TMPFILE" <<EOF
# Changelog

## $NEW ($DATE)

<!-- Fill in release notes, then save and close -->

EOF
# Append old content minus the first "# Changelog" line
tail -n +2 "$CHANGELOG" >> "$TMPFILE"
cp "$TMPFILE" "$CHANGELOG"
rm "$TMPFILE"

# --- Open editor for changelog ---
${EDITOR:-vim} "$CHANGELOG"

# --- Fix markdown lint ---
uvx rumdl fmt "$CHANGELOG"

# --- Abort if changelog still has placeholder ---
if grep -q '<!-- Fill in release notes' "$CHANGELOG"; then
    echo "ERROR: Changelog not edited. Aborting release." >&2
    git checkout "$CHANGELOG"
    exit 1
fi

# --- Commit ---
cd "$ROOT"
git add -A
git commit -m "Release v$NEW"

# --- Tests ---
echo "==> Running galaga tests"
uv run pytest packages/galaga/tests/ -v

echo "==> Running galaga-matrix tests"
PYTHONPATH=.:packages/galaga_matrix uv run pytest packages/galaga_matrix/tests/ -v

echo "==> Running galaga-marimo tests (Python 3.14)"
TMPVENV=$(mktemp -d)/release-test
uv venv "$TMPVENV" --python 3.14
uv pip install --python "$TMPVENV/bin/python" -e packages/galaga -e packages/galaga_marimo pytest
"$TMPVENV/bin/pytest" packages/galaga_marimo/tests/ -v
rm -rf "$TMPVENV"

# --- Build + check ---
echo "==> Building"
rm -rf dist/ packages/galaga_marimo/dist/ packages/galaga_matrix/dist/
cd packages/galaga && uv build
cd "$ROOT/packages/galaga_marimo" && uv build
cd "$ROOT/packages/galaga_matrix" && uv build
cd "$ROOT"

echo "==> Twine check"
uvx twine check dist/galaga-*
uvx twine check packages/galaga_marimo/dist/galaga_marimo-*
uvx twine check packages/galaga_matrix/dist/galaga_matrix-*

# --- Publish ---
echo "==> Fetching PyPI token (one password prompt)..."
UV_PUBLISH_TOKEN=$(keyring get https://upload.pypi.org/legacy/ __token__)
export UV_PUBLISH_TOKEN

echo "==> Publishing galaga"
uv publish dist/galaga-*

echo "==> Publishing galaga-marimo"
uv publish packages/galaga_marimo/dist/galaga_marimo-*

echo "==> Publishing galaga-matrix"
uv publish packages/galaga_matrix/dist/galaga_matrix-*

# --- Tag + push + release ---
echo "==> Tagging v$NEW"
git push
git tag "v$NEW"
git push origin "v$NEW"

echo "==> Creating GitHub release"
GH_RELEASE_ARGS=()
if [[ "$RELEASE_KIND" == "prerelease" ]]; then
    GH_RELEASE_ARGS+=(--prerelease)
fi
gh release create "v$NEW" --title "v$NEW" --notes-file CHANGELOG.md "${GH_RELEASE_ARGS[@]}"

echo "==> Released v$NEW 🎉"
