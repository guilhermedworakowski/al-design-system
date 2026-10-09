# AL Design System

[![npm](https://img.shields.io/npm/v/al-design-system)](https://www.npmjs.com/package/al-design-system)
[![license](https://img.shields.io/github/license/guilhermedworakowski/al-design-system)](LICENSE)
[![build](https://github.com/guilhermedworakowski/al-design-system/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/guilhermedworakowski/al-design-system/actions/workflows/build.yml)

An open-source design system, from Figma to code. Plain CSS, a little vanilla JavaScript only where CSS can't reach, and no dependencies.

**English** · [Português](README.pt-BR.md) · [Documentation site](https://al.guilhermedesignd.com)

## What it is

- **Foundation + 23 components**, designed in Figma and coded from the same tokens.
- **Light and dark themes** built in. It follows the operating system by default, and you can force one.
- **Accessibility is checked by the build.** Every rendered combination (variant × state × theme) is measured for contrast against the background it actually sits on, and each component's markup contract is verified. If something fails, the build stops.
- **Nothing is typed by hand.** Tokens, CSS variables, `tokens.json` and the documentation tables are all generated from one source.

## Components

| Group | Component | Script | Guidelines |
|---|---|:---:|---|
| Actions and display | Button | | [guidelines](src/components/button/guidelines.md) |
| | Icon | | (70 icons, see [Icons](#icons)) |
| | Icon Button | | [guidelines](src/components/icon-button/guidelines.md) |
| | Tag | | [guidelines](src/components/tag/guidelines.md) |
| | Avatar | | [guidelines](src/components/avatar/guidelines.md) |
| Forms | Select | | [guidelines](src/components/select/guidelines.md) |
| | Checkbox | | [guidelines](src/components/checkbox/guidelines.md) |
| | Radio | | [guidelines](src/components/radio/guidelines.md) |
| | Switch | | [guidelines](src/components/switch/guidelines.md) |
| | Input | | [guidelines](src/components/input/guidelines.md) |
| | Textarea | | [guidelines](src/components/textarea/guidelines.md) |
| | Password | ✓ | [guidelines](src/components/password/guidelines.md) |
| Structure and overlays | Divider | | [guidelines](src/components/divider/guidelines.md) |
| | Card | | [guidelines](src/components/card/guidelines.md) |
| | Tab | ✓ | [guidelines](src/components/tab/guidelines.md) |
| | Accordion | | [guidelines](src/components/accordion/guidelines.md) |
| | Modal | ✓ | [guidelines](src/components/modal/guidelines.md) |
| | Drawer | ✓ | [guidelines](src/components/drawer/guidelines.md) |
| Navigation | Sidebar | ✓ | [guidelines](src/components/sidebar/guidelines.md) |
| | Breadcrumb | ✓ | [guidelines](src/components/breadcrumb/guidelines.md) |
| Feedback | Tooltip | ✓ | [guidelines](src/components/tooltip/guidelines.md) |
| | Toast | ✓ | [guidelines](src/components/toast/guidelines.md) |
| | Alert | ✓ | [guidelines](src/components/alert/guidelines.md) |

Each guidelines file holds the usage rules (when to use it, when not to, content, behavior and accessibility) and, when there are any, the contrast exceptions the component declares.

## Install

```bash
npm install al-design-system
```

Or straight from a CDN, pinned to a version:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/al-design-system@1.0.1/dist/al.css">
```

Each [GitHub Release](https://github.com/guilhermedworakowski/al-design-system/releases) also carries the `dist/` folder as a zip.

### What's in the package

| File | What it is |
|---|---|
| `al.css` | Foundation + all 23 components, in one file |
| `foundation.css` | Only the Foundation: color, typography, spacing, radius, icon size, elevation, focus ring and motion |
| `components/<name>.css` | One component (its tokens + its CSS) |
| `components/<name>.js` | The behavior, for the 9 components that have a script |
| `icons/*.svg`, `icons/icons.json` | The 70 icons |
| `tokens.json` | The Foundation tokens, to read from code |

## Usage

### CSS

The simplest way is the whole thing:

```js
import 'al-design-system';            // same as al-design-system/al.css
```

Or only what the product uses. The Foundation always comes first, because every component token points to one of its tokens:

```js
import 'al-design-system/foundation.css';
import 'al-design-system/components/button.css';
```

Then the markup uses the `.al-*` classes:

```html
<button type="button" class="al-btn al-btn--primary al-btn--md">Save</button>
```

The exact markup of each component (which element, which attributes) is described at the top of its CSS file and on the [documentation site](https://al.guilhermedesignd.com).

### Scripts

Password, Tab, Modal, Drawer, Sidebar, Breadcrumb, Tooltip, Toast and Alert need their script, loaded once per page. Each one wires up the components already on the page by itself:

```html
<script src="node_modules/al-design-system/dist/components/modal.js" defer></script>
```

Content added later is wired with `init`, for example `window.alModals.init(element)`. Toast and Alert are opened from code: `alToast.show(...)` and `alAlert.show(...)`. The usage of each script is at the top of its file.

### Theme

Without anything on `<html>`, the theme follows the operating system (`prefers-color-scheme`). To force one:

```html
<html data-theme="dark">
```

### Fonts

Fonts are not in the package. The Foundation asks for `Inter` and `JetBrains Mono`, with system fallbacks. Loading the font files is up to the product, preferably hosted alongside it.

### Icons

The SVGs go inline, with the `.al-icon` class on the `<svg>` itself, so they inherit the text color (`<img>` doesn't). The file only has the drawing. The accessibility contract is added by whoever uses it:

- decorative: `aria-hidden="true" focusable="false"`;
- carries meaning: `role="img"` and an `aria-label`.

## Tokens

Three layers, each with one job:

1. **Primitive**: the raw color ramps, in OKLCH, on a single lightness scale shared by every family. No component uses them directly.
2. **Semantic**: the role (`bg-brand`, `text-secondary`, `border-focus`), with one value per theme. This is where the theme is resolved.
3. **Component**: an alias of a semantic token, one per role in the component (`button-primary-bg-hover`). Never a loose hex value.

In CSS they are custom properties prefixed with `--al-`. `tokens.json` has the same values for anyone who wants to read them from code.

## Accessibility

The minimums are the WCAG contrast ones: 4.5:1 for text, 3:1 for icons, borders and focus. When the brand color doesn't reach the minimum, the exception is named one by one, never goes below 3:1, and is paid for with a usage rule (a visible label, a title, a second cue). When a component has exceptions, they are listed in its guidelines.

Besides contrast, each component has a markup contract checked against the HTML: the right native element, an accessible name, the right attributes, nothing interactive where it shouldn't be.

## Versioning

AL follows semantic versioning, read like this:

- **third digit** (1.0.**1**): an adjustment, with no new component or layer;
- **middle digit** (1.**1**.0): a new component or layer;
- **first digit** (**2**.0.0): a change that breaks what already exists.

What changed in each version is in the [CHANGELOG](CHANGELOG.md).

## Repository structure

```
src/foundation/        the Foundation source (color, typography, spacing...) in Python
src/components/<name>/ one folder per component:
  tokens.py              the component tokens (aliases of the Foundation)
  <name>.css             the handwritten CSS
  <name>.js              the script, when there is one
  check.py, a11y.py      the gates (literal CSS, orphan tokens, contrast, markup)
  guidelines.md          the usage rules
site/                  the documentation site generator
tools/                 what the build shares (paths, dist assembly)
build.py               runs everything, in order
build/                 generated output (CSS, tokens, site)
dist/                  the package that goes to npm
```

To build from source you only need Python 3.9 or later, with no packages to install:

```bash
python3 build.py
```

It regenerates everything and runs every gate. Details are in [CONTRIBUTING](CONTRIBUTING.md).

## License

[MIT](LICENSE) © 2026 Guilherme Domingues. The icons come from [Lucide](https://lucide.dev) (ISC); see [`icons/NOTICE`](src/components/icon/NOTICE).
