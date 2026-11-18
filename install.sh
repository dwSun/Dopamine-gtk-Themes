#!/bin/bash

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$REPO_DIR/src"

ROOT_UID=0
DEST_DIR=

# For tweaks
opacity=
panel=
window=
outline=
titlebutton=
icon='-default'

# Destination directory
if [[ "$UID" -eq "$ROOT_UID" ]]; then
  DEST_DIR="/usr/share/themes"
elif [[ -n "$XDG_DATA_HOME" ]]; then
  DEST_DIR="$XDG_DATA_HOME/themes"
elif [[ -d "$HOME/.themes" ]]; then
  DEST_DIR="$HOME/.themes"
elif [[ -d "$HOME/.local/share/themes" ]]; then
  DEST_DIR="$HOME/.local/share/themes"
else
  DEST_DIR="$HOME/.themes"
fi

SASSC_OPT="-M -t expanded"

THEME_NAME=Dopamine
THEME_VARIANTS=('-nord' '-gruvbox' '-monokai' '-catppuccin' '-candy' '-tangerine' '-berry' '-magenta' '-sakura' '-coral')
COLOR_VARIANTS=('-Light' '-Dark')

if [[ "$(command -v gnome-shell)" ]]; then
  gnome-shell --version
  SHELL_VERSION="$(gnome-shell --version | cut -d ' ' -f 3 | cut -d . -f -1)"
  if [[ "${SHELL_VERSION:-}" -ge "48" ]]; then
    GS_VERSION="48-0"
  elif [[ "${SHELL_VERSION:-}" -ge "47" ]]; then
    GS_VERSION="47-0"
  elif [[ "${SHELL_VERSION:-}" -ge "46" ]]; then
    GS_VERSION="46-0"
  elif [[ "${SHELL_VERSION:-}" -ge "44" ]]; then
    GS_VERSION="44-0"
  elif [[ "${SHELL_VERSION:-}" -ge "42" ]]; then
    GS_VERSION="42-0"
  elif [[ "${SHELL_VERSION:-}" -ge "40" ]]; then
    GS_VERSION="40-0"
  else
    GS_VERSION="3-28"
  fi
else
  echo "'gnome-shell' not found, using styles for last gnome-shell version available."
  GS_VERSION="48-0"
fi

usage() {
cat << EOF
Usage: $0 [OPTION]...

OPTIONS:
  -d, --dest DIR          Specify destination directory (Default: $DEST_DIR)

  -n, --name NAME         Specify theme name (Default: $THEME_NAME)

  -t, --theme VARIANT     Specify theme color variant(s) [nord|gruvbox|monokai|catppuccin|candy|tangerine|berry|magenta|sakura|coral|all] (Default: default)

  -c, --color VARIANT     Specify color variant(s) [light|dark] (Default: All variants)

  -i, --icon VARIANT      Specify icon variant(s) for shell panel
                          [default|apple|simple|gnome|ubuntu|arch|manjaro|fedora|debian|void|opensuse|popos|mxlinux|zorin|endeavouros|tux|nixos]
                          (Default: default)

  -l, --libadwaita        Install link to gtk4 config for theming libadwaita

  -r, --remove
  -u, --uninstall         Uninstall/remove themes or link for libadwaita

  --tweaks                Specify versions for tweaks [solid|float|round|noborder|square]
                          solid:    no transparency version
                          float:    floating panel
                          round:    rounded windows
                          noborder: windows and menu with no border
                          square:   square windows button

  -h, --help              Show help
EOF
}

