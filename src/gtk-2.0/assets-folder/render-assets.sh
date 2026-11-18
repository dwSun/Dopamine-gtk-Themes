#!/usr/bin/env bash
# Compatibility shim.
#
# These helpers used to hold their own hard-coded per-theme accent lists (and
# needed inkscape/rendersvg). Both drifted from src/_sass/_theme-palettes.scss.
# All assets are now produced by one generator that reads the palette directly.
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
while [[ ! -f "$REPO_DIR/scripts/generate-theme-assets.py" && "$REPO_DIR" != "/" ]]; do
  REPO_DIR="$(dirname "$REPO_DIR")"
done
exec python3 "$REPO_DIR/scripts/generate-theme-assets.py" "$@"
