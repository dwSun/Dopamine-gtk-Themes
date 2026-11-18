#!/usr/bin/env python3
"""Render the README colour cards as SVG.

Why SVG: README thumbnails shrink a 640x360 window mock until the palette is
unreadable, and raster previews blur the hex labels. These cards are drawn
straight from ``src/_sass/_theme-palettes.scss`` (via ``palette_utils``) and
stay sharp at any size, with every core colour value printed next to its chip.

Outputs:
  assets/preview/overview.svg            one row per variant, dark + light
  assets/preview/palettes/<name>.svg     full card for one variant
"""
from __future__ import annotations

import sys
from pathlib import Path

from palette_utils import ROOT, parse_palettes

OUT_DIR = ROOT / "assets/preview"
CARDS_DIR = OUT_DIR / "palettes"

# Roles shown on a variant card, in reading order.
CARD_ROLES = [
    ("background", "background"),
    ("surface", "surface"),
    ("base", "base"),
    ("base-alt", "base-alt"),
    ("primary", "accent"),
    ("foreground", "text"),
    ("link", "link"),
    ("error", "error"),
]


FONT = "Inter, 'Noto Sans CJK SC', 'Noto Sans', 'DejaVu Sans', sans-serif"
MONO = "'JetBrains Mono', 'Maple Mono', 'DejaVu Sans Mono', monospace"


def rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


def rel_lum(value: str) -> float:
    def f(c: float) -> float:
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (f(c) for c in rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ink(value: str, dark: str = "#141418", light: str = "#FFFFFF") -> str:
    return dark if rel_lum(value) > 0.42 else light


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def variant_card(name: str, modes: dict[str, dict[str, str]]) -> str:
    """820x262 card: dark block on the left, light block on the right."""
    W, H = 820, 262
    pad = 18
    block_w = (W - 2 * pad - 16) / 2
    head_h = 34
    chip_w = (block_w - 3 * 6) / 4
    chip_h = 48
    row_gap = 20

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(name)} palette">',
        f'<rect width="{W}" height="{H}" rx="12" fill="#FFFFFF"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="#E4E4E7"/>',
    ]

    for idx, (mode, label, card_bg, card_border) in enumerate((
        ("dark", "DARK", "#151519", "#2A2A33"),
        ("light", "LIGHT", "#FAFAFB", "#E7E7EC"),
    )):
        roles = modes.get(mode)
        if not roles:
            continue
        bx = pad + idx * (block_w + 16)
        by = pad
        parts.append(
            f'<rect x="{bx:.1f}" y="{by}" width="{block_w:.1f}" height="{H - 2 * pad}" '
            f'rx="10" fill="{card_bg}" stroke="{card_border}"/>'
        )
        name_ink = "#FFFFFF" if mode == "dark" else "#18181B"
        sub_ink = "#A1A1AA" if mode == "dark" else "#71717A"
        parts.append(
            f'<text x="{bx + 14:.1f}" y="{by + 24}" font-family="{FONT}" font-size="15" '
            f'font-weight="600" fill="{name_ink}">{esc(name)}</text>'
        )
        parts.append(
            f'<text x="{bx + 14 + 8 * len(name) + 10:.1f}" y="{by + 24}" font-family="{MONO}" '
            f'font-size="10" letter-spacing="1.2" fill="{sub_ink}">{label}</text>'
        )

        for i, (role, text) in enumerate(CARD_ROLES):
            col, row = i % 4, i // 4
            cx = bx + 14 + col * (chip_w + 6)
            cy = by + head_h + row * (chip_h + row_gap)
            value = roles[role]
            fg = ink(value)
            parts.append(
                f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{chip_w:.1f}" height="{chip_h}" '
                f'rx="6" fill="{value}" stroke="rgba(0,0,0,0.10)"/>'
            )
            # label inside the chip, hex underneath
            parts.append(
                f'<text x="{cx + 7:.1f}" y="{cy + 16:.1f}" font-family="{FONT}" font-size="9.5" '
                f'fill="{fg}" opacity="0.85">{esc(text)}</text>'
            )
            parts.append(
                f'<text x="{cx + 7:.1f}" y="{cy + chip_h - 8:.1f}" font-family="{MONO}" '
                f'font-size="11" fill="{fg}">{value.upper()}</text>'
            )

        # surface-area strip: how much of a window each layer covers
        sy = by + H - 2 * pad - 46
        segs = (("surface", 0.32), ("base", 0.50), ("primary", 0.18))
        sx = bx + 14
        total = block_w - 28
        for role, share in segs:
            sw = total * share
            value = roles[role]
            parts.append(
                f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="14" fill="{value}"/>'
            )
            sx += sw
        parts.append(
            f'<text x="{bx + 14:.1f}" y="{sy + 28:.1f}" font-family="{FONT}" font-size="9" '
            f'fill="{sub_ink}">surface · base · accent coverage</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def overview(palettes: dict[str, dict[str, dict[str, str]]]) -> str:
    names = list(palettes)
    W = 860
    row_h = 26
    gap = 10
    head = 46
    H = head + len(names) * (row_h + gap) + 12
    label_w = 118
    chip_w = 58
    group_gap = 10

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="Dopamine palette overview">',
        f'<rect width="{W}" height="{H}" rx="12" fill="#FFFFFF"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="#E4E4E7"/>',
        f'<text x="18" y="28" font-family="{FONT}" font-size="13" font-weight="600" fill="#18181B">'
        f'Dopamine palettes</text>',
        f'<text x="{18 + label_w}" y="27" font-family="{MONO}" font-size="9" letter-spacing="1.1" '
        f'fill="#71717A">DARK · bg / surface / base / accent</text>',
        f'<text x="{18 + label_w + 4 * chip_w + 4 * 4 + group_gap + 14}" y="27" '
        f'font-family="{MONO}" font-size="9" letter-spacing="1.1" fill="#71717A">'
        f'LIGHT · bg / surface / base / accent</text>',
    ]

    role_names = ("background", "surface", "base", "primary")
    for i, name in enumerate(names):
        y = head + i * (row_h + gap)
        parts.append(
            f'<text x="18" y="{y + 17}" font-family="{FONT}" font-size="12" fill="#18181B">'
            f'{esc(name)}</text>'
        )
        x = 18 + label_w
        for mode, group in (("dark", 0), ("light", 1)):
            roles = palettes[name].get(mode, {})
            if group == 1:
                x += group_gap
            for role in role_names:
                value = roles.get(role)
                if not value:
                    x += chip_w + 4
                    continue
                parts.append(
                    f'<rect x="{x:.1f}" y="{y}" width="{chip_w}" height="{row_h}" rx="4" '
                    f'fill="{value}"/>'
                )
                x += chip_w + 4
            x += 8
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    palettes = parse_palettes()
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    for name, modes in palettes.items():
        (CARDS_DIR / f"{name}.svg").write_text(variant_card(name, modes), encoding="utf-8")
        print(f"wrote {CARDS_DIR / f'{name}.svg'}")
    (OUT_DIR / "overview.svg").write_text(overview(palettes), encoding="utf-8")
    print(f"wrote {OUT_DIR / 'overview.svg'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