install() {
  local dest="$1"
  local name="$2"
  local theme="$3"
  local color="$4"
  local icon="$5"

  [[ "$color" == '-Dark' ]] && local ELSE_DARK="$color"
  [[ "$color" == '-Light' ]] && local ELSE_LIGHT="$color"
  [[ "$color" == '-Dark' ]] || [[ "$color" == '' ]] && local ACTIVITIES_ASSETS_SUFFIX="-Dark"

  if [[ "$window" == 'round' ]]; then
    round='-round'
  else
    round=$window
  fi

  local THEME_DIR="$dest/$name$round$theme$color"

  [[ -d "$THEME_DIR" ]] && rm -rf "${THEME_DIR:?}"

  theme_tweaks && install_theme_color

    # sassc-compile paths below always need a fresh _tweaks-temp.scss; theme_tweaks()
    # only prepares it when tweaks=='true', so seed it here for the plain case too.
    if [[ "$tweaks" != 'true' ]]; then
      cp -rf ${SRC_DIR}/_sass/_tweaks.scss ${SRC_DIR}/_sass/_tweaks-temp.scss
      cp -rf ${SRC_DIR}/gnome-shell/sass/_tweaks.scss ${SRC_DIR}/gnome-shell/sass/_tweaks-temp.scss
    fi

  echo "Installing '$THEME_DIR'..."

  mkdir -p                                                                      "$THEME_DIR"
  cp -r "$REPO_DIR/COPYING"                                                     "$THEME_DIR"

  echo "[Desktop Entry]" >>                                                     "$THEME_DIR/index.theme"
  echo "Type=X-GNOME-Metatheme" >>                                              "$THEME_DIR/index.theme"
  echo "Name=$name$round$theme$color" >>                                   "$THEME_DIR/index.theme"
  echo "Comment=A Dopamine GTK theme for GNOME" >>                               "$THEME_DIR/index.theme"
  echo "Encoding=UTF-8" >>                                                      "$THEME_DIR/index.theme"
  echo "" >>                                                                    "$THEME_DIR/index.theme"
  echo "[X-GNOME-Metatheme]" >>                                                 "$THEME_DIR/index.theme"
  echo "GtkTheme=$name$round$theme$color" >>                               "$THEME_DIR/index.theme"
  echo "MetacityTheme=$name$round$theme$color" >>                          "$THEME_DIR/index.theme"
  echo "IconTheme=$name${ELSE_DARK:-}" >>                                       "$THEME_DIR/index.theme"
  echo "CursorTheme=$name${ELSE_DARK:-}" >>                                     "$THEME_DIR/index.theme"
  echo "ButtonLayout=close,minimize,maximize:menu" >>                           "$THEME_DIR/index.theme"

  mkdir -p                                                                      "$THEME_DIR/gnome-shell"
  cp -r "$SRC_DIR/gnome-shell/pad-osd.css"                                      "$THEME_DIR/gnome-shell"

  # Always sassc-compile shell css: there is no pre-built gnome-shell-<theme>.css,
  # so cp would silently leave a missing source in place for any non-default variant.
  sassc $SASSC_OPT "$SRC_DIR/gnome-shell/shell-$GS_VERSION/gnome-shell$color.scss" "$THEME_DIR/gnome-shell/gnome-shell.css"

  cp -r "${SRC_DIR}/gnome-shell/common-assets"                                  "$THEME_DIR/gnome-shell/assets"
  cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/"*.svg                     "$THEME_DIR/gnome-shell/assets"
  cp -r "${SRC_DIR}/gnome-shell/theme$theme/"*.svg                              "$THEME_DIR/gnome-shell/assets"
  cp -r "${SRC_DIR}/gnome-shell/assets${ACTIVITIES_ASSETS_SUFFIX:-}/activities/activities${icon}.svg" "$THEME_DIR/gnome-shell/assets/activities.svg"

  if [[ "$window" = "round" ]] ; then
    cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/buttons-round/"*.svg     "$THEME_DIR/gnome-shell/assets"
  else
    cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/buttons/"*.svg           "$THEME_DIR/gnome-shell/assets"
  fi

  if [[ "$color" = "-Light" ]] ; then
    cp -r "${SRC_DIR}/gnome-shell/assets-Dark/activities/activities${icon}.svg" "$THEME_DIR/gnome-shell/assets/activities-white.svg"
  fi

  if [[ "$opacity" = "solid" ]] ; then
    if [[ "$window" = "round" ]] ; then
      if [[ "$outline" = "" ]] ; then
        cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/solid-round/"*.svg    "$THEME_DIR/gnome-shell/assets"
      else
        cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/solid-round-borderless/"*.svg "$THEME_DIR/gnome-shell/assets"
      fi
    else
      if [[ "$outline" = "" ]] ; then
        cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/solid/"*.svg           "$THEME_DIR/gnome-shell/assets"
      else
        cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/solid-borderless/"*.svg "$THEME_DIR/gnome-shell/assets"
      fi
    fi
  else
    if [[ "$window" = "round" ]] ; then
      if [[ "$outline" = "" ]] ; then
        cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/default-round/"*.svg   "$THEME_DIR/gnome-shell/assets"
      else
        cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/default-round-borderless/"*.svg "$THEME_DIR/gnome-shell/assets"
      fi
    else
      if [[ "$outline" = "" ]] ; then
        cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/default/"*.svg         "$THEME_DIR/gnome-shell/assets"
      else
        cp -r "${SRC_DIR}/gnome-shell/assets${ELSE_DARK:-}/default-borderless/"*.svg "$THEME_DIR/gnome-shell/assets"
      fi
    fi
  fi

  cd "$THEME_DIR/gnome-shell"
  ln -s assets/no-events.svg no-events.svg
  ln -s assets/process-working.svg process-working.svg
  ln -s assets/no-notifications.svg no-notifications.svg

  mkdir -p                                                                      "$THEME_DIR/gtk-2.0"
  cp -r "$SRC_DIR/gtk-2.0/common/"{apps.rc,hacks.rc,main.rc}                    "$THEME_DIR/gtk-2.0"
  cp -r "$SRC_DIR/gtk-2.0/assets-folder/assets$theme${ELSE_DARK:-}"             "$THEME_DIR/gtk-2.0/assets"
  cp -r "$SRC_DIR/gtk-2.0/gtkrc$theme${ELSE_DARK:-}"                            "$THEME_DIR/gtk-2.0/gtkrc"

  mkdir -p                                                                      "$THEME_DIR/gtk-3.0"
  cp -r "$SRC_DIR/gtk/assets$theme"                                             "$THEME_DIR/gtk-3.0/assets"
  cp -r "$SRC_DIR/gtk/scalable"                                                 "$THEME_DIR/gtk-3.0/assets"
  cp -r "$SRC_DIR/gtk/thumbnail$theme${ELSE_DARK:-}.png"                        "$THEME_DIR/gtk-3.0/thumbnail.png"

  # Always sassc-compile gtk css: see gnome-shell note above.
  sassc $SASSC_OPT "$SRC_DIR/gtk/3.0/gtk$color.scss"                     "$THEME_DIR/gtk-3.0/gtk.css"
  sassc $SASSC_OPT "$SRC_DIR/gtk/3.0/gtk-Dark.scss"                      "$THEME_DIR/gtk-3.0/gtk-dark.css"

  mkdir -p                                                                      "$THEME_DIR/gtk-4.0"
  cp -r "$SRC_DIR/gtk/assets$theme"                                             "$THEME_DIR/gtk-4.0/assets"
  cp -r "$SRC_DIR/gtk/scalable"                                                 "$THEME_DIR/gtk-4.0/assets"

  sassc $SASSC_OPT "$SRC_DIR/gtk/4.0/gtk$color.scss"                     "$THEME_DIR/gtk-4.0/gtk.css"
  sassc $SASSC_OPT "$SRC_DIR/gtk/4.0/gtk-Dark.scss"                      "$THEME_DIR/gtk-4.0/gtk-dark.css"

  mkdir -p                                                                      "$THEME_DIR/cinnamon"
  cp -r "$SRC_DIR/cinnamon/common-assets"                                       "$THEME_DIR/cinnamon/assets"
  cp -r "$SRC_DIR/cinnamon/assets${ELSE_DARK:-}/"*.svg                          "$THEME_DIR/cinnamon/assets"

  if [[ "$accent" == 'true' || "$opacity" == 'solid' ]]; then
    sassc $SASSC_OPT "$SRC_DIR/cinnamon/cinnamon$color.scss"               "$THEME_DIR/cinnamon/cinnamon.css"
  else
    cp -r "$SRC_DIR/cinnamon/cinnamon$color.css"                           "$THEME_DIR/cinnamon/cinnamon.css"
  fi

  cp -r "$SRC_DIR/cinnamon/thumbnail$theme$color.png"                           "$THEME_DIR/cinnamon/thumbnail.png"
  
  mkdir -p                                                                      "$THEME_DIR/xfwm4"

  if [[ "$titlebutton" = "square" ]] ; then
    cp -r "$SRC_DIR/xfwm4/assets-square$color/"*.png                            "$THEME_DIR/xfwm4"
    cp -r "$SRC_DIR/xfwm4/themerc-square${ELSE_LIGHT:-}"                        "$THEME_DIR/xfwm4/themerc"
  else
    cp -r "$SRC_DIR/xfwm4/assets$color/"*.png                                   "$THEME_DIR/xfwm4"
    cp -r "$SRC_DIR/xfwm4/themerc${ELSE_LIGHT:-}"                               "$THEME_DIR/xfwm4/themerc"
  fi

  mkdir -p                                                                      "$THEME_DIR/labwc"
  cp -r "$SRC_DIR/labwc/assets${ELSE_LIGHT:-}/"*.svg                            "$THEME_DIR/labwc"
  cp -r "$SRC_DIR/labwc/themerc${ELSE_DARK:-}${ELSE_LIGHT:-}"                   "$THEME_DIR/labwc/themerc"

  mkdir -p                                                                      "$THEME_DIR/metacity-1"
  cp -r "$SRC_DIR/metacity-1/metacity-theme-2$color.xml"                        "$THEME_DIR/metacity-1/metacity-theme-2.xml"

  if [[ "$window" = "round" ]] ; then
    cp -r "$SRC_DIR/metacity-1/metacity-theme-3-round.xml"                      "$THEME_DIR/metacity-1/metacity-theme-3.xml"
    cp -r "$SRC_DIR/metacity-1/assets-round"                                    "$THEME_DIR/metacity-1/assets"
  else
    cp -r "$SRC_DIR/metacity-1/metacity-theme-3.xml"                            "$THEME_DIR/metacity-1"
    cp -r "$SRC_DIR/metacity-1/assets"                                          "$THEME_DIR/metacity-1"
  fi

  cp -r "$SRC_DIR/metacity-1/thumbnail${ELSE_DARK:-}.png"                       "$THEME_DIR/metacity-1/thumbnail.png"
  cd "$THEME_DIR/metacity-1" && ln -s metacity-theme-2.xml metacity-theme-1.xml

  mkdir -p                                                                      "$THEME_DIR/plank"
  cp -r "$SRC_DIR/plank/theme${ELSE_LIGHT:-}/dock.theme"                        "$THEME_DIR/plank"

  # Per-theme helper to link this theme into ~/.config/gtk-{3,4}.0 for
  # applications (notably libadwaita) that do not read the GNOME tweak theme.
  cp -r "$SRC_DIR/gtk-set.sh"                                                   "$THEME_DIR/gtk-set.sh"
}

