#!/usr/bin/env python3
"""
Generate recolored assets for all Dopamine Themes variants.

This script is designed for environments without inkscape/rendersvg:
PNG assets are produced by HSV hue-remapping the upstream blue assets.

Outputs:
  - src/gtk/assets-<theme>.svg          (source SVG, sed-recolored)
  - src/gtk/assets-<theme>/             (52 PNGs, light + dark variants)
  - src/gtk-2.0/assets-folder/assets-<theme>{,-Dark}/  (30 PNGs each)
  - src/gtk-2.0/gtkrc-<theme>{,-Dark}
  - src/gnome-shell/theme-<theme>/      (3 SVGs)
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from palette_utils import hex_to_rgb, parse_palettes

ROOT = Path(__file__).resolve().parents[1]


def build_theme_colors() -> dict[str, dict[str, tuple[int, int, int]]]:
    """Derive every variant's asset accent from the palette SCSS.

    The naming follows the *source* asset reference, not the GNOME variant:
      * ``"dark"``  → pixels used by Light themes (source ``#1A73E8``)
      * ``"light"`` → pixels used by Dark themes  (source ``#3281EA``)

    Keeping this derived instead of hard-coded is what makes the five dopamine
    themes get their own focus rings; they used to be left upstream blue.
    """
    colors: dict[str, dict[str, tuple[int, int, int]]] = {}
    for name, modes in parse_palettes().items():
        if name == "default":  # default reuses the untouched upstream assets
            continue
        colors[name] = {
            "dark": hex_to_rgb(modes["light"]["primary"]),
            "light": hex_to_rgb(modes["dark"]["primary"]),
        }
    return colors


THEMES = build_theme_colors()

# Upstream blue references used in the base assets.
# "dark"  primary maps from the darker blue (#1A73E8).
# "light" primary maps from the brighter blue (#3281EA).
SOURCE_REFS = {
    "dark":  {"hex": "#1A73E8", "rgb": (0x1A, 0x73, 0xE8)},
    "light": {"hex": "#3281EA", "rgb": (0x32, 0x81, 0xEA)},
}


def rgb_to_hsv(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn
    if df == 0:
        h = 0.0
    elif mx == r:
        h = (60 * ((g - b) / df) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / df) + 120) % 360
    else:
        h = (60 * ((r - g) / df) + 240) % 360
    s = 0 if mx == 0 else df / mx
    v = mx
    return h, s, v


def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def recolor_png(src: Path, dst: Path, target_rgb: tuple[int, int, int],
                source_rgb: tuple[int, int, int]) -> None:
    """Hue-remap the blue family in src PNG to target color, write dst."""
    img = Image.open(src).convert("RGBA")
    arr = np.array(img)
    rgb = arr[:, :, :3].astype(np.float32)
    alpha = arr[:, :, 3]

    src_h, src_s, src_v = rgb_to_hsv(source_rgb)
    tgt_h, tgt_s, tgt_v = rgb_to_hsv(target_rgb)

    # Convert image to HSV (full 0-360 hue)
    r, g, b = rgb[:, :, 0] / 255.0, rgb[:, :, 1] / 255.0, rgb[:, :, 2] / 255.0
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    with np.errstate(divide='ignore', invalid='ignore'):
        df = mx - mn
        # Hue
    h = np.zeros_like(r)
    mask_r = (mx == r) & (df > 1e-8)
    mask_g = (mx == g) & (df > 1e-8)
    mask_b = (mx == b) & (df > 1e-8)
    h[mask_r] = (60 * ((g[mask_r] - b[mask_r]) / df[mask_r]) + 360) % 360
    h[mask_g] = (60 * ((b[mask_g] - r[mask_g]) / df[mask_g]) + 120) % 360
    h[mask_b] = (60 * ((r[mask_b] - g[mask_b]) / df[mask_b]) + 240) % 360

    with np.errstate(divide='ignore', invalid='ignore'):
        s = np.where(mx > 0, df / mx, 0)
    v = mx

    # Mask: pixels close to the source blue hue and reasonably saturated/bright
    hue_dist = np.abs((h - src_h + 180) % 360 - 180)
    mask = (hue_dist < 40) & (s > 0.08) & (v > 0.12)

    # Apply hue shift
    h[mask] = (h[mask] + (tgt_h - src_h)) % 360

    # Scale saturation/value relative to the source reference
    if src_s > 0:
        s[mask] = np.clip(s[mask] * (tgt_s / src_s), 0, 1)
    s[mask] = np.clip(s[mask], 0, 1)
    v[mask] = np.clip(v[mask] * (tgt_v / src_v), 0, 1)

    # Back to RGB
    new_rgb = np.zeros_like(rgb)
    for i in range(3):
        new_rgb[:, :, i] = hsv_to_rgb_vectorized(h, s, v)[:, :, i]

    out = np.dstack([new_rgb.astype(np.uint8), alpha])
    Image.fromarray(out).save(dst, optimize=True)


def hsv_to_rgb_vectorized(h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Vectorized HSV->RGB for numpy arrays (h in 0-360, s/v in 0-1)."""
    c = v * s
    hh = (h / 60) % 2 - 1
    x = c * (1 - np.abs(hh))
    m = v - c

    r = np.zeros_like(h)
    g = np.zeros_like(h)
    b = np.zeros_like(h)

    seg0 = (h < 60)
    seg1 = (h >= 60) & (h < 120)
    seg2 = (h >= 120) & (h < 180)
    seg3 = (h >= 180) & (h < 240)
    seg4 = (h >= 240) & (h < 300)
    seg5 = (h >= 300)

    r[seg0], g[seg0], b[seg0] = c[seg0], x[seg0], 0
    r[seg1], g[seg1], b[seg1] = x[seg1], c[seg1], 0
    r[seg2], g[seg2], b[seg2] = 0, c[seg2], x[seg2]
    r[seg3], g[seg3], b[seg3] = 0, x[seg3], c[seg3]
    r[seg4], g[seg4], b[seg4] = x[seg4], 0, c[seg4]
    r[seg5], g[seg5], b[seg5] = c[seg5], 0, x[seg5]

    rgb = np.stack([(r + m) * 255, (g + m) * 255, (b + m) * 255], axis=-1)
    return np.clip(rgb, 0, 255).astype(np.uint8)


def is_dark_asset(filename: str) -> bool:
    """Files ending in -dark (or -dark@2) are the dark-variant assets."""
    base = filename.replace("@2", "")
    return base.endswith("-dark.png")


def generate_gtk3_assets(theme: str, dark_rgb: tuple, light_rgb: tuple) -> None:
    src_dir = ROOT / "src" / "gtk" / "assets"
    dst_dir = ROOT / "src" / "gtk" / f"assets-{theme}"
    dst_dir.mkdir(parents=True, exist_ok=True)

    for png in sorted(src_dir.glob("*.png")):
        target = light_rgb if is_dark_asset(png.name) else dark_rgb
        source = SOURCE_REFS["light"]["rgb"] if is_dark_asset(png.name) else SOURCE_REFS["dark"]["rgb"]
        recolor_png(png, dst_dir / png.name, target, source)


def generate_gtk2_assets(theme: str, dark_rgb: tuple, light_rgb: tuple) -> None:
    base = ROOT / "src" / "gtk-2.0" / "assets-folder"
    for src_name, dst_suffix in (("assets", f"assets-{theme}"), ("assets-Dark", f"assets-{theme}-Dark")):
        src_dir = base / src_name
        dst_dir = base / dst_suffix
        if not src_dir.exists():
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        # assets/ maps to dark primary; assets-Dark/ maps to light primary
        target = dark_rgb if src_name == "assets" else light_rgb
        source = SOURCE_REFS["dark"]["rgb"] if src_name == "assets" else SOURCE_REFS["light"]["rgb"]
        for png in sorted(src_dir.glob("*.png")):
            recolor_png(png, dst_dir / png.name, target, source)


def sed_replace(text: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def generate_gtk2_gtkrc(theme: str, dark_rgb: tuple, light_rgb: tuple) -> None:
    base = ROOT / "src" / "gtk-2.0"
    dark_hex = "#{:02x}{:02x}{:02x}".format(*dark_rgb)
    light_hex = "#{:02x}{:02x}{:02x}".format(*light_rgb)

    for src_name, dst_name in (("gtkrc", f"gtkrc-{theme}"), ("gtkrc-Dark", f"gtkrc-{theme}-Dark")):
        src = base / src_name
        if not src.exists():
            continue
        dst = base / dst_name
        # The base gtkrc files both reference #0078D4/#1A73E8; map them to the
        # accent of the variant this file will be installed for. Previously the
        # dark gtkrc always got the *light* accent, so GTK2 dark themes showed
        # the wrong (darker) selection colour.
        accent = dark_hex if src_name == "gtkrc" else light_hex
        text = src.read_text()
        text = sed_replace(text, [
            ("#0078D4", accent.upper()),
            ("#0078d4", accent.lower()),
            ("#1A73E8", accent.upper()),
            ("#1a73e8", accent.lower()),
            ("#3281EA", light_hex.upper()),
            ("#3281ea", light_hex.lower()),
        ])
        dst.write_text(text)


def generate_shell_svgs(theme: str, dark_rgb: tuple) -> None:
    src_dir = ROOT / "src" / "gnome-shell" / "theme"
    dst_dir = ROOT / "src" / "gnome-shell" / f"theme-{theme}"
    dst_dir.mkdir(parents=True, exist_ok=True)

    dark_hex = "#{:02x}{:02x}{:02x}".format(*dark_rgb)
    for svg in sorted(src_dir.glob("*.svg")):
        text = svg.read_text()
        text = sed_replace(text, [
            ("#0078D4", dark_hex.upper()),
            ("#0078d4", dark_hex.lower()),
            ("#1A73E8", dark_hex.upper()),
            ("#1a73e8", dark_hex.lower()),
            ("#3281EA", dark_hex.upper()),
            ("#3281ea", dark_hex.lower()),
        ])
        (dst_dir / svg.name).write_text(text)


def generate_gtk_svgs(theme: str, dark_rgb: tuple, light_rgb: tuple) -> None:
    """Generate src/gtk/assets-<theme>.svg from assets.svg via sed."""
    src = ROOT / "src" / "gtk" / "assets.svg"
    dst = ROOT / "src" / "gtk" / f"assets-{theme}.svg"
    dark_hex = "#{:02x}{:02x}{:02x}".format(*dark_rgb)
    light_hex = "#{:02x}{:02x}{:02x}".format(*light_rgb)
    text = src.read_text()
    text = sed_replace(text, [
        ("#1A73E8", dark_hex.upper()),
        ("#1a73e8", dark_hex.lower()),
        ("#3281EA", light_hex.upper()),
        ("#3281ea", light_hex.lower()),
    ])
    dst.write_text(text)


def generate_gtk2_svgs(theme: str, dark_rgb: tuple, light_rgb: tuple) -> None:
    base = ROOT / "src" / "gtk-2.0" / "assets-folder"
    dark_hex = "#{:02x}{:02x}{:02x}".format(*dark_rgb)
    light_hex = "#{:02x}{:02x}{:02x}".format(*light_rgb)
    for src_name, dst_name in (("assets.svg", f"assets-{theme}.svg"), ("assets-Dark.svg", f"assets-{theme}-Dark.svg")):
        src = base / src_name
        if not src.exists():
            continue
        dst = base / dst_name
        text = src.read_text()
        text = sed_replace(text, [
            ("#0078D4", dark_hex.upper()),
            ("#0078d4", dark_hex.lower()),
            ("#1A73E8", dark_hex.upper()),
            ("#1a73e8", dark_hex.lower()),
            ("#3281EA", light_hex.upper()),
            ("#3281ea", light_hex.lower()),
        ])
        dst.write_text(text)


def _remove_path(path: Path) -> None:
    """Best-effort removal of a file or directory; ignore ENOENT."""
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    except FileNotFoundError:
        pass


def clean_old_variant_dirs() -> None:
    """Remove legacy btop variant directories/files that are being replaced."""
    legacy_themes = [
        "adapta", "ayu", "dracula", "dusklight", "everforest", "flexoki-dark",
        "gotham", "gruvbox", "horizon", "kanagawa-wave", "monokai", "nord",
        "onedark", "solarized-dark", "tokyo-night",
    ]
    # GTK3
    gtk_assets = ROOT / "src" / "gtk"
    for t in legacy_themes:
        for path in (gtk_assets / f"assets-{t}", gtk_assets / f"assets-{t}.svg"):
            _remove_path(path)
        for path in gtk_assets.glob(f"thumbnail-{t}*.png"):
            _remove_path(path)
    # GTK2
    gtk2_folder = ROOT / "src" / "gtk-2.0" / "assets-folder"
    for t in legacy_themes:
        for path in (gtk2_folder / f"assets-{t}", gtk2_folder / f"assets-{t}-Dark",
                     gtk2_folder / f"assets-{t}.svg", gtk2_folder / f"assets-{t}-Dark.svg"):
            _remove_path(path)
        for path in (ROOT / "src" / "gtk-2.0" / f"gtkrc-{t}", ROOT / "src" / "gtk-2.0" / f"gtkrc-{t}-Dark"):
            _remove_path(path)
    # Shell
    shell_themes = ROOT / "src" / "gnome-shell"
    for t in legacy_themes:
        _remove_path(shell_themes / f"theme-{t}")
    # Cinnamon thumbnails
    cinnamon = ROOT / "src" / "cinnamon"
    for t in legacy_themes:
        for path in cinnamon.glob(f"thumbnail-{t}*.png"):
            _remove_path(path)


def generate_thumbnails(theme: str, dark_rgb: tuple) -> None:
    """Recolor the blue accent in base thumbnail PNGs for each theme."""
    source = SOURCE_REFS["dark"]["rgb"]  # thumbnails use #0078d4 family
    base_names = {"thumbnail.png", "thumbnail-Light.png", "thumbnail-Dark.png"}
    for subdir in (ROOT / "src" / "gtk", ROOT / "src" / "cinnamon"):
        for src in subdir.glob("thumbnail*.png"):
            if src.name not in base_names:
                continue  # skip already-themed thumbnails
            dst_name = src.name.replace("thumbnail", f"thumbnail-{theme}")
            recolor_png(src, subdir / dst_name, dark_rgb, source)


def main() -> int:
    clean_old_variant_dirs()

    for theme, colors in THEMES.items():
        print(f"Generating assets for {theme} ...")
        dark_rgb = colors["dark"]
        light_rgb = colors["light"]
        generate_gtk_svgs(theme, dark_rgb, light_rgb)
        generate_gtk3_assets(theme, dark_rgb, light_rgb)
        generate_gtk2_svgs(theme, dark_rgb, light_rgb)
        generate_gtk2_assets(theme, dark_rgb, light_rgb)
        generate_gtk2_gtkrc(theme, dark_rgb, light_rgb)
        generate_shell_svgs(theme, dark_rgb)
        generate_thumbnails(theme, dark_rgb)

    print("All theme assets generated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
