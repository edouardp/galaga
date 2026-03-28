#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/publish-guard.sh"

BUMP_TYPE="${1:?Usage: $0 <patch|minor|major>}"

# --- Read current version ---
CURRENT=$(grep '^version' "$ROOT/packages/galaga/pyproject.toml" | head -1 | sed 's/.*"\(.*\)"/\1/')
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case "$BUMP_TYPE" in
    patch) NEW="$MAJOR.$MINOR.$((PATCH + 1))" ;;
    minor) NEW="$MAJOR.$((MINOR + 1)).0" ;;
    major) NEW="$((MAJOR + 1)).0.0" ;;
    *) echo "ERROR: bump type must be patch, minor, or major" >&2; exit 1 ;;
esac

echo "==> Bumping $CURRENT -> $NEW"

# --- Update versions in both pyproject.toml files ---
sed -i '' "s/^version = \"$CURRENT\"/version = \"$NEW\"/" \
    "$ROOT/packages/galaga/pyproject.toml" \
    "$ROOT/packages/galaga_marimo/pyproject.toml"

# --- Update galaga dep pin in galaga-marimo ---
sed -i '' "s/\"galaga>=.*\"/\"galaga>=$NEW\"/" \
    "$ROOT/packages/galaga_marimo/pyproject.toml"

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

echo "==> Running galaga-marimo tests (Python 3.14)"
TMPVENV=$(mktemp -d)/release-test
uv venv "$TMPVENV" --python 3.14
uv pip install --python "$TMPVENV/bin/python" -e packages/galaga -e packages/galaga_marimo pytest
"$TMPVENV/bin/pytest" packages/galaga_marimo/tests/ -v
rm -rf "$TMPVENV"

# --- Build + check ---
echo "==> Building"
rm -rf dist/ packages/galaga_marimo/dist/
cd packages/galaga && uv build
cd "$ROOT/packages/galaga_marimo" && uv build
cd "$ROOT"

echo "==> Twine check"
uvx twine check dist/galaga-*
uvx twine check packages/galaga_marimo/dist/galaga_marimo-*

# --- Publish ---
echo "==> Publishing galaga"
uv publish --keyring-provider subprocess --username __token__ dist/galaga-*

echo "==> Publishing galaga-marimo"
uv publish --keyring-provider subprocess --username __token__ packages/galaga_marimo/dist/galaga_marimo-*

# --- Tag + push + release ---
echo "==> Tagging v$NEW"
git push
git tag "v$NEW"
git push origin "v$NEW"

echo "==> Creating GitHub release"
gh release create "v$NEW" --title "v$NEW" --notes-file CHANGELOG.md

echo "==> Released v$NEW 🎉"