themes=()
colors=()
lcolors=()

while [[ "$#" -gt 0 ]]; do
  case "${1:-}" in
    -d|--dest)
      dest="$2"
      mkdir -p "$dest"
      shift 2
      ;;
    -n|--name)
      name="$2"
      shift 2
      ;;
    -l|--libadwaita)
      libadwaita="true"
      shift
      ;;
    -u|--uninstall|-r|--remove)
      uninstall="true"
      shift
      ;;
    --tweaks)
      shift
      for tweaks in "$@"; do
        case "$tweaks" in
          solid)
            opacity="solid"
            shift
            ;;
          float)
            panel="float"
            echo -e "Install floating panel version ..."
            shift
            ;;
          round)
            window="round"
            echo -e "Install rounded windows version ..."
            shift
            ;;
          noborder)
            outline="false"
            echo -e "Install windows without outline version ..."
            shift
            ;;
          square)
            titlebutton="square"
            echo -e "Install square windows button version ..."
            shift
            ;;
          -*)
            break
            ;;
          *)
            echo "ERROR: Unrecognized tweaks variant '$1'."
            echo "Try '$0 --help' for more information."
            exit 1
            ;;
        esac
      done
      ;;
    -t|--theme)
      accent='true'
      shift
      for variant in "$@"; do
        case "$variant" in
          all)
            themes+=("${THEME_VARIANTS[@]}")
            shift
            ;;
          -*)
            break
            ;;
          *)
            if [[ " ${THEME_VARIANTS[*]} " == *" -$variant "* ]]; then
              themes+=("-$variant")
              shift
            else
              echo "ERROR: Unrecognized theme variant '$variant'."
              echo "Try '$0 --help' for more information."
              exit 1
            fi
            ;;
        esac
      done
      ;;
    -i|--icon)
      activities='icon'
      shift
      for icons in "$@"; do
        case "$icons" in
          default)
            icon='-default'
            shift
            ;;
          apple)
            icon='-apple'
            shift
            ;;
          simple)
            icon='-simple'
            shift
            ;;
          gnome)
            icon='-gnome'
            shift
            ;;
          ubuntu)
            icon='-ubuntu'
            shift
            ;;
          arch)
            icon='-arch'
            shift
            ;;
          manjaro)
            icon='-manjaro'
            shift
            ;;
          fedora)
            icon='-fedora'
            shift
            ;;
          debian)
            icon='-debian'
            shift
            ;;
          void)
            icon='-void'
            shift
            ;;
          opensuse)
            icon='-opensuse'
            shift
            ;;
          popos)
            icon='-popos'
            shift
            ;;
          mxlinux)
            icon='-mxlinux'
            shift
            ;;
          zorin)
            icon='-zorin'
            shift
            ;;
          endeavouros)
            icon='-endeavouros'
            shift
            ;;
          tux)
            icon='-tux'
            shift
            ;;
          nixos)
            icon='-nixos'
            shift
            ;;
          -*)
            break
            ;;
          *)
            echo "ERROR: Unrecognized icon variant '$1'."
            echo "Try '$0 --help' for more information."
            exit 1
            ;;
        esac
        echo "Install $icons icon for gnome-shell panel..."
      done
      ;;
    -c|--color)
      shift
      for variant in "$@"; do
        case "$variant" in
          light)
            colors+=("${COLOR_VARIANTS[0]}")
            lcolors+=("${COLOR_VARIANTS[0]}")
            shift
            ;;
          dark)
            colors+=("${COLOR_VARIANTS[1]}")
            lcolors+=("${COLOR_VARIANTS[1]}")
            shift
            ;;
          -*|--*)
            break
            ;;
          *)
            echo "ERROR: Unrecognized color variant '$1'."
            echo "Try '$0 --help' for more information."
            exit 1
            ;;
        esac
      done
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: Unrecognized installation option '${1:-}'."
      echo "Try '$0 --help' for more information."
      exit 1
      ;;
  esac
