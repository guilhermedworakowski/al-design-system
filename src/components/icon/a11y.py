"""
Accessibility QA for the Icon.

As in the Button, validation is by RENDERED COMBINATION, not by a loose token
pair. But the Icon has two particularities that change what is measured:

1. The criterion is different. An icon is not text: the floor is the 3:1 of
   1.4.11 (non-text), not the 4.5:1 of 1.4.3. A pair that would fail as a label
   can pass as an icon - and the opposite never happens.

2. The default color is not a token, it is `currentColor`. So there are TWO
   families of combinations, and both need to be measured:
     - explicit ink   -> the four `--al-icon-ink-*` against the surfaces where
                         each one makes sense;
     - inherited ink  -> the icon inside the Button, where it wears the label's
                         color. The same logic as the variant with no fill
                         applies here: Ghost and Secondary have no background,
                         so the icon touches the CANVAS, not "transparent".

And there is a third gate that is not about contrast: the MARKUP CONTRACT. The
rule of decorative icon versus meaningful icon didn't become a document by
design - an AL icon lives inside an actionable element and the label carries
the meaning. So it is checked here, in the HTML the site really emits, instead
of being read on a page nobody opens.

Run: python3 a11y.py   (requires the generated build/site/index.html)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import TOKENS_JSON, SITE_HTML, comp_out  # noqa: E402
from contrast import cr  # noqa: E402

FOUND = json.load(open(TOKENS_JSON))
ICON = json.load(open(comp_out('icon', 'tokens.json')))
BTN = json.load(open(comp_out('button', 'tokens.json')))
MANIFEST = json.load(open(comp_out('icon', 'icons.json')))

SEM = FOUND['color']['semantic']
THEMES = ('light', 'dark')
NON_TEXT_FLOOR = 3.0

SITE = SITE_HTML

# Where each explicit ink makes sense. Measuring `on-brand` against the canvas
# would invent a scenario the design system doesn't produce.
INK_SURFACES = {
    'default':  ['bg-canvas', 'bg-surface', 'bg-subtle'],
    'on-brand': ['bg-brand', 'bg-brand-hover', 'bg-brand-active'],
    'on-solid': ['bg-danger', 'bg-danger-hover', 'bg-danger-active'],
    'disabled': ['bg-canvas', 'bg-disabled'],
}

# Brand exception inherited from the Foundation. White on the brand gives
# 3.34:1 - below normal text, above the non-text floor. For an icon this is NOT
# an exception: it is a pass with room to spare. It stays named so nobody
# "fixes" the value.
BRAND_PAIRS = {('light', 'on-brand', 'bg-brand'), ('dark', 'on-brand', 'bg-brand')}

VARIANTS = ('primary', 'secondary', 'ghost', 'danger')


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def ink(mode, theme):
    return ICON['resolved'][f'icon-ink-{mode}'][theme]


def btn(name, theme):
    v = BTN['resolved'][f'button-{name}']
    return v[theme] if isinstance(v, dict) else v


def effective_bg(variant, state, theme):
    """The background the icon actually touches. Transparent = the canvas shows."""
    suffix = {'default': 'bg', 'hover': 'bg-hover', 'active': 'bg-active'}[state]
    value = btn(f'{variant}-{suffix}', theme)
    return sem('bg-canvas', theme) if value == 'transparent' else value


# ─────────────────────────────────────────────── markup contract
SVG_TAG = re.compile(r'<svg\b[^>]*>')


def markup_contract():
    """Reads the HTML the site emits and enforces the contract of each .al-icon.

    Decorative -> aria-hidden="true" AND focusable="false"
    Meaningful -> role="img" AND a non-empty aria-label
    And never both at the same time: an icon hidden from the screen reader that
    also carries a label is a contradiction, and the label loses.
    """
    if not os.path.exists(SITE):
        return None, ['build/site/index.html does not exist - run site/site.py before this gate']

    html = open(SITE).read()

    # Markup only. <style> and <script> carry examples in comments - the header
    # of icon.css itself has two - and an example in a comment is not a
    # rendered element. Measuring there would fail documentation.
    html = re.sub(r'<style\b.*?</style>', lambda m: '\n' * m.group(0).count('\n'),
                  html, flags=re.S)
    html = re.sub(r'<script\b.*?</script>', lambda m: '\n' * m.group(0).count('\n'),
                  html, flags=re.S)
    html = re.sub(r'<!--.*?-->', lambda m: '\n' * m.group(0).count('\n'), html, flags=re.S)

    checked, problems = 0, []

    for m in SVG_TAG.finditer(html):
        tag = m.group(0)
        if not re.search(r'class="[^"]*\bal-icon\b', tag):
            continue
        checked += 1
        line = html.count('\n', 0, m.start()) + 1

        hidden = 'aria-hidden="true"' in tag
        focusable_off = 'focusable="false"' in tag
        role_img = 'role="img"' in tag
        label = re.search(r'aria-label="([^"]*)"', tag)

        if hidden and (role_img or (label and label.group(1).strip())):
            problems.append(f'line {line}: aria-hidden together with a label - the label will never be read')
        elif hidden:
            if not focusable_off:
                problems.append(f'line {line}: decorative without focusable="false" - '
                                f'it enters the tab order in some browsers')
        elif role_img:
            if not (label and label.group(1).strip()):
                problems.append(f'line {line}: role="img" without aria-label - '
                                f'announced as an image with no name')
        else:
            problems.append(f'line {line}: no contract - neither decorative '
                            f'(aria-hidden) nor meaningful (role="img")')

    return checked, problems


def write_report(rows, checked, failures, notes):
    """The report becomes data, not just a log.

    The site reads this file to build the accessibility tab. Without it the page
    would have to recompute the same contrasts on its own - and a second
    implementation of the same criterion is a divergence waiting to happen.
    """
    out = {
        'component': 'icon',
        'criterion': 'WCAG 1.4.11 non-text',
        'floor': NON_TEXT_FLOOR,
        'markupChecked': checked,
        'fails': len(failures),
        'brandPairs': [{'theme': t, 'label': l, 'ratio': round(r, 2)} for t, l, r in notes],
        'rows': [{'group': g, 'theme': t, 'label': l, 'fg': fg, 'bg': bg,
                  'ratio': round(ratio, 2), 'floor': floor, 'pass': ok, 'exempt': floor is None}
                 for g, t, l, fg, bg, ratio, floor, ok in rows],
    }
    path = comp_out('icon', 'a11y.json')
    json.dump(out, open(path, 'w'), indent=2, ensure_ascii=False)
    return path


def run():
    rows, failures, notes = [], [], []

    # ---- 1. explicit ink against the surface (1.4.11, 3:1) ----
    for theme in THEMES:
        for mode, surfaces in INK_SURFACES.items():
            for surface in surfaces:
                fg, bg = ink(mode, theme), sem(surface, theme)
                ratio = cr(fg, bg)
                if mode == 'disabled':
                    # 1.4.3 and 1.4.11 exempt inactive components. Measured and
                    # reported, never failed - raising it makes disabled look
                    # active.
                    rows.append(('ink', theme, f'{mode} · {surface}', fg, bg, ratio, None, True))
                    continue
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('ink', theme, f'{mode} · {surface}', fg, bg,
                             ratio, NON_TEXT_FLOOR, ok))
                if not ok:
                    failures.append((theme, f'{mode} on {surface}', ratio))
                elif (theme, mode, surface) in BRAND_PAIRS:
                    notes.append((theme, f'{mode} on {surface}', ratio))

    # ---- 2. inherited ink inside the Button (currentColor) ----
    for theme in THEMES:
        for v in VARIANTS:
            for state in ('default', 'hover', 'active'):
                fg = btn(f'{v}-label', theme)          # the icon wears this color
                bg = effective_bg(v, state, theme)
                ratio = cr(fg, bg)
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('inherited', theme, f'{v} · {state}', fg, bg,
                             ratio, NON_TEXT_FLOOR, ok))
                if not ok:
                    failures.append((theme, f'{v} {state} (inherited)', ratio))

    # ---- 3. markup contract on the rendered HTML ----
    checked, markup_problems = markup_contract()

    # ---------------- report ----------------
    print('=' * 78)
    print('ACCESSIBILITY QA - ICON')
    print('=' * 78)
    print('An icon is not text: the floor is 3:1 (WCAG 1.4.11 non-text), not 4.5:1.')

    titles = {
        'ink':       '1. EXPLICIT INK AGAINST THE SURFACE    (WCAG 1.4.11 · min 3:1)',
        'inherited': '2. INHERITED INK INSIDE THE BUTTON     (currentColor · min 3:1)',
    }
    for group in ('ink', 'inherited'):
        print(f'\n{titles[group]}')
        print('-' * 78)
        for g, theme, label, fg, bg, ratio, floor, ok in rows:
            if g != group:
                continue
            if floor is None:
                tag = 'EXEMPT'
                extra = '(inactive component)'
            else:
                tag = 'OK  ' if ok else 'FAIL'
                extra = f'(min {floor})'
            print(f'  {tag} {theme:<6} {label:<24} {fg} / {bg}  {ratio:5.2f}:1  {extra}')

    print(f'\n3. MARKUP CONTRACT                     (on the HTML the site emits)')
    print('-' * 78)
    if checked is None:
        for p in markup_problems:
            print(f'  FAIL {p}')
    else:
        print(f'  {checked} .al-icon elements inspected in build/site/index.html')
        print(f'  decorative -> aria-hidden="true" + focusable="false"')
        print(f'  meaningful -> role="img" + aria-label')
        if markup_problems:
            for p in markup_problems:
                print(f'  FAIL {p}')
        else:
            print(f'  0 outside the contract.')

    print(f'\n4. DRAWING FAMILY')
    print('-' * 78)
    print(f'  {MANIFEST["count"]} icons · grid {MANIFEST["grid"]} · stroke {MANIFEST["strokeWidth"]} '
          f'· {MANIFEST["family"]} · {MANIFEST["license"]}')
    print(f'  Smallest box in use: {ICON["resolved"]["icon-box-16"]}px. WCAG defines no minimum')
    print(f'  size for an icon; 2.5.8 measures the TARGET, and the target belongs to the')
    print(f'  actionable element that contains it.')

    n_fail = len(failures) + (len(markup_problems) if markup_problems else 0)
    total = len([r for r in rows if r[6] is not None]) + (checked or 0)

    print('\n' + '=' * 78)
    print(f'{total} checks. {n_fail} failures.')
    if notes:
        print(f'{len(notes)} brand pair(s), all above the non-text floor:')
        for theme, label, ratio in notes:
            print(f'   {theme:<6} {label:<28} {ratio:.2f}:1')
        print('White on the brand fails as normal text and passes as an icon -')
        print('same color, different criterion. It is not an exception here, it is a pass.')
    print('Disabled stays out of the minimum by design: WCAG exempts inactive')
    print('components, and raising that contrast would make disabled look clickable.')

    if failures:
        print('\nFAILURES:')
        for theme, label, ratio in failures:
            print(f'   {theme:<6} {label:<28} {ratio:.2f}:1  (min {NON_TEXT_FLOOR})')
    if markup_problems:
        print('\nMARKUP CONTRACT:')
        for p in markup_problems:
            print(f'   {p}')

    # Without the site yet (the build's first pass in a clean clone), it writes
    # the report anyway, like the other gates: the site needs it to exist. The
    # gate still fails; build.py tolerates only that pass.
    if not n_fail or checked is None:
        write_report(rows, checked or 0, failures, notes)
        print('\nbuild/components/icon/a11y.json written')

    return 1 if n_fail else 0


if __name__ == '__main__':
    sys.exit(run())
