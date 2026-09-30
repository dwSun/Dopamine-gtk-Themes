#! /usr/bin/env bash

set -ueo pipefail

# Theme order matches install.sh / release/make-release.sh.
# Empty theme name = default/upstream Fluent blue.
for theme in '' '-nord' '-dracula' '-gruvbox' '-tokyo-night' '-everforest' '-monokai' '-solarized' '-catppuccin' '-candy' '-tangerine' '-minty' '-berry' '-nebula'; do
    case "$theme" in
      '')
        theme_color_dark='#1A73E8'
        theme_color_light='#3281EA'
        ;;
      -nord)
        theme_color_dark='#5E81AC'
        theme_color_light='#88C0D0'
        ;;
      -dracula)
        theme_color_dark='#FF79C6'
        theme_color_light='#FFB3E0'
        ;;
      -gruvbox)
        theme_color_dark='#D79921'
        theme_color_light='#FABD2F'
        ;;
      -tokyo-night)
        theme_color_dark='#7AA2F7'
        theme_color_light='#A9C2FF'
        ;;
      -everforest)
        theme_color_dark='#A7C080'
        theme_color_light='#C5D9A0'
        ;;
      -monokai)
        theme_color_dark='#F92672'
        theme_color_light='#FF6B9F'
        ;;
      -solarized)
        theme_color_dark='#B58900'
        theme_color_light='#E6B450'
        ;;
      -catppuccin)
        theme_color_dark='#F5C2E7'
        theme_color_light='#FFE0F5'
        ;;
      -candy)
        theme_color_dark='#FF4F9A'
        theme_color_light='#FFB3E0'
        ;;
      -tangerine)
        theme_color_dark='#FF8A1F'
        theme_color_light='#FFBC80'
        ;;
      -minty)
        theme_color_dark='#69F0AE'
        theme_color_light='#B9F6CA'
        ;;
      -berry)
        theme_color_dark='#FF6F91'
        theme_color_light='#FFB3C1'
        ;;
      -nebula)
        theme_color_dark='#00E5FF'
        theme_color_light='#80E8FF'
        ;;

    esac

  rm -f "assets${theme}.svg"
  cp -rf "assets.svg" "assets${theme}.svg"
  sed -i "s/#1A73E8/${theme_color_dark}/g" "assets${theme}.svg"
  sed -i "s/#3281EA/${theme_color_light}/g" "assets${theme}.svg"
done

echo -e "DONE!"