done

if [[ "${#themes[@]}" -eq 0 ]] ; then
  themes=('')
fi

if [[ "${#colors[@]}" -eq 0 ]] ; then
  colors=("${COLOR_VARIANTS[@]}")
fi

if [[ "${#lcolors[@]}" -eq 0 ]] ; then
  lcolors=("${COLOR_VARIANTS[0]}")
fi

#  Check command avalibility
function has_command() {
  command -v $1 > /dev/null
}

#  Install needed packages
install_package() {
  if [ ! "$(command -v sassc 2> /dev/null)" ]; then
    echo sassc needs to be installed to generate the css.
    if has_command zypper; then
      sudo zypper in sassc
    elif has_command apt-get; then
      sudo apt-get install sassc
    elif has_command dnf; then
      sudo dnf install sassc
    elif has_command dnf; then
      sudo dnf install sassc
    elif has_command pacman; then
      sudo pacman -S --noconfirm sassc
    fi
  fi
}

tweaks_temp() {
  cp -rf ${SRC_DIR}/_sass/_tweaks.scss ${SRC_DIR}/_sass/_tweaks-temp.scss
  cp -rf ${SRC_DIR}/gnome-shell/sass/_tweaks.scss ${SRC_DIR}/gnome-shell/sass/_tweaks-temp.scss
}

