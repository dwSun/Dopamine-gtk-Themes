#!/bin/bash
#
# Set this theme as the active GTK 3/4 theme for applications that read
# ~/.config/gtk-3.0 and ~/.config/gtk-4.0 directly (e.g. libadwaita apps).
#
# Run from inside the installed theme directory, e.g.:
#   ~/.themes/Dopamine-nord-Dark/gtk-set.sh

set -euo pipefail

THEME_DIR="$(cd "$(dirname "$0")" && pwd)"
THEME_NAME="$(basename "$THEME_DIR")"

GTK3_DIR="${HOME}/.config/gtk-3.0"
GTK4_DIR="${HOME}/.config/gtk-4.0"

backup_or_remove() {
  local target="$1"
  if [[ -L "$target" ]]; then
    rm -f "$target"
  elif [[ -e "$target" ]]; then
    local backup="${target}.bak.$(date +%s)"
    mv -f "$target" "$backup"
    echo "Backed up existing file: $target -> $backup"
  fi
}

link_theme_file() {
  local src="$1"
  local dst="$2"

  if [[ ! -e "$src" ]]; then
    echo "WARNING: source file does not exist, skipping: $src"
    return
  fi

  backup_or_remove "$dst"
  ln -sfn "$src" "$dst"
}

mkdir -p "$GTK3_DIR" "$GTK4_DIR"

echo "Setting GTK theme to: $THEME_NAME"

# GTK 3
link_theme_file "$THEME_DIR/gtk-3.0/gtk.css"      "$GTK3_DIR/gtk.css"
link_theme_file "$THEME_DIR/gtk-3.0/gtk-dark.css" "$GTK3_DIR/gtk-dark.css"
link_theme_file "$THEME_DIR/gtk-3.0/assets"       "$GTK3_DIR/assets"

# GTK 4
link_theme_file "$THEME_DIR/gtk-4.0/gtk.css"      "$GTK4_DIR/gtk.css"
link_theme_file "$THEME_DIR/gtk-4.0/gtk-dark.css" "$GTK4_DIR/gtk-dark.css"
link_theme_file "$THEME_DIR/gtk-4.0/assets"       "$GTK4_DIR/assets"

echo "Done. Restart GTK applications to apply the theme."
