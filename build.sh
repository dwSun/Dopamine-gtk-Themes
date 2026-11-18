#!/bin/bash

# Build all generated artifacts from source.
# Run this after cloning (and after editing src/_sass/_theme-palettes.scss) before
# running install.sh.

set -ueo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

echo "== Building CSS (GTK3/4, GNOME Shell, Cinnamon)..."
./parse-sass.sh

echo "== Recolouring theme assets..."
# Recolours the upstream blue PNG/SVG assets per palette. This replaces the old
# make-assets.sh + render-assets.sh chain, which needed inkscape/rendersvg and
# silently left the dopamine variants upstream-blue.
python3 scripts/generate-theme-assets.py

echo "== Rendering README previews and palette cards..."
python3 scripts/gen-previews.py --contact-sheet
python3 scripts/gen-palette-cards.py

echo "== done!"
echo "You can now run ./install.sh"
