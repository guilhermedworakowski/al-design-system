# Changelog

Every release of AL Design System, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the version numbers follow the rule in the [README](README.md#versioning): the third digit is an adjustment, the middle digit is a new component or layer.

## [1.3.0] - 2026-10-21

### Added
- **Pagination**, in Navigation: a `<nav aria-label="Pagination">` in four types: Numbered (jump to a page, a fixed window of 7 positions), Simple (previous and next when the total is unknown), Load more (keeps the reading position) and Range ("Showing 41–60 of 312" with rows per page). Previous, Next and Load more are the Button; rows per page is the Select. The current page is tonal and set by `aria-current="page"`. The row never wraps: when it does not fit, its container scrolls. 17 tokens, 24 usage rules, its own CSS and accessibility gates, and a page in the documentation site in English and Portuguese.
- No new Foundation token. Three declared contrast exceptions, all inherited from the Tab: the tonal current page, white on the dark brand hover, and the dark pressed fill on bg-surface.

## [1.2.0] - 2026-10-21

### Added
- **Progress**, in Feedback: the native `<progress value max>`, determinate only, in three types: Label (label and percentage), Steps ("N of total") and Thin (a 4px bar for background tasks). 9 tokens, 24 usage rules, its own CSS and accessibility gates, and a page in the documentation site in English and Portuguese.
- **`bg-track`**, a new semantic in the Foundation: the empty part of a bar that fills up, readable on canvas, surface and surface-raised in both themes (neutral-200 light, neutral-700 dark).
- One declared contrast exception: the fill against the track is below 3:1 (2.53:1 light, 2.2:1 dark). The bar is never the only cue: Label shows the percentage, Steps the count, and Thin a name and value read by assistive tech.

## [1.1.0] - 2026-10-21

### Added
- **Link**, in Actions: the native `<a href>`, always underlined, with an optional icon on the right. Standalone it uses label-md; with `al-link--inline` it inherits the paragraph font and hides the icon. Three states (default, hover, focus), 10 tokens, 22 usage rules, its own CSS and accessibility gates, and a page in the documentation site in English and Portuguese.
- One declared contrast exception: the default ink is the brand orange (`color-orange-500`), below 4.5:1 on the light canvas, the light surface and the dark surface. The underline, present in every state, keeps the link from depending on color alone (WCAG 1.4.1).

## [1.0.1] - 2026-10-09

Preparation for the open-source launch. No class or token changed meaning; one Sidebar style and two gate rules (Tab and Breadcrumb) changed (see Changed).

### Added
- Published on npm as `al-design-system`, with a `dist/` folder: `al.css` (everything), `foundation.css`, one `components/<name>.css` per component (tokens + CSS), the 9 scripts, the icons and `tokens.json`.
- A release workflow: a `vX.Y.Z` tag runs the full build, attaches `dist/` as a zip to the GitHub Release and publishes to npm.
- `guidelines.md` for 22 components (all except Icon), with the usage rules readable on GitHub. A new gate checks that every approved rule is there, once.
- A single `build.py` at the root that runs every step in order, and a GitHub Actions check that runs it on every pull request.
- README in English and Portuguese, CHANGELOG, CONTRIBUTING and issue templates.
- A language selector (EN / PT) in the documentation site, modeled on the author's portfolio: Mono, Body/sm, all caps, the current language in `text-brand` and the other in `text-secondary`. It sits at the top right, 40px from the edge and centered on the hero's section line; below 1024px it moves to the right end of the top bar. Each language is a link (`aria-current` on the current one, `hreflang` on both) at least 24px tall.
- The documentation site in English and Portuguese: two pages, English at the root (`index.html`) and Portuguese in `pt/index.html`, each with the right `lang`. The selector leads to the same page in the other language, English opens first and the site remembers the choice. Everything the reader sees is translated, including accessible names and the code samples; the repository stays in English. The texts that come from `tokens.json` (type style uses, motion token uses, contrast pair names) have their Portuguese version in the site generator, and the build fails if a new one has none. The gates measure the English page.

### Changed
- **Package paths.** The 1.0.0 package was installed from a Git tag and exposed `foundation/al-foundation.css` and `components/<name>/...`. From 1.0.1, install from npm and import `al-design-system/foundation.css` and `al-design-system/components/<name>.css`; the component tokens and CSS now come in one file.
- The repository is split into `src/` (handwritten), `tools/` (shared code), `build/` and `dist/` (generated, outside git).
- Code, comments, build messages and internal names are in English.
- The literal-CSS gate is stricter: a literal duration now fails the build, and Button, Icon, Icon Button, Tag and Avatar gained the orphan-token check the other components already had. No component CSS had to change.
- **Sidebar:** the group label is now all caps, applied by CSS (`text-transform`); the text stays in sentence case in the HTML, so screen readers read the word instead of spelling it. Rule 17 changed to match.
- **Tab gate:** the 2-to-6-tabs limit (rule 8) no longer applies inside a `.al-sidebar`. The rule itself sends more than six destinations to side navigation, and the Sidebar gate owns those lists. A live demo marked with `data-al-demo` doesn't count as a nesting level either: it is a sample sitting inside a documentation page that has its own tabs.
- **Toast and Alert gates:** the status names and close-button labels they expect are now the English ones (Success, Warning, Error or Danger, Info; “Close notification”, “Close alert”), since they measure the English page.
- **Breadcrumb gate:** "one per page" (rule 7) now counts per page in a single-file site, where each page is a subtree that toggles `hidden`, and a live demo that can't be `inert` is marked with `data-al-demo` and counts as a sample. The guidelines declare the documentation site's divergence from rules 1 and 3: its 2-level trail repeats the Sidebar.
- **Figma library:** components bind the semantic and Foundation variables directly, and the 22 per-component variable collections are gone (407 variables that only repeated a semantic or Foundation token). The only component variables left are the 10 values the Foundation lacks (Modal and Drawer widths, Sidebar width, Breadcrumb menu minimum width, Tooltip and Toast maximum widths), in a single `4. Components` collection. No token changed in code; the `tokens.py` headers and the `figmaCollection` metadata were updated to match.
- The documentation site's navigation is now the AL Sidebar itself, grouped by Foundation and by component type, instead of a handmade rail. Every page opens with the same hero: the Sidebar group, a Breadcrumb outside the two overview pages, the title, the description and the summary as Tags. The footer, modeled on the author's portfolio, holds the name and version, a one-line description centered between them and the license. The section tabs are the AL Tab Line, in a sticky band between the hero and the panels, with the line running the full width of the content. Section titles in the body use the portfolio's eyebrow style (Mono, Body/sm, all caps, `text-brand`), 16px above their content and without the bottom border; sections sit 40px apart, and the first one starts 40px below the tabs. Body text under them is Body/sm in `text-secondary`, and every paragraph keeps the hero description's 62ch measure. The site's own body borders (playground chips and fields, the Copy button, the note bar) are `border-subtle`; component borders are untouched. Notes have a Body/sm bold `text-primary` title and Body/sm `text-secondary` text on `bg-surface`. The Button page is the model for the component pages, after Astryx: Overview (preview, usage, anatomy, a do and don't table with Tags, and example cards with Description and Code in a Square Tab plus "Open in playground"), Playground (the playground, classes and attributes, states, measures, and color tokens per variant in a Square Tab), Guidelines and Accessibility. Its playground controls are the AL Select and Input; using the Select with 2 or 3 options is a conscious divergence from Select rule 1, so all six controls share one shape. Its Accessibility tab opens with a contrast table (requirement, minimum, applies to, measured, guidance with the WCAG criterion); the measured values come from the `a11y.json` the Button gate now writes, like the other components' gates. The Icon Button page follows the same model: its Specifications tab became the Playground (Select controls, no label field, since the accessible name follows the icon), and its Accessibility tab opens with the same contrast table, read from its gate's `a11y.json`, in place of the three row-by-row contrast tables. The other 20 component pages (Forms and inputs, Content, Navigation, Feedback and status) follow the same model: Specifications became the Playground, with the AL Select as every control and the label field as the AL Input; the anatomy moved to the Overview as a table; the do and don't table joins the Guidelines' do and don't examples with items from the numbered rules; the old demos became example cards with Description, Code and, where it maps, Open in playground; every Accessibility tab opens with a contrast table read from that component's gate (`a11y.json`), in place of the row-by-row tables. Tag color tokens are in a Square Tab like the Button's. The card grids left in the Playground and Guidelines (how the state comes from the markup, when to use, out of scope) are two-column tables like the Button's. Playgrounds that act on the page (Modal, Drawer, Toast) have one Secondary/sm “Visualizar” button below the Selects, without helper text; the Alert playground has none, since its stage is already the live Alert. Tables use Foundation tokens: Caption headers, Body/sm cells, `space-8` by `space-16` padding. Numbered rules have a Body/sm bold `text-primary` title and Body/sm `text-secondary` text, with a Caption number; example card text runs the card's full width. Example blocks in Guidelines and Accessibility take the example cards' spacing and text: Do and Don't are Success and Error Tags (a descriptive label sits below the Tag as a title), titles are Body/sm bold `text-primary` and captions Body/sm `text-secondary`. The Foundation pages follow the same model: stacked notes and the last card grid are two-column tables, the principles table has a header row, code samples sit in the code block, contrast results are Success and Warning Tags instead of handmade badges, and the Icon page has Overview (preview, usage, a short anatomy, an example card and the library), Playground (AL Select and Input controls, classes and attributes, measures, tokens, markup contract, files and gates) and Accessibility, with no Guidelines tab, since Icon has no usage rules.

### Removed
- The per-component QA pages; every gate now measures the documentation site itself.
- The Principles and The proof pages from the published site (`build/site/`). They were behind-the-scenes pages from building the system and stay only in the full version published as the artifact (`build/artifact/`).

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

[1.3.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/guilhermedworakowski/al-design-system/compare/v1.0.1...v1.1.0
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
