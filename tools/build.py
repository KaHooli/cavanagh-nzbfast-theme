#!/usr/bin/env python3
"""Build the drop-in `custom.css` from `src/cavanagh-nzbfast.css`.

nzbfast serves exactly one file from its config folder - `custom.css` -
so the crest is embedded as a base64 data URL rather than referenced.

Usage:
    tools/build.py           write custom.css
    tools/build.py --check   exit 1 if custom.css is out of date
"""
import base64
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "cavanagh-nzbfast.css"
OUT = ROOT / "custom.css"
CREST = ROOT / "branding" / "cavanagh-crest-96.png"
VERSION = (ROOT / "VERSION").read_text().strip()

# nzbfast refuses to serve a custom.css larger than 1 MiB (USER_CSS_MAX in
# crates/nzbfast-api/src/assets.rs). Stay far below it: the file is read
# and gzipped on every page load.
MAX_BYTES = 128 * 1024


def build() -> str:
    crest = base64.b64encode(CREST.read_bytes()).decode("ascii")
    css = SRC.read_text()
    for token, value in {
        "__CAVANAGH_CREST__": f"data:image/png;base64,{crest}",
        "__VERSION__": VERSION,
    }.items():
        if token not in css:
            sys.exit(f"build: placeholder {token} missing from {SRC.name}")
        css = css.replace(token, value)
    if len(css.encode()) > MAX_BYTES:
        sys.exit(f"build: custom.css is {len(css.encode())} bytes, over {MAX_BYTES}")
    return css


def main() -> None:
    css = build()
    if "--check" in sys.argv[1:]:
        if not OUT.exists() or OUT.read_text() != css:
            sys.exit("custom.css is out of date: run tools/build.py and commit the result")
        print(f"custom.css is up to date ({len(css.encode())} bytes)")
        return
    OUT.write_text(css)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(css.encode())} bytes)")


if __name__ == "__main__":
    main()
