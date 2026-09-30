#!/usr/bin/env python3
"""
Generate color preview images for every Dopamine variant.

Layout (640x360):
  ┌─ Variant name + theme accent dot (small)──────────────┐
  │                                                       │
  │   Sample text on `background`, foreground = on(bg)    │
  │                                                       │
  ├─ 8 swatches: primary · success · warning · error ·    │
  │              link · surface · base · base-alt        │
  └───────────────────────────────────────────────────────┘

All colors come from the SCSS palette; semantic colors are the
same ones used by src/_sass/_colors.scss.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Palette — must mirror src/_sass/_colors.scss and src/gnome-shell/sass/_colors.scss
# ---------------------------------------------------------------------------
VARIANTS = [
    "nord", "dracula", "gruvbox", "tokyo-night",
    "everforest", "monokai", "solarized", "catppuccin",
]

# Full palettes mirroring src/_sass/_theme-palettes.scss.
# Each entry maps (mode) -> {role: hex} for mode in "light"|"dark".
PALETTES = {
    "nord": {
        "light": {"primary": "#5e81ac", "background": "#eceff4", "surface": "#e5e9f0",
                  "base": "#d8dee9", "base-alt": "#c8d0e0", "foreground": "#2e3440",
                  "foreground-secondary": "#4c566a", "link": "#5e81ac", "link-visited": "#b48ead",
                  "success": "#a3be8c", "warning": "#d08770", "error": "#bf616a"},
        "dark":  {"primary": "#88c0d0", "background": "#2e3440", "surface": "#3b4252",
                  "base": "#434c5e", "base-alt": "#4c566a", "foreground": "#d8dee9",
                  "foreground-secondary": "#aebacf", "link": "#81a1c1", "link-visited": "#b48ead",
                  "success": "#a3be8c", "warning": "#ebcb8b", "error": "#bf616a"},
    },
    "dracula": {
        "light": {"primary": "#bd93f9", "background": "#f8f8f2", "surface": "#ffffff",
                  "base": "#e6e6e6", "base-alt": "#d1d1d1", "foreground": "#282a36",
                  "foreground-secondary": "#44475a", "link": "#6272a4", "link-visited": "#bd93f9",
                  "success": "#50b26e", "warning": "#d79921", "error": "#e05555"},
        "dark":  {"primary": "#ff79c6", "background": "#282a36", "surface": "#44475a",
                  "base": "#6272a4", "base-alt": "#4a4e5f", "foreground": "#f8f8f2",
                  "foreground-secondary": "#bfbfbf", "link": "#8be9fd", "link-visited": "#bd93f9",
                  "success": "#50fa7b", "warning": "#ffb86c", "error": "#ff5555"},
    },
    "gruvbox": {
        "light": {"primary": "#d79921", "background": "#fbf1c7", "surface": "#f2e5bc",
                  "base": "#ebdbb2", "base-alt": "#d5c4a1", "foreground": "#3c3836",
                  "foreground-secondary": "#665c54", "link": "#458588", "link-visited": "#b16286",
                  "success": "#98971a", "warning": "#d65d0e", "error": "#cc241d"},
        "dark":  {"primary": "#fabd2f", "background": "#282828", "surface": "#3c3836",
                  "base": "#504945", "base-alt": "#665c54", "foreground": "#ebdbb2",
                  "foreground-secondary": "#bdae93", "link": "#83a598", "link-visited": "#d3869b",
                  "success": "#b8bb26", "warning": "#fe8019", "error": "#fb4934"},
    },
    "tokyo-night": {
        "light": {"primary": "#565f89", "background": "#d5d6db", "surface": "#cbccd1",
                  "base": "#c0c1c6", "base-alt": "#b0b1b6", "foreground": "#343a52",
                  "foreground-secondary": "#565f89", "link": "#565f89", "link-visited": "#8b7cb3",
                  "success": "#73a54c", "warning": "#b58a4f", "error": "#c55f73"},
        "dark":  {"primary": "#7aa2f7", "background": "#1a1b26", "surface": "#24283b",
                  "base": "#414868", "base-alt": "#2f334d", "foreground": "#c0caf5",
                  "foreground-secondary": "#a9b1d6", "link": "#7aa2f7", "link-visited": "#bb9af7",
                  "success": "#9ece6a", "warning": "#e0af68", "error": "#f7768e"},
    },
    "everforest": {
        "light": {"primary": "#8da101", "background": "#fdf6e3", "surface": "#f3efd9",
                  "base": "#e6e2cc", "base-alt": "#d8d4be", "foreground": "#5c6a72",
                  "foreground-secondary": "#7a8478", "link": "#5f8a7d", "link-visited": "#b07aa1",
                  "success": "#6e9a6e", "warning": "#c4a000", "error": "#d15f5f"},
        "dark":  {"primary": "#a7c080", "background": "#2b3339", "surface": "#323d43",
                  "base": "#3a454a", "base-alt": "#445055", "foreground": "#d3c6aa",
                  "foreground-secondary": "#ada391", "link": "#7fbbb3", "link-visited": "#d699b6",
                  "success": "#83c092", "warning": "#dbbc7f", "error": "#e67e80"},
    },
    "monokai": {
        "light": {"primary": "#fd971f", "background": "#f8f8f2", "surface": "#ffffff",
                  "base": "#e6e6e6", "base-alt": "#d1d1d1", "foreground": "#272822",
                  "foreground-secondary": "#49483e", "link": "#4a9eb0", "link-visited": "#8b6bcc",
                  "success": "#7fb224", "warning": "#d9791e", "error": "#d91e5f"},
        "dark":  {"primary": "#f92672", "background": "#272822", "surface": "#3e3d32",
                  "base": "#49483e", "base-alt": "#57584f", "foreground": "#f8f8f2",
                  "foreground-secondary": "#c2c2b8", "link": "#66d9ef", "link-visited": "#ae81ff",
                  "success": "#a6e22e", "warning": "#fd971f", "error": "#f92672"},
    },
    "solarized": {
        "light": {"primary": "#268bd2", "background": "#fdf6e3", "surface": "#eee8d5",
                  "base": "#e6e1cf", "base-alt": "#d9d3c1", "foreground": "#073642",
                  "foreground-secondary": "#586e75", "link": "#268bd2", "link-visited": "#6c71c4",
                  "success": "#859900", "warning": "#b58900", "error": "#dc322f"},
        "dark":  {"primary": "#b58900", "background": "#002b36", "surface": "#073642",
                  "base": "#083e4f", "base-alt": "#0e5368", "foreground": "#eee8d5",
                  "foreground-secondary": "#93a1a1", "link": "#268bd2", "link-visited": "#6c71c4",
                  "success": "#859900", "warning": "#cb4b16", "error": "#dc322f"},
    },
    "catppuccin": {
        "light": {"primary": "#8839ef", "background": "#eff1f5", "surface": "#e6e9ef",
                  "base": "#ccd0da", "base-alt": "#bcc0cc", "foreground": "#4c4f69",
                  "foreground-secondary": "#6c6f85", "link": "#1e66f5", "link-visited": "#8839ef",
                  "success": "#40a02b", "warning": "#df8e1d", "error": "#d20f39"},
        "dark":  {"primary": "#f5c2e7", "background": "#1e1e2e", "surface": "#302d41",
                  "base": "#41445a", "base-alt": "#4d516d", "foreground": "#d9e0ee",
                  "foreground-secondary": "#b8b4c7", "link": "#96cdfb", "link-visited": "#ddb6f2",
                  "success": "#abe9b3", "warning": "#fae3b0", "error": "#f28fad"},
    },
}

# Default palette for the no-variant preview
DEFAULT_PALETTE = PALETTES["nord"]

# Convenience accessors kept for compatibility with the drawing code below.
BG          = {"light": DEFAULT_PALETTE["light"]["background"], "dark": DEFAULT_PALETTE["dark"]["background"]}
SURFACE     = {"light": DEFAULT_PALETTE["light"]["surface"],    "dark": DEFAULT_PALETTE["dark"]["surface"]}
BASE        = {"light": DEFAULT_PALETTE["light"]["base"],       "dark": DEFAULT_PALETTE["dark"]["base"]}
BASE_ALT    = {"light": DEFAULT_PALETTE["light"]["base-alt"],   "dark": DEFAULT_PALETTE["dark"]["base-alt"]}
TEXT        = {"light": DEFAULT_PALETTE["light"]["foreground"], "dark": DEFAULT_PALETTE["dark"]["foreground"]}
TEXT_DIM    = {"light": DEFAULT_PALETTE["light"]["foreground-secondary"], "dark": DEFAULT_PALETTE["dark"]["foreground-secondary"]}
LINK        = {"light": DEFAULT_PALETTE["light"]["link"],       "dark": DEFAULT_PALETTE["dark"]["link"]}
SUCCESS     = {"light": DEFAULT_PALETTE["light"]["success"],    "dark": DEFAULT_PALETTE["dark"]["success"]}
WARNING     = {"light": DEFAULT_PALETTE["light"]["warning"],    "dark": DEFAULT_PALETTE["dark"]["warning"]}
ERROR       = {"light": DEFAULT_PALETTE["light"]["error"],      "dark": DEFAULT_PALETTE["dark"]["error"]}
BORDER      = {"light": DEFAULT_PALETTE["light"]["foreground"], "dark": DEFAULT_PALETTE["dark"]["foreground"]}

# ---------------------------------------------------------------------------
# Image layout
# ---------------------------------------------------------------------------
W, H         = 640, 360
PAD          = 24
TITLE_Y      = 24
SAMPLE_Y     = 110
SWATCH_Y     = 220
SWATCH_H     = 96
SWATCH_W     = (W - 2 * PAD - 7 * 12) // 8        # 8 swatches × 12px gap
SAMPLE_LINE2 = 170

FONT_REG = "/usr/share/fonts/MapleMonoNormal-NF-CN/MapleMonoNormal-NF-CN-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/MapleMonoNormal-NF-CN/MapleMonoNormal-NF-CN-Bold.ttf"
FONT_LIGHT = "/usr/share/fonts/MapleMonoNormal-NF-CN/MapleMonoNormal-NF-CN-Light.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def hex2rgb(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    if len(s) != 6:
        raise ValueError(f"Invalid hex color: {s!r}")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def text_width(draw: ImageDraw.ImageDraw, txt: str, fnt) -> int:
    bbox = draw.textbbox((0, 0), txt, font=fnt)
    return int(bbox[2] - bbox[0])


def draw_preview(variant: str, mode: str, out: Path) -> None:
    pal = PALETTES.get(variant, DEFAULT_PALETTE)[mode]
    accent = pal["primary"]
    bg     = pal["background"]
    fg     = pal["foreground"]
    fgdim  = pal["foreground-secondary"]

    img = Image.new("RGB", (W, H), hex2rgb(bg))
    d = ImageDraw.Draw(img)

    # 1px border so light variants are visible on white viewers
    border_rgb = tuple(max(0, c - 30) for c in hex2rgb(pal["base-alt"]))
    d.rectangle([0, 0, W - 1, H - 1], outline=border_rgb, width=1)

    # ---- Header ----
    f_title = font(FONT_BOLD, 28)
    f_meta = font(FONT_LIGHT, 13)

    title = variant
    d.text((PAD, TITLE_Y), title, fill=hex2rgb(accent), font=f_title)

    meta = f"Dopamine · {mode.upper()} · accent {accent.upper()}"
    meta_w = text_width(d, meta, f_meta)
    d.text((W - PAD - meta_w, TITLE_Y + 10), meta, fill=hex2rgb(fgdim), font=f_meta)

    # accent underline below title
    title_w = text_width(d, title, f_title)
    d.rectangle([PAD, TITLE_Y + 36, PAD + title_w, TITLE_Y + 39], fill=hex2rgb(accent))

    # ---- Sample text ----
    f_sample = font(FONT_REG, 18)
    f_sample2 = font(FONT_REG, 14)

    d.text((PAD, SAMPLE_Y),    "Maple Mono-inspired GTK theme", fill=hex2rgb(fg), font=f_sample)
    d.text((PAD, SAMPLE_LINE2), "AaBbCc 0123 — 选定高亮 / 焦点进度环", fill=hex2rgb(fgdim), font=f_sample2)

    # ---- Swatch row (8 chips) ----
    swatches = [
        ("primary",  accent),
        ("success",  pal["success"]),
        ("warning",  pal["warning"]),
        ("error",    pal["error"]),
        ("link",     pal["link"]),
        ("surface",  pal["surface"]),
        ("base",     pal["base"]),
        ("base-alt", pal["base-alt"]),
    ]
    f_label = font(FONT_LIGHT, 10)
    x = PAD
    for name, hexcol in swatches:
        rgb = hex2rgb(hexcol)
        d.rounded_rectangle(
            [x, SWATCH_Y, x + SWATCH_W, SWATCH_Y + SWATCH_H],
            radius=6,
            fill=rgb,
            outline=tuple(max(0, c - 40) for c in rgb) if mode == "light" else tuple(min(255, c + 40) for c in rgb),
            width=1,
        )
        # label color: white-on-dark-chip if chip is dark, else dark text
        brightness = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        label_rgb = (255, 255, 255) if brightness < 140 else (16, 34, 45)
        d.text((x + 8, SWATCH_Y + 8), name, fill=label_rgb, font=f_label)
        d.text((x + 8, SWATCH_Y + SWATCH_H - 18), hexcol.upper(), fill=label_rgb, font=f_label)
        x += SWATCH_W + 12

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out}")


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/preview")
    for v in VARIANTS:
        for mode in ("light", "dark"):
            draw_preview(v, mode, root / f"{v}-{mode}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