install_float_panel() {
  sed -i "/\$panel_style:/s/default/float/" ${SRC_DIR}/gnome-shell/sass/_tweaks-temp.scss
  sed -i "/\$panel_style:/s/default/float/" ${SRC_DIR}/_sass/_tweaks-temp.scss
}

install_solid() {
  sed -i "/\$opacity:/s/default/solid/" ${SRC_DIR}/gnome-shell/sass/_tweaks-temp.scss
  sed -i "/\$opacity:/s/default/solid/" ${SRC_DIR}/_sass/_tweaks-temp.scss
  echo -e "Install solid version ..."
}

install_round() {
  sed -i "/\$window:/s/default/round/" ${SRC_DIR}/gnome-shell/sass/_tweaks-temp.scss
  sed -i "/\$window:/s/default/round/" ${SRC_DIR}/_sass/_tweaks-temp.scss
}



install_noborder() {
  sed -i "/\$outline:/s/true/false/" ${SRC_DIR}/gnome-shell/sass/_tweaks-temp.scss
  sed -i "/\$outline:/s/true/false/" ${SRC_DIR}/_sass/_tweaks-temp.scss
}

install_square() {
  sed -i "/\$titlebutton:/s/circular/square/" ${SRC_DIR}/_sass/_tweaks-temp.scss
}

