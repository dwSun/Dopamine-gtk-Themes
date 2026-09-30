#! /bin/bash

THEME_DIR=$(cd $(dirname $0) && pwd)

THEME_NAME=Dopamine

_COLOR_VARIANTS=('-Light' '-Dark')
_ROUND_VARIANTS=('' '-round')
_THEME_VARIANTS=('-nord' '-dracula' '-gruvbox' '-tokyo-night' '-everforest' '-monokai' '-solarized' '-catppuccin' '-candy' '-tangerine' '-minty' '-berry' '-nebula')

if [ ! -z "${ROUND_VARIANTS:-}" ]; then
  IFS=', ' read -r -a _ROUND_VARIANTS <<< "${ROUND_VARIANTS:-}"
fi

if [ ! -z "${COLOR_VARIANTS:-}" ]; then
  IFS=', ' read -r -a _COLOR_VARIANTS <<< "${COLOR_VARIANTS:-}"
fi

if [ ! -z "${THEME_VARIANTS:-}" ]; then
  IFS=', ' read -r -a _THEME_VARIANTS <<< "${THEME_VARIANTS:-}"
fi

Tar_themes() {
for round in "${_ROUND_VARIANTS[@]}"; do
  for theme in "${_THEME_VARIANTS[@]}"; do
    rm -rf ${THEME_NAME}${round}${theme}.tar.xz
  done
done

for round in "${_ROUND_VARIANTS[@]}"; do
  for theme in "${_THEME_VARIANTS[@]}"; do
    tar -Jcvf ${THEME_NAME}${round}${theme}.tar.xz ${THEME_NAME}${round}${theme}{'','-Light','-Dark'}
  done
done
}

Clear_theme() {
for round in "${_ROUND_VARIANTS[@]}"; do
  for theme in "${_THEME_VARIANTS[@]}"; do
    for color in "${_COLOR_VARIANTS[@]}"; do
      [[ -d "${THEME_NAME}${round}${theme}${color}" ]] && rm -rf "${THEME_NAME}${round}${theme}${color}"
    done
  done
done
}

cd .. && ./install.sh -d $THEME_DIR -t all && ./install.sh -d $THEME_DIR -t all --tweaks round

cd $THEME_DIR && Tar_themes && Clear_theme

