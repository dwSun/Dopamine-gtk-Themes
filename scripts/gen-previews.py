#!/usr/bin/env python3
"""
Generate README preview images for every Dopamine variant.

Palettes are parsed straight out of ``src/_sass/_theme-palettes.scss`` so the
pictures can never drift away from the shipped CSS again (the old version kept
a hand-copied dict and silently missed the five dopamine variants, which is why
README's "berry" used to be a solid pink rectangle instead of a theme).

Each preview is a 640x360 mock window rendered from the real palette roles:

  titlebar + traffic lights · sidebar (surface) · content (base)
  selected row (accent) · suggested button (accent) · switch · progress bar

Usage:
    python3 scripts/gen-previews.py [OUTPUT_DIR]
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from palette_utils import ROOT, PALETTE_SCSS, parse_palettes

FONT_DIR = Path("/usr/share/fonts/MapleMonoNormal-NF-CN")
FONT_FILES = {
    "regular": FONT_DIR / "MapleMonoNormal-NF-CN-Regular.ttf",
    "light": FONT_DIR / "MapleMonoNormal-NF-CN-Light.ttf",
    "medium": FONT_DIR / "MapleMonoNormal-NF-CN-Medium.ttf",
    "bold": FONT_DIR / "MapleMonoNormal-NF-CN-Bold.ttf",
}

W, H = 640, 360

# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------
def hex2rgb(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def mix(a: str, b: str, t: float) -> tuple[int, int, int]:
    """Blend hex a -> b by t (0 = a, 1 = b), returning RGB."""
    ra, ga, ba = hex2rgb(a)
    rb, gb, bb = hex2rgb(b)
    return (
        round(ra + (rb - ra) * t),
        round(ga + (gb - ga) * t),
        round(ba + (bb - ba) * t),
    )


def brightness(rgb: tuple[int, int, int]) -> float:
    return (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000


def ink_on(pal: dict[str, str], bg_hex: str) -> tuple[int, int, int]:
    """Text colour GTK would pick on top of ``bg_hex`` (mirrors on())."""
    role = "foreground-on-light" if brightness(hex2rgb(bg_hex)) >= 156 else "foreground-on-dark"
    return hex2rgb(pal[role])


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    # Fall back to Pillow's bundled font if Maple Mono Nerd is unavailable.
    path = FONT_FILES.get(kind, FONT_FILES["regular"])
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size)


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------
def draw_preview(
    name: str,
    mode: str,
    pal: dict[str, str],
    out: Path,
) -> None:
    accent = pal["primary"]
    bg = pal["background"]
    surface = pal["surface"]
    base = pal["base"]
    base_alt = pal["base-alt"]
    titlebar = pal.get("titlebar", bg)
    fg = hex2rgb(pal["foreground"])
    fg_dim = hex2rgb(pal["foreground-secondary"])
    accent_rgb = hex2rgb(accent)
    on_accent = ink_on(pal, accent)

    img = Image.new("RGB", (W, H), hex2rgb(bg))
    d = ImageDraw.Draw(img)

    # --- window shell -----------------------------------------------------
    wx0, wy0, wx1, wy1 = 18, 16, W - 18, H - 16
    d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=12, fill=hex2rgb(bg),
                        outline=hex2rgb(base_alt), width=1)

    tb_h = 40
    d.rounded_rectangle([wx0, wy0, wx1, wy0 + tb_h], radius=12, fill=hex2rgb(titlebar))
    d.rectangle([wx0, wy0 + tb_h - 12, wx1, wy0 + tb_h], fill=hex2rgb(titlebar))
    d.line([wx0 + 1, wy0 + tb_h, wx1 - 1, wy0 + tb_h], fill=hex2rgb(base_alt))

    # accent marker + title
    f_title = font("medium", 13)
    f_small = font("light", 10)
    d.rounded_rectangle([wx0 + 16, wy0 + 13, wx0 + 20, wy0 + tb_h - 13], radius=2, fill=accent_rgb)
    d.text((wx0 + 30, wy0 + 11), "Dopamine", fill=fg, font=f_title)
    tw = d.textlength("Dopamine", font=f_title)
    d.text((wx0 + 34 + tw, wy0 + 12), f"· {name}", fill=fg_dim, font=f_title)

    # traffic lights (GTK order from right: close, minimize, maximize)
    dot_r = 5
    for idx, role in enumerate(("error", "warning", "success")):
        cx = wx1 - 22 - idx * 18
        cy = wy0 + tb_h // 2
        d.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
                  fill=hex2rgb(pal[role]))

    # --- sidebar ----------------------------------------------------------
    sx0, sy0, sx1, sy1 = wx0 + 1, wy0 + tb_h + 1, wx0 + 168, wy1 - 1
    d.rectangle([sx0, sy0, sx1, sy1], fill=hex2rgb(surface))
    d.line([sx1, sy0, sx1, sy1], fill=hex2rgb(base_alt))

    f_item = font("regular", 12)
    items = ["Files", "Recent", "Starred", "Trash"]
    for i, label in enumerate(items):
        y = sy0 + 14 + i * 34
        if i == 0:
            sel = mix(surface, accent, 0.22)
            d.rounded_rectangle([sx0 + 8, y - 6, sx1 - 10, y + 22], radius=6, fill=sel)
            d.rounded_rectangle([sx0 + 8, y + 2, sx0 + 11, y + 14], radius=2, fill=accent_rgb)
            d.text((sx0 + 20, y - 2), label, fill=on_accent if brightness(sel) > 156 else fg, font=f_item)
        else:
            d.text((sx0 + 20, y - 2), label, fill=fg_dim, font=f_item)

    # sidebar footer: user chip
    d.ellipse([sx0 + 14, sy1 - 34, sx0 + 34, sy1 - 14], fill=accent_rgb)
    d.text((sx0 + 42, sy1 - 31), "david", fill=fg_dim, font=f_small)

    # --- content ----------------------------------------------------------
    cx0 = sx1 + 1
    d.rectangle([cx0, sy0, wx1 - 1, sy1], fill=hex2rgb(base))

    d.text((cx0 + 18, sy0 + 14), "Recent files", fill=fg, font=font("medium", 13))
    d.text((cx0 + 18, sy0 + 34), "selected row uses the accent colour", fill=fg_dim, font=f_small)

    rows = [("berry-report.png", "2.4 MB"), ("palette-notes.md", "12 KB"), ("preview.png", "340 KB")]
    row_y = sy0 + 58
    for i, (label, meta) in enumerate(rows):
        y = row_y + i * 38
        if i == 1:
            d.rounded_rectangle([cx0 + 12, y - 6, wx1 - 14, y + 26], radius=6, fill=accent_rgb)
            d.text((cx0 + 22, y + 2), label, fill=on_accent, font=f_item)
            w = d.textlength(meta, font=f_small)
            d.text((wx1 - 26 - w, y + 4), meta, fill=on_accent, font=f_small)
        else:
            d.text((cx0 + 22, y + 2), label, fill=fg, font=f_item)
            w = d.textlength(meta, font=f_small)
            d.text((wx1 - 26 - w, y + 4), meta, fill=fg_dim, font=f_small)

    # --- widgets ----------------------------------------------------------
    wy = row_y + 3 * 38 + 4
    # progress bar
    d.text((cx0 + 18, wy), "progress", fill=fg_dim, font=f_small)
    d.rounded_rectangle([cx0 + 18, wy + 16, cx0 + 178, wy + 24], radius=4, fill=hex2rgb(base_alt))
    d.rounded_rectangle([cx0 + 18, wy + 16, cx0 + 118, wy + 24], radius=4, fill=accent_rgb)

    # switch (on)
    d.text((cx0 + 200, wy), "switch", fill=fg_dim, font=f_small)
    d.rounded_rectangle([cx0 + 200, wy + 14, cx0 + 238, wy + 30], radius=8, fill=accent_rgb)
    d.ellipse([cx0 + 222, wy + 16, cx0 + 236, wy + 30], fill=(255, 255, 255))

    # buttons
    by = wy + 44
    d.rounded_rectangle([cx0 + 18, by, cx0 + 104, by + 26], radius=6, fill=accent_rgb)
    bw = d.textlength("Suggested", font=f_small)
    d.text((cx0 + 61 - bw / 2, by + 7), "Suggested", fill=on_accent, font=f_small)
    d.rounded_rectangle([cx0 + 112, by, cx0 + 190, by + 26], radius=6,
                        fill=hex2rgb(surface), outline=hex2rgb(base_alt), width=1)
    bw = d.textlength("Cancel", font=f_small)
    d.text((cx0 + 151 - bw / 2, by + 7), "Cancel", fill=fg, font=f_small)

    # --- footer caption ---------------------------------------------------
    cap = f"accent {accent}   ·   background {bg}   ·   base {base}"
    d.text((wx0 + 16, H - 34), cap, fill=fg_dim, font=font("light", 10))
    tag = mode.upper()
    wtag = d.textlength(tag, font=f_small)
    d.text((wx1 - 16 - wtag, H - 34), tag, fill=accent_rgb, font=f_small)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out}  ({name} {mode})")


def make_contact_sheet(out_dir: Path, palettes: dict, mode: str) -> None:
    """Paste all previews of one mode into a single review sheet."""
    cols, thumb_w = 3, 400
    gap, margin = 12, 16
    names = [n for n, modes in palettes.items() if mode in modes]
    rows = (len(names) + cols - 1) // cols
    thumb_h = thumb_w * H // W
    sheet = Image.new("RGB", (2 * margin + cols * thumb_w + (cols - 1) * gap,
                              2 * margin + rows * thumb_h + (rows - 1) * gap), (24, 24, 24))
    for i, name in enumerate(names):
        src = out_dir / f"{name}-{mode}.png"
        if not src.exists():
            continue
        img = Image.open(src).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        x = margin + (i % cols) * (thumb_w + gap)
        y = margin + (i // cols) * (thumb_h + gap)
        sheet.paste(img, (x, y))
    out = out_dir / f"contact-sheet-{mode}.png"
    sheet.save(out, format="PNG", optimize=True)
    print(f"wrote {out}")


def main() -> int:
    positional = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_dir = Path(positional[0]) if positional else ROOT / "assets/preview"
    palettes = parse_palettes()
    if not palettes:
        print(f"ERROR: no palettes parsed from {PALETTE_SCSS}", file=sys.stderr)
        return 1
    for name, modes in palettes.items():
        for mode in ("light", "dark"):
            if mode not in modes:
                continue
            draw_preview(name, mode, modes[mode], out_dir / f"{name}-{mode}.png")
    print(f"{len(palettes)} palettes written to {out_dir}")
    if "--contact-sheet" in sys.argv:
        for mode in ("dark", "light"):
            make_contact_sheet(out_dir, palettes, mode)
    return 0


if __name__ == "__main__":
    sys.exit(main())
