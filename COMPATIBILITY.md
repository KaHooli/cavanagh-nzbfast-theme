# nzbfast frontend compatibility

Last reviewed: **4 October 2026**

This theme was reviewed against nzbfast **v1.7.1** (upstream `main` at
`370da77`, 26 September 2026). It was rendered in Chromium against the
dashboard and wall HTML from that commit in the Light, Dark, Auto and High
contrast themes, at desktop and phone widths.

## How nzbfast loads the theme

- `GET /custom.css` serves `custom.css` from the folder that holds
  `config.json` (`crates/nzbfast-api/src/assets.rs`, `USER_CSS_FILE`). The
  file is read from disk on each request and sent with an ETag. A missing
  file returns an empty `200`.
- Files over **1 MiB** are refused (`USER_CSS_MAX`). The built theme is about
  33 KB, and `tools/build.py` fails if it grows past 128 KB.
- `web/dashboard.html` and `web/wall.html` link the file **last** in
  `<head>`, after the shared tokens and each page's own `<style>`. At equal
  specificity, the theme wins.
- `web/login.html` does **not** link the file, by design. The manual pages do
  not link it either.
- No other file is served from the config folder, so every asset is embedded
  in the stylesheet.

## Tokens the theme overrides

All of these come from `web/ui-tokens.html`, which the dashboard, the wall and
the manual share:

`color-scheme`, `--bg`, `--surface`, `--surface-2`, `--fg`, `--dim`, `--line`,
`--acc`, `--acc2`, `--ok`, `--warn`, `--bad`, `--gold`, `--code`, `--mark`.

The chart series (`--p0`–`--p5`) and identity colours (`--id0`–`--id5`) are
left alone. They are tuned for separation, and the colour-blind-safe palette
setting changes them.

nzbfast derives `--ctl-*` (header control fills) from `--acc`, `--surface`,
`--fg` and `--line`, so those follow the theme automatically.

### Theme selection model

nzbfast stores its theme in `localStorage.nzbfastTheme` and sets
`data-theme` on `<html>` before first paint. Auto means the attribute is
absent and `prefers-color-scheme` decides. The theme mirrors this model:

| Selector | Palette |
| --- | --- |
| `:root[data-theme="light"]` | Cavanagh light |
| `:root[data-theme="dark"]` | Cavanagh dark |
| `:root:not([data-theme])` inside `@media (prefers-color-scheme: …)` | Cavanagh light/dark (Auto) |
| `:root[data-theme="contrast"]` | not touched |

`tools/check_contrast.py` fails if the Auto blocks drift from the explicit
blocks.

### User settings layers

nzbfast applies Settings > Interface choices as attribute layers
(`data-accent`, `data-userbg`, `data-usersurface`, `data-userfg`,
`data-border`). These have the same specificity as the theme's palette
blocks, and the theme loads later, so the palettes would win over them. The
theme therefore restates those layer rules at the end of the file. Verified:
a user accent, background and strong border all take effect with the theme
installed.

## Page selectors the theme relies on

These are not part of the token API. Recheck them after each nzbfast upgrade.

| Selector | Page | Purpose |
| --- | --- | --- |
| `header h1 .logo > svg.ic` | dashboard | Hide the bolt glyph |
| `header h1 .logo::before` | dashboard | Draw the crest |
| `.wrap > header` | dashboard | Gold rule under the header |
| `.bar h1 a > svg.ic`, `.bar h1 a::before` | wall | Bolt glyph and crest |
| `body > .bar` | wall | Gold bottom border on the sticky bar |
| `body` | both | Background glow (skipped when the user sets a background) |

`body > .bar` is scoped deliberately: the dashboard also uses `.bar` for
progress bars.

The wall hides `.bar h1 a span` and `.bar h1 a::after` below 700 px. The theme
uses `::before`, so the crest stays visible on phones.

## Upgrade test checklist

After each nzbfast release, check the following:

- [ ] `/custom.css` is still linked last in the dashboard and wall `<head>`
- [ ] the token names in `web/ui-tokens.html` are unchanged
- [ ] the user-layer rules at the end of `ui-tokens.html` still match the
      copies at the end of `src/cavanagh-nzbfast.css`
- [ ] the dashboard header still renders the crest, not the bolt, in Light,
      Dark and Auto
- [ ] the wall bar shows the crest on desktop and on a phone (< 700 px)
- [ ] High contrast is unchanged from stock nzbfast
- [ ] primary buttons (white text on the accent) are readable in both palettes
- [ ] queue/history status colours (ok, warn, bad) are distinguishable
- [ ] a custom accent and background from Settings > Interface override the
      theme
- [ ] the header nav pills sit at the same x position on the dashboard and on
      the wall
