# Changelog

Every release of AL Design System, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the version numbers follow the rule in the [README](README.md#versioning): the third digit is an adjustment, the middle digit is a new component or layer.

## [1.0.1] - 2026-10-09

Preparation for the open-source launch. No class or token changed meaning; one Sidebar style and two gate rules (Tab and Breadcrumb) changed (see Changed).

### Added
- Published on npm as `al-design-system`, with a `dist/` folder: `al.css` (everything), `foundation.css`, one `components/<name>.css` per component (tokens + CSS), the 9 scripts, the icons and `tokens.json`.
- A release workflow: a `vX.Y.Z` tag runs the full build, attaches `dist/` as a zip to the GitHub Release and publishes to npm.
- `guidelines.md` for 22 components (all except Icon), with the usage rules readable on GitHub. A new gate checks that every approved rule is there, once.
- A single `build.py` at the root that runs every step in order, and a GitHub Actions check that runs it on every pull request.
- README in English and Portuguese, CHANGELOG, CONTRIBUTING and issue templates.

### Changed
- **Package paths.** The 1.0.0 package was installed from a Git tag and exposed `foundation/al-foundation.css` and `components/<name>/...`. From 1.0.1, install from npm and import `al-design-system/foundation.css` and `al-design-system/components/<name>.css`; the component tokens and CSS now come in one file.
- The repository is split into `src/` (handwritten), `tools/` (shared code), `build/` and `dist/` (generated, outside git).
- Code, comments, build messages and internal names are in English.
- The literal-CSS gate is stricter: a literal duration now fails the build, and Button, Icon, Icon Button, Tag and Avatar gained the orphan-token check the other components already had. No component CSS had to change.
- **Sidebar:** the group label is now all caps, applied by CSS (`text-transform`); the text stays in sentence case in the HTML, so screen readers read the word instead of spelling it. Rule 17 changed to match.
- **Tab gate:** the 2-to-6-tabs limit (rule 8) no longer applies inside a `.al-sidebar`. The rule itself sends more than six destinations to side navigation, and the Sidebar gate owns those lists.
- **Breadcrumb gate:** "one per page" (rule 7) now counts per page in a single-file site, where each page is a subtree that toggles `hidden`, and a live demo that can't be `inert` is marked with `data-al-demo` and counts as a sample. The guidelines declare the documentation site's divergence from rules 1 and 3: its 2-level trail repeats the Sidebar.
- The documentation site's navigation is now the AL Sidebar itself, grouped by Foundation and by component type, instead of a handmade rail. Every page opens with the same hero: the Sidebar group, a Breadcrumb outside the two overview pages, the title, the description and the summary as Tags.

### Removed
- The per-component QA pages; every gate now measures the documentation site itself.

## [1.0.0] - 2026-10-09

V1 closed: Foundation and 23 components in five tiers.

### Added
- **Alert**: page-level message at the top of the content, one per page, Warning and Danger without a close button.

## [0.23.0] - 2026-10-09
### Added
- **Toast**: one at a time in a queue, never takes focus, errors announced as `alert`. The Switch uses it to report a failed change.

## [0.22.0] - 2026-10-08
### Added
- **Tooltip**: inverted surface, always with an icon, no arrow, opened as a manual popover.

## [0.21.0] - 2026-10-08
### Added
- **Breadcrumb**: collapses the middle levels into a `…` menu from five levels on.

## [0.20.0] - 2026-10-08
### Added
- **Sidebar**: app navigation on `bg-canvas`, items reuse the Square Tab, becomes a modal panel below 1024px.

## [0.19.0] - 2026-10-08
### Added
- **Drawer**: native `<dialog>` entering from the right, with a close button.

## [0.18.2] - 2026-10-07
### Fixed
- Ghost and Secondary buttons (Button and Icon Button) inside Card and Modal use `bg-hover-raised` and `bg-active-raised`.

## [0.18.1] - 2026-10-07
### Fixed
- Modal footer buttons: in dark mode the hover matched the Modal background and disappeared; they now use the `-raised` hover and pressed colors.

## [0.18.0] - 2026-10-07
### Added
- **Modal**: native `<dialog>`, no close button, closes on the scrim only when it has no fields. New `bg-scrim` semantic token.

## [0.17.2] - 2026-10-07
### Added
- Motion completed: `duration-feedback`, the spinner durations and `easing-spinner`. All 12 components with transitions now use motion tokens, easing out into a state and in out of it.

## [0.17.1] - 2026-10-07
### Added
- Motion enters the Foundation: panel and popup durations, enter and exit easings.

## [0.17.0] - 2026-10-07
### Added
- **Accordion**: native `<details>`, no script, several items open by default.

## [0.16.0] - 2026-10-07
### Added
- **Tab**: one component for panels and navigation, Line and Square types.

## [0.15.0] - 2026-10-07
### Added
- **Card**: Filled, Border and Elevated types, three paddings, clickable through a stretched link on the title.

## [0.14.0] - 2026-10-07
### Added
- **Divider**: 1px in `border-default`, a real `<hr>` announced by default.

## [0.13.0] - 2026-10-06
### Added
- **Password**: show/hide button with its own focus; the field hides again on submit.

## [0.12.0] - 2026-10-06
### Added
- **Textarea**: mirrors the Input, minimum of three lines, resizes vertically only.

## [0.11.1] - 2026-09-30
### Added
- Installable as an npm package from a Git tag.

### Fixed
- Duplicate ids on the Select and Input documentation pages.

## [0.11.0] - 2026-09-26
### Added
- **Input**: seven states, including a new read-only state; optional affixes and character counter.

## [0.10.0] - 2026-09-26
### Added
- **Switch**: immediate effect, no error state. New `bg-thumb` semantic tokens.

## [0.9.0] - 2026-09-24
### Added
- **Radio**: native input; the error lights the whole group.

## [0.8.0] - 2026-09-24
### Added
- **Checkbox**: native input, including the indeterminate state.

## [0.7.0] - 2026-09-23
### Added
- **Select**: native `<select>`, one size.

## [0.6.0] - 2026-09-11
### Added
- **Avatar**: photo → initials → icon fallback chain.

## [0.5.0] - 2026-09-10
### Added
- **Tag**: status labels with zero text contrast exceptions.

## [0.4.0] - 2026-09-08
### Added
- **Icon Button**: the Button without a visible label; the accessible name is mandatory.

## [0.3.1] - 2026-09-07
### Changed
- The Button uses the Foundation icons, sized to the label's line height (20 in `sm`, 24 in `md`), so turning the icon on doesn't change the button's height.

## [0.3.0] - 2026-09-06
### Added
- **Icon**: 70 icons from Lucide on a 24px grid, with the `icon-size` scale.

## [0.2.0] - 2026-09-04
### Added
- Foundation: color primitives, semantic layer with light and dark themes, typography, spacing, radius, elevation and focus ring.
- **Button**: the first component through the full pipeline.

[1.0.1]: https://github.com/guilhermedworakowski/al-design-system/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.23.0...v1.0.0
[0.23.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.22.0...v0.23.0
[0.22.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.21.0...v0.22.0
[0.21.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.20.0...v0.21.0
[0.20.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.19.0...v0.20.0
[0.19.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.18.2...v0.19.0
[0.18.2]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.18.1...v0.18.2
[0.18.1]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.18.0...v0.18.1
[0.18.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.17.2...v0.18.0
[0.17.2]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.17.1...v0.17.2
[0.17.1]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.17.0...v0.17.1
[0.17.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.16.0...v0.17.0
[0.16.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.15.0...v0.16.0
[0.15.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.14.0...v0.15.0
[0.14.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.11.1...v0.12.0
[0.11.1]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.11.0...v0.11.1
[0.11.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/guilhermedworakowski/al-design-system/releases/tag/v0.2.0
