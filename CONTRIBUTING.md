# Contributing to AL Design System

Thanks for taking the time. This guide explains how the repository works and what a pull request needs before it can be merged.

## Before you start

- **Open an issue first.** Describe the problem before writing code, so we can agree on the fix. Use the templates: bug, accessibility issue, or feature / component request.
- **New components start in Figma.** AL is designed by hand before it is coded, so a new component or a new variant is proposed through an issue and decided by the maintainer. Pull requests from contributors are welcome for fixes, accessibility improvements, documentation and the build itself.
- **Small and focused.** One fix per pull request is easier to review than several.

## Setup

You only need Python 3.9 or newer. There are no packages to install.

```bash
git clone https://github.com/guilhermedworakowski/al-design-system.git
cd al-design-system
python3 build.py
```

`build.py` regenerates everything and runs every gate, in order. It stops at the first step that fails and shows why.

| Command | What it does |
|---|---|
| `python3 build.py` | Full build |
| `python3 build.py --check` | Full build, then checks that nothing outside `build/` and `dist/` changed. This is what CI runs. It needs a clean working tree. |
| `python3 build.py --verbose` | Shows the output of every step |

To see the documentation site locally, open `build/site/index.html` in a browser after the build.

## How the repository works

### Handwritten vs generated

Everything you edit is in `src/`, `tools/` or `site/`. `build/` and `dist/` are generated and stay out of git. **Never edit a generated file**: change the source and run the build.

```
src/foundation/          the Foundation source: palette, semantic layer, typography, spacing...
src/components/<name>/
  tokens.py                the component tokens
  <name>.css               the component CSS
  <name>.js                the script, when the component has one
  check.py                 component-specific CSS checks
  a11y.py                  contrast of every rendered combination + markup contract
  guidelines.md            the usage rules
tools/                   code shared by the build (paths, contrast, HTML reader, gates, dist)
site/site.py             the documentation site generator
build.py                 the full build
```

The list of components, in cascade order, lives in `tools/paths.py`.

### Tokens

Three layers, and a component only talks to the last one:

1. **Primitive**: raw color ramps. No component uses them directly.
2. **Semantic**: a role (`bg-brand`, `text-secondary`), with one value per theme.
3. **Component**: an alias of a semantic token (`button-primary-bg-hover`), declared in the component's `tokens.py`.

The component CSS only uses its own component tokens (`var(--al-button-...)`). A hex value, a pixel value or a duration written straight into the CSS fails the build.

Token names use hyphens between levels, never slashes.

## The gates

Validation is part of the build, not an optional check. Each gate stops the build with a non-zero exit:

| Gate | Where | What it refuses |
|---|---|---|
| Guidelines | `tools/guidegate.py` | A usage rule missing, repeated or extra, compared to the approved count |
| Contrast | `src/foundation/export.py` | A Foundation color pair below the WCAG minimum. Brand exceptions are named one by one and never go below 3:1. |
| Alias | `src/components/<name>/tokens.py` | A component token with its own value instead of pointing to the Foundation |
| Literal CSS | `src/components/<name>/check.py` (through `tools/cssgate.py`) | A literal color, length, weight or duration in the component CSS; a token declared and never used; a token used and never declared |
| Accessibility | `src/components/<name>/a11y.py` | A rendered combination (variant × state × theme) below the minimum against its real background, or HTML that breaks the component's markup contract |
| Icons | `src/components/icon/icons.py` | An SVG outside the family: another grid, another stroke, a hard-coded color |

When a gate fails, its message names the file, the token or the element and the reason. Fix the source and run the build again. A gate is never relaxed to make a change pass. If you think a gate is wrong, open an issue.

## Pull requests

1. Branch from `dev` (`main` only receives releases).
2. Make the change in the source files.
3. Run `python3 build.py --check` with a clean working tree. It must pass.
4. Open the pull request **against `dev`**, describing what changed and how you checked it. Link the issue.
5. CI runs the same check. A pull request is merged when CI is green and the maintainer approves.

If the change affects what a product sees (a token value, a class, a script), add a line to the `Unreleased` section of the [CHANGELOG](CHANGELOG.md).

## Code style

- Comments, messages and names in English.
- CSS classes start with `.al-` and follow `.al-<component>__<part>` and `.al-<component>--<modifier>`.
- Python uses only the standard library and must run on 3.9.
- Scripts are plain JavaScript, no dependencies and no build step, and they only do what CSS can't.
- Prefer the native HTML element (`<button>`, `<dialog>`, `<details>`, `<input>`) over ARIA on a `<div>`.

## License

By contributing, you agree that your contribution is licensed under the [MIT License](LICENSE).
