#!/usr/bin/env python3
"""Check the theme's light and dark palettes against WCAG contrast targets.

Reads the `:root[data-theme="light"]` and `:root[data-theme="dark"]` blocks
from src/cavanagh-nzbfast.css (the Auto blocks are kept identical to them,
which this script also verifies) and checks the colour pairs nzbfast
actually paints.
"""
import pathlib
import re
import sys

SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "cavanagh-nzbfast.css"

# (foreground, background, minimum ratio). "#fff" is the literal white
# nzbfast uses for text on accent-filled buttons and chips.
PAIRS = [
    ("--fg", "--bg", 7.0),
    ("--fg", "--surface", 7.0),
    ("--fg", "--surface-2", 7.0),
    ("--dim", "--bg", 4.5),
    ("--dim", "--surface", 4.5),
    ("--dim", "--surface-2", 4.5),
    ("#fff", "--acc", 4.5),
    ("--acc", "--surface", 3.0),
    ("--ok", "--bg", 4.5),
    ("--ok", "--surface", 4.5),
    ("--warn", "--bg", 4.5),
    ("--warn", "--surface", 4.5),
    ("--bad", "--bg", 4.5),
    ("--bad", "--surface", 4.5),
]


def lum(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    chans = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    chans = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in chans]
    return 0.2126 * chans[0] + 0.7152 * chans[1] + 0.0722 * chans[2]


def ratio(a: str, b: str) -> float:
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def block(css: str, selector: str) -> dict:
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    if not m:
        sys.exit(f"contrast: block {selector} not found")
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)))


def main() -> None:
    css = SRC.read_text()
    failed = False
    for theme in ("light", "dark"):
        explicit = block(css, f':root[data-theme="{theme}"]')
        media = re.search(r"@media \(prefers-color-scheme: " + theme + r"\)\s*\{(.*?\})\s*\}", css, re.S)
        auto = block(media.group(1), ":root:not([data-theme])") if media else None
        if auto != explicit:
            print(f"FAIL {theme}: Auto block differs from the explicit data-theme block")
            failed = True
        for fg, bg, minimum in PAIRS:
            a = explicit.get(fg, fg).strip()
            b = explicit[bg].strip()
            r = ratio(a, b)
            ok = r >= minimum
            failed |= not ok
            print(f"{'ok  ' if ok else 'FAIL'} {theme:5} {fg:>9} on {bg:<11} {r:5.2f}:1 (min {minimum})")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