activities_style() {
  sed -i "/\$activities:/s/default/icon/" ${SRC_DIR}/gnome-shell/sass/_tweaks-temp.scss
}

install_theme_color() {
  if [[ "$theme" != '' ]]; then
    theme_color="${theme#-}"
    if [[ " ${THEME_VARIANTS[*]} " != *" $theme "* ]]; then
      echo "ERROR: Unrecognized theme variant '$theme'."
      echo "Try '$0 --help' for more information."
      exit 1
    fi
    # Write the whole line instead of substituting the literal 'default': the
    # temp file can still hold a colour from a previous run, and the old
    # sed-only-match-default trick then silently did nothing.
    sed -i "s/^\$theme: .*/\$theme: '${theme_color}';/" "${SRC_DIR}/gnome-shell/sass/_tweaks-temp.scss"
    sed -i "s/^\$theme: .*/\$theme: '${theme_color}';/" "${SRC_DIR}/_sass/_tweaks-temp.scss"
  fi
}

theme_tweaks() {
  if [[ "$panel" = "float" || "$opacity" == 'solid' || "$window" == 'round' || "$accent" == 'true' || "$outline" == 'false' || "$titlebutton" == 'square' || "$activities" = "icon" ]]; then
    tweaks='true'
    install_package; tweaks_temp
  fi

  if [[ "$panel" = "float" ]] ; then
    install_float_panel
  fi

  if [[ "$opacity" = "solid" ]] ; then
    install_solid
  fi

  if [[ "$window" = "round" ]] ; then
    install_round
  fi

  if [[ "$outline" = "false" ]] ; then
    install_noborder
  fi

  if [[ "$titlebutton" = "square" ]] ; then
    install_square
  fi

  if [[ "$activities" = "icon" ]] ; then
    activities_style
  fi
}

