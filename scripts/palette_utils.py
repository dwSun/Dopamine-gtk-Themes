#!/usr/bin/env python3
"""Single source of truth for the Dopamine palettes.

Both the README preview generator (``gen-previews.py``) and the asset
recolourer (``generate-theme-assets.py``) read colours from
``src/_sass/_theme-palettes.scss`` through this module, so no tool can drift
away from the CSS that actually ships.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTE_SCSS = ROOT / "src/_sass/_theme-palettes.scss"

ROLE_RE = re.compile(r"'([a-z-]+)'\s*:\s*(#[0-9A-Fa-f]{6})")


def parse_palettes(path: Path = PALETTE_SCSS) -> dict[str, dict[str, dict[str, str]]]:
    """Return {'berry': {'dark': {role: '#RRGGBB'}, 'light': {...}}, ...}.

    Role hexes are upper-cased; the ``default`` entry is included because it is
    the palette used when no ``-t`` variant is given.
    """
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"\n  '([a-z-]+)': \(", text)
    palettes: dict[str, dict[str, dict[str, str]]] = {}
    for i in range(1, len(parts), 2):
        name, body = parts[i], parts[i + 1]
        modes: dict[str, dict[str, str]] = {}
        for mode in ("dark", "light"):
            m = re.search(r"'%s': \((.*?)\n    \)," % mode, body, re.S)
            if not m:
                continue
            modes[mode] = {k: v.upper() for k, v in ROLE_RE.findall(m.group(1))}
        if modes:
            palettes[name] = modes
    return palettes


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


if __name__ == "__main__":
    for name, modes in parse_palettes().items():
        for mode, roles in modes.items():
            print(name, mode, roles["primary"], roles["background"], roles["base"])
