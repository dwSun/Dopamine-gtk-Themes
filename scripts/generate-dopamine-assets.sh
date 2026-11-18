#!/usr/bin/env bash
# Compatibility shim.
#
# The dopamine variants used to be "generated" by copying the upstream blue
# assets and only swapping SVGs/gtkrc/thumbnails, which left their GTK entry
# focus rings bright blue (#1A73E8) while the rest of the theme was warm.
#
# All variants are now recoloured by scripts/generate-theme-assets.py, which
# reads the accents straight from src/_sass/_theme-palettes.scss. This wrapper
# is kept so existing docs/commands keep working.
set -euo pipefail
exec python3 "$(cd "$(dirname "$0")" && pwd)/generate-theme-assets.py" "$@"
