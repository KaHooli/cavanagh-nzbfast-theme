# Plan: Cavanagh Family theme for nzbfast

## Goal

Give the self-hosted nzbfast dashboard the same Cavanagh Family identity as
the authentik sign-in theme (palette, crest and typographic accents), using
only nzbfast's supported customisation point: `/config/custom.css`.

## How the authentik theme maps to nzbfast

| authentik theme | nzbfast equivalent | Decision |
| --- | --- | --- |
| Brand **Custom CSS** field | `custom.css` in the config folder | Ship one drop-in `custom.css` |
| `--ak-global--*` / PatternFly variables | Shared tokens in `web/ui-tokens.html` (`--bg`, `--surface`, `--acc`, ...) | Override tokens first; use page selectors only for the brand mark |
| `html[data-theme="light/dark"]` | `:root[data-theme]`, with no attribute for Auto | Mirror the model, including Auto by `prefers-color-scheme` |
| Uploaded logo, favicon and background files | Not possible: nzbfast serves only `custom.css` from the config folder | Embed the crest as a data URL; draw the background as a CSS gradient |
| FIDO mark embedded as a data URL | Same technique | Crest embedded as a 96 px PNG data URL (about 26 KB) |
| `::part()` exposed surfaces | No shadow DOM; plain classes | A small, documented set of selectors in `COMPATIBILITY.md` |
| "Powered by authentik" footer hidden | Nothing equivalent | Not needed |
| Wide 7:1 wordmark | Header `h1` (crest + "nzbfast") | Crest replaces the bolt; the name is set in a serif face, in brand colour |

## Constraints found in nzbfast's source

1. `custom.css` is the only user file served, and it is capped at 1 MiB, so
   every asset must be inline and small.
2. It is linked last in the dashboard and wall `<head>`, so equal specificity
   wins without `!important`.
3. It is **not** linked on `/login` or `/manual`, so those pages stay stock.
   Changing this would need an upstream change.
4. `<meta name="theme-color">`, the favicon and the PWA icons cannot be
   changed from CSS.
5. `--acc` is used both as a fill under white text and as text on surfaces,
   so the dark-mode accent has to balance the two (it is lifted to
   `#CC3D42`).
6. The user layers in Settings > Interface (accent, background, surface,
   text, border) have the same specificity as theme blocks, so the theme must
   restate them last to keep the user's choice in charge.
7. High contrast is an accessibility theme and must not be restyled.

## Delivered in 1.0.0

- [x] Repository skeleton: README, PLAN, COMPATIBILITY, VERSION, .gitignore
- [x] `src/cavanagh-nzbfast.css`: light, dark and Auto palettes, crest,
      serif wordmark, gold header rule, oxblood glow, user-layer
      restatement
- [x] `tools/build.py`: embeds the crest, stamps the version, enforces a
      size budget, and has a `--check` mode
- [x] `tools/check_contrast.py`: WCAG checks for both palettes, plus a check
      that the Auto and explicit blocks match
- [x] GitHub Actions workflow that runs the build check and the contrast
      check on every push and PR
- [x] Rendered verification of the dashboard and wall from nzbfast v1.7.1:
      Light, Dark, Auto-light, High contrast, and the wall at phone width
- [x] `theme-preview.jpg`

## Possible follow-ups

- **Theme sign-in:** propose upstream (a follow-up to nzbfast/nzbfast#31) an opt-in
  setting to link `custom.css` on `/login`. The page's comment explains why it
  is not linked today, so this needs the maintainer's agreement.
- **Theme-aware crest:** the authentik package has light and dark icon SVGs,
  but they embed about 460 KB of raster each, so they are too heavy to inline
  twice. A vector redraw of the crest would allow a crisp, theme-aware mark at
  any zoom.
- **Card accents:** a gold top border on `.card` headers or on the
  throughput card. Left out of 1.0 to keep the page-selector surface small.
- **Release zip:** attach `custom.css` to tagged GitHub releases so a stable
  URL exists per version (for example
  `.../releases/download/v1.0.0/custom.css`).
- **Upstream watch:** an action that diffs `web/ui-tokens.html` on nzbfast
  `main` and opens an issue when token names change.