uninstall() {
  local dest="${1}"
  local name="${2}"
  local theme="${3}"
  local color="${4}"

  if [[ "$window" == 'round' ]]; then
    round='-round'
  else
    round=$window
  fi

  local THEME_DIR="$dest/$name$round$theme$color"

  if [[ -d "${THEME_DIR}" ]]; then
    echo -e "Uninstall ${THEME_DIR}... "
    rm -rf "${THEME_DIR}"
  fi
}

uninstall_link() {
  rm -rf "${HOME}/.config/gtk-4.0"/{assets,gtk.css,gtk-dark.css}
}

link_libadwaita() {
  local dest="$1"
  local name="$2"
  local theme="$3"
  local color="$4"

  if [[ "$window" == 'round' ]]; then
    round='-round'
  else
    round=$window
  fi

  local THEME_DIR="$dest/$name$round$theme$color"

  echo -e "\nLink '$THEME_DIR/gtk-4.0' to '${HOME}/.config/gtk-4.0' for libadwaita..."

  mkdir -p                                                                      "${HOME}/.config/gtk-4.0"
  ln -sf "${THEME_DIR}/gtk-4.0/assets"                                          "${HOME}/.config/gtk-4.0/assets"
  ln -sf "${THEME_DIR}/gtk-4.0/gtk.css"                                         "${HOME}/.config/gtk-4.0/gtk.css"
  ln -sf "${THEME_DIR}/gtk-4.0/gtk-dark.css"                                    "${HOME}/.config/gtk-4.0/gtk-dark.css"
}

clean() {
  local dest="$1"
  local name="$2"
  local round="$3"
  local theme="$4"
  local color="$5"

  local THEME_DIR="$dest/$name$round$theme$color"

  if [[ -d ${THEME_DIR} ]]; then
    rm -rf ${THEME_DIR}
    echo -e "Find: ${THEME_DIR} ! removing it ..."
  fi
}

clean_theme() {
  for round in '' '-round'; do
    for theme in "${THEME_VARIANTS[@]}"; do
      for color in '-light' '-dark'; do
        clean "${dest:-$DEST_DIR}" "${name:-$THEME_NAME}" "$round" "$theme" "$color"
      done
    done
  done

  if [[ "$DEST_DIR" == "$HOME/.themes" ]]; then
    local dest="$HOME/.local/share/themes"
  fi

  for theme in "${THEME_VARIANTS[@]}"; do
    for color in "${COLOR_VARIANTS[@]}"; do
      uninstall "${dest}" "${name:-$THEME_NAME}" "$theme" "$color"
    done
  done
}

uninstall_theme() {
  for theme in "${themes[@]}"; do
    for color in "${colors[@]}"; do
      uninstall "${dest:-$DEST_DIR}" "${name:-$THEME_NAME}" "$theme" "$color"
    done
  done
}

install_theme() {
  for theme in "${themes[@]}"; do
    for color in "${colors[@]}"; do
      install "${dest:-$DEST_DIR}" "${name:-$THEME_NAME}" "$theme" "$color" "$icon"
    done
  done
}

link_theme() {
  for theme in "${themes[@]}"; do
    for color in "${lcolors[@]}"; do
      link_libadwaita "${dest:-$DEST_DIR}" "${name:-$THEME_NAME}" "$theme" "$color"
    done
  done
}

if [[ "$uninstall" == 'true' ]]; then
  if [[ "$libadwaita" == 'true' ]]; then
    echo -e "\nUninstall ${HOME}/.config/gtk-4.0 links ..."
    uninstall_link
  else
    echo && uninstall_theme && uninstall_link
  fi
else
   clean_theme && install_theme

   if [[ "$libadwaita" == 'true' ]]; then
     uninstall_link && link_theme
   fi
fi

echo
echo "Done."
