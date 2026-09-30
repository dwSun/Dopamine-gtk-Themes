#!/usr/bin/env bash
# 为 Dopamine Themes 生成/重新生成多巴胺风格主题资源。
# 用法：bash scripts/generate-dopamine-assets.sh
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

declare -A DARK=(
  [candy]=#FF4F9A
  [tangerine]=#FF8A1F
  [minty]=#69F0AE
  [berry]=#FF6F91
  [nebula]=#00E5FF
)
declare -A LIGHT=(
  [candy]=#FFB3E0
  [tangerine]=#FFBC80
  [minty]=#B9F6CA
  [berry]=#FFB3C1
  [nebula]=#80E8FF
)

for theme in candy tangerine minty berry nebula; do
  dark="${DARK[$theme]}"
  light="${LIGHT[$theme]}"

  # GTK3/4 assets SVG & fallback PNG dir
  sed -e "s/#1A73E8/$dark/gI" -e "s/#3281EA/$light/gI" \
      src/gtk/assets.svg > "src/gtk/assets-${theme}.svg"
  rm -rf "src/gtk/assets-${theme}"
  cp -r src/gtk/assets "src/gtk/assets-${theme}"

  # GTK2 SVGs & PNG dirs
  sed -e "s/#1A73E8/$dark/gI" -e "s/#3281EA/$light/gI" \
      src/gtk-2.0/assets-folder/assets.svg > "src/gtk-2.0/assets-folder/assets-${theme}.svg"
  sed -e "s/#1A73E8/$dark/gI" -e "s/#3281EA/$light/gI" \
      src/gtk-2.0/assets-folder/assets-Dark.svg > "src/gtk-2.0/assets-folder/assets-${theme}-Dark.svg"
  rm -rf "src/gtk-2.0/assets-folder/assets-${theme}" "src/gtk-2.0/assets-folder/assets-${theme}-Dark"
  cp -r src/gtk-2.0/assets-folder/assets "src/gtk-2.0/assets-folder/assets-${theme}"
  cp -r src/gtk-2.0/assets-folder/assets-Dark "src/gtk-2.0/assets-folder/assets-${theme}-Dark"

  # GNOME Shell theme SVGs
  rm -rf "src/gnome-shell/theme-${theme}"
  mkdir -p "src/gnome-shell/theme-${theme}"
  for f in src/gnome-shell/theme/*.svg; do
    base=$(basename "$f")
    sed -e "s/#0078d4/$dark/gI" -e "s/#1A73E8/$dark/gI" "$f" > "src/gnome-shell/theme-${theme}/$base"
  done

  # Cinnamon thumbnails
  magick -size 240x90 "xc:${dark}" -pointsize 14 -fill white -gravity center -annotate +0+0 "$theme" "src/cinnamon/thumbnail-${theme}.png"
  magick -size 240x90 "xc:${dark}" -pointsize 14 -fill white -gravity center -annotate +0+0 "$theme Dark" "src/cinnamon/thumbnail-${theme}-Dark.png"
  magick -size 240x90 "xc:${light}" -pointsize 14 -fill black -gravity center -annotate +0+0 "$theme Light" "src/cinnamon/thumbnail-${theme}-Light.png"

  # GTK thumbnails
  magick -size 121x36 "xc:${dark}" -pointsize 10 -fill white -gravity center -annotate +0+0 "$theme" "src/gtk/thumbnail-${theme}-Dark.png"
  magick -size 121x36 "xc:${light}" -pointsize 10 -fill black -gravity center -annotate +0+0 "$theme" "src/gtk/thumbnail-${theme}.png"

  # GTK2 gtkrc files
  cat > "src/gtk-2.0/gtkrc-${theme}" <<RC
# Dopamine Themes - GTK2 color scheme for ${theme} Light

gtk-color-scheme = "text_color:#212121\\nbase_color:#FFFFFF"
gtk-color-scheme = "fg_color:#212121\\nbg_color:#F2F2F2"
gtk-color-scheme = "selected_fg_color:#FFFFFF\\nselected_bg_color:${dark}"
gtk-color-scheme = "titlebar_fg_color:#212121\\ntitlebar_bg_color:#F7F7F7"
gtk-color-scheme = "menu_color:#FFFFFF"
gtk-color-scheme = "tooltip_fg_color:#FFFFFF\\ntooltip_bg_color:#616161"
gtk-color-scheme = "link_color:${dark}\\nvisited_link_color:#9C27B0"

gtk-auto-mnemonics              = 1
gtk-primary-button-warps-slider = 1

include "main.rc"
include "apps.rc"
include "hacks.rc"
RC

  cat > "src/gtk-2.0/gtkrc-${theme}-Dark" <<RC
# Dopamine Themes - GTK2 color scheme for ${theme} Dark

gtk-color-scheme = "text_color:#FFFFFF\\nbase_color:#2B2B2B"
gtk-color-scheme = "fg_color:#FFFFFF\\nbg_color:#333333"
gtk-color-scheme = "selected_fg_color:#FFFFFF\\nselected_bg_color:${dark}"
gtk-color-scheme = "titlebar_fg_color:#FFFFFF\\ntitlebar_bg_color:#202020"
gtk-color-scheme = "menu_color:#3C3C3C"
gtk-color-scheme = "tooltip_fg_color:#FFFFFF\\ntooltip_bg_color:#616161"
gtk-color-scheme = "link_color:${light}\\nvisited_link_color:#CE93D8"

gtk-auto-mnemonics              = 1
gtk-primary-button-warps-slider = 1

include "main.rc"
include "apps.rc"
include "hacks.rc"
RC

  # README preview placeholders
  magick -size 640x360 "xc:${dark}" -pointsize 32 -fill white -gravity center -annotate +0+0 "${theme} Dark" "assets/preview/${theme}-dark.png"
  magick -size 640x360 "xc:${light}" -pointsize 32 -fill "#222222" -gravity center -annotate +0+0 "${theme} Light" "assets/preview/${theme}-light.png"

done

echo "Dopamine theme assets regenerated."
