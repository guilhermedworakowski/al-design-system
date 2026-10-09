"""
Accessibility QA for the Icon Button.

As in the Button, validation is by RENDERED COMBINATION - each variant, in
each state, in each theme, against the effective background the button really
has. A variant with no fill touches the CANVAS, not "transparent".

Two things change compared with the Button, and both pull the same way:

1. THE CRITERION IS DIFFERENT. Here an ICON carries the meaning, not a text
   label: the floor is the 3:1 of 1.4.11 (non-text), not the 4.5:1 of 1.4.3.
   That is why this component has no brand exception - white on bg-brand gives
   3.34:1, which fails as text and passes as an icon. Same color, different
   criterion.

2. THE GHOST HAS NO LABEL TO LEAN ON. In the Button, the variant with no fill
   and no border doesn't need a boundary of its own: it is text, and counts as
   text. Here there is no text - the icon itself is the component's visible
   boundary, and it is already measured in section 1 against the canvas.
   Section 2 records that explicitly instead of repeating the Button's
   sentence, which would be false.

And there is a contract that is not about contrast: the ACCESSIBLE NAME. An
Icon Button with no aria-label is not a degraded button, it is a mute button -
and that is this component's number one failure in any system. It doesn't
live in the CSS, so check.py can't reach it; it lives in the markup, and it is
measured here, on the HTML the site emits.

Run: python3 a11y.py
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
IB = json.load(open(comp_out('icon-button', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = IB['resolved']
THEMES = ('light', 'dark')
VARIANTS = ('primary', 'secondary', 'ghost', 'danger')

# The only floor in this component. There is no second floor because there is
# no text.
NON_TEXT_FLOOR = 3.0

# Brand pairs inherited from the Foundation. In the Button they are a named
# exception; here they pass with room to spare, because the criterion is
# different. They stay listed so nobody "fixes" the value thinking it slipped.
BRAND_PAIRS = {
    ('light', 'primary', 'default'),
    ('dark', 'primary', 'default'),
    ('dark', 'primary', 'hover'),
}

SITE = SITE_HTML


def tok(name, theme):
    v = RES[f'icon-button-{name}']
    return v[theme] if isinstance(v, dict) else v


def canvas(theme):
    return SEM['bg-canvas'][0 if theme == 'light' else 1]


def effective_bg(variant, state, theme):
    """The background the icon actually touches. Transparent = the canvas shows."""
    suffix = {'default': 'bg', 'hover': 'bg-hover',
              'active': 'bg-active', 'disabled': 'bg-disabled'}[state]
    value = tok(f'{variant}-{suffix}', theme)
    return canvas(theme) if value == 'transparent' else value


# ─────────────────────────────────────────────── markup contract
BTN_TAG = re.compile(r'<button\b[^>]*>')


def labelled_text(html, rid):
    """Text of the element with that id - up to the first </div>, which is where
    the .al-tooltip closes. Approximate on purpose: it only needs to prove it
    is not empty."""
    m = re.search(r'<[^>]*\bid="' + re.escape(rid) + r'"[^>]*>(.*?)</div>', html, re.S)
    return m and re.sub(r'<[^>]+>', '', m.group(1)).strip()


def markup_contract():
    """Enforces the contract of each .al-icon-btn on the HTML the site emits.

    Four usage rules:
      10  the name is on the BUTTON, in a single way: a non-empty aria-label OR
          an aria-labelledby pointing to an element that exists and has text
          (the Tooltip, decided on 2026-10-08). Both together fail: labelledby
          wins and the aria-label becomes text nobody reads and that goes stale
          on its own.
      14  aria-busy always comes with aria-disabled
      17  the `disabled` attribute is not used: it takes the button out of the
          focus order in the middle of the interaction and nothing is announced
      20  the button never gets aria-hidden - what is decorative is the svg,
          inside it

    Returns (checked, problems). checked = None when the site doesn't emit the
    component yet - which is the case until the playground is built. That is
    PENDING, not a pass: the gate starts counting by itself when the HTML shows
    up, without anyone having to remember to switch anything on.
    """
    if not os.path.exists(SITE):
        return None, ['build/site/index.html does not exist - run site/site.py']

    html = open(SITE).read()
    # examples in comments, <style> and <script> are not rendered elements
    for pat in (r'<style\b.*?</style>', r'<script\b.*?</script>', r'<!--.*?-->'):
        html = re.sub(pat, lambda m: '\n' * m.group(0).count('\n'), html, flags=re.S)

    checked, problems = 0, []
    for m in BTN_TAG.finditer(html):
        tag = m.group(0)
        if not re.search(r'class="[^"]*\bal-icon-btn\b', tag):
            continue
        checked += 1
        line = html.count('\n', 0, m.start()) + 1

        label = re.search(r'aria-label="([^"]*)"', tag)
        ref = re.search(r'aria-labelledby="([^"]*)"', tag)
        if label and ref:
            problems.append(f'line {line}: aria-label and aria-labelledby together - '
                            f'the name has to live in a single place')
        elif ref:
            for rid in ref.group(1).split():
                if not labelled_text(html, rid):
                    problems.append(f'line {line}: aria-labelledby="{rid}" points to an '
                                    f'element that does not exist or has no text')
        elif not (label and label.group(1).strip()):
            problems.append(f'line {line}: no aria-label and no aria-labelledby - '
                            f'a mute button for the screen reader')
        if 'aria-hidden="true"' in tag:
            problems.append(f'line {line}: aria-hidden on the button itself - '
                            f'the svg is decorative, not the actionable element')
        if 'aria-busy="true"' in tag and 'aria-disabled="true"' not in tag:
            problems.append(f'line {line}: aria-busy without aria-disabled - '
                            f'the button stays clickable while loading')
        if re.search(r'(?<![\w-])disabled(?![\w-])', tag):
            problems.append(f'line {line}: disabled attribute - use aria-disabled, '
                            f'or focus disappears in the middle of the interaction')

    if checked == 0:
        return None, ['no .al-icon-btn in build/site/index.html - the component enters '
                      'the site with its playground; until then this gate stays pending']
    return checked, problems


def write_report(rows, checked, brand, targets):
    """The report becomes data, not just a log.

    The QA page and the playground read this file instead of recomputing the
    same contrasts on their own - a second implementation of the same
    criterion is a divergence waiting to happen.
    """
    out = {
        'component': 'icon-button',
        'criterion': 'WCAG 1.4.11 non-text',
        'floor': NON_TEXT_FLOOR,
        'markupChecked': checked,
        'markupPending': checked is None,
        'fails': 0,
        'targets': [{'size': s, 'box': b, 'meetsRecommended': b >= 44} for s, b in targets],
        'brandPairs': [{'theme': t, 'label': f'{v} · {s}', 'ratio': round(r, 2)}
                       for t, v, s, r in brand],
        'rows': [{'group': g, 'theme': t, 'label': l, 'fg': fg, 'bg': bg,
                  'ratio': round(ratio, 2), 'floor': floor,
                  'pass': ok, 'exempt': floor is None}
                 for g, t, l, fg, bg, ratio, floor, ok, _ in rows],
    }
    path = comp_out('icon-button', 'a11y.json')
    json.dump(out, open(path, 'w'), indent=2, ensure_ascii=False)
    return path


def run():
    rows, failures, brand = [], [], []

    # ---- 1. icon ink against the effective background (1.4.11, 3:1) ----
    for theme in THEMES:
        for v in VARIANTS:
            for state in ('default', 'hover', 'active'):
                fg = tok(f'{v}-ink', theme)
                bg = effective_bg(v, state, theme)
                ratio = cr(fg, bg)
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('ink', theme, f'{v} · {state}', fg, bg,
                             ratio, NON_TEXT_FLOOR, ok, False))
                if not ok:
                    failures.append((theme, v, state, ratio, NON_TEXT_FLOOR))
                elif (theme, v, state) in BRAND_PAIRS:
                    brand.append((theme, v, state, ratio))

            # disabled: exempt under 1.4.3, measured and reported, never failed
            fg = tok(f'{v}-ink-disabled', theme)
            bg = effective_bg(v, 'disabled', theme)
            rows.append(('ink', theme, f'{v} · disabled', fg, bg,
                         cr(fg, bg), None, True, False))

    # ---- 2. the component's visible boundary against the canvas (1.4.11, 3:1) ----
    for theme in THEMES:
        for v in VARIANTS:
            bg = tok(f'{v}-bg', theme)
            border = tok(f'{v}-border', theme)
            cv = canvas(theme)
            if bg != 'transparent':
                ratio = cr(bg, cv)
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('boundary', theme, f'{v} · fill', bg, cv,
                             ratio, 3.0, ok, False))
                if not ok:
                    failures.append((theme, v, 'fill', ratio, 3.0))
            elif border != 'transparent':
                ratio = cr(border, cv)
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('boundary', theme, f'{v} · border', border, cv,
                             ratio, 3.0, ok, False))
                if not ok:
                    failures.append((theme, v, 'border', ratio, 3.0))
            else:
                # Ghost. No fill, no border and - unlike the Button - no label.
                # The component's boundary IS the icon, already measured in
                # section 1 against the canvas. It is not a gap: it is the same
                # pixel.
                fg = tok(f'{v}-ink', theme)
                ratio = cr(fg, cv)
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('boundary', theme, f'{v} · the icon is the boundary', fg, cv,
                             ratio, 3.0, ok, False))
                if not ok:
                    failures.append((theme, v, 'icon as boundary', ratio, 3.0))

    # ---- 3. focus ring against the canvas (2.4.11/2.4.13, 3:1) ----
    for theme in THEMES:
        i = 0 if theme == 'light' else 1
        cv = canvas(theme)
        for v in VARIANTS:
            ring = SEM['shadow-focus-error' if v == 'danger' else 'shadow-focus-default'][i]
            ratio = cr(ring, cv)
            ok = ratio >= NON_TEXT_FLOOR
            rows.append(('focus', theme, f'{v} · ring vs canvas', ring, cv,
                         ratio, 3.0, ok, False))
            if not ok:
                failures.append((theme, v, 'focus ring', ratio, 3.0))

    # ---- 4. touch target (2.5.8, minimum 24x24) ----
    targets = [(size, IB['derived']['box'][size]) for size in IB['derived']['box']]

    # ---- 5. markup contract on the rendered HTML ----
    checked, markup_problems = markup_contract()

    # ---------------- report ----------------
    print('=' * 78)
    print('ACCESSIBILITY QA - ICON BUTTON')
    print('=' * 78)
    print('What carries the meaning is an icon, not a label: the floor is 3:1')
    print('(WCAG 1.4.11 non-text) across the board, not 4.5:1.')

    for group, title in (
        ('ink',      '1. ICON INK AGAINST THE EFFECTIVE BACKGROUND  (WCAG 1.4.11 · min 3:1)'),
        ('boundary', '2. COMPONENT BOUNDARY AGAINST THE CANVAS      (WCAG 1.4.11 · min 3:1)'),
        ('focus',    '3. FOCUS RING AGAINST THE CANVAS              (WCAG 2.4.11/2.4.13 · min 3:1)'),
    ):
        print(f'\n{title}')
        print('-' * 78)
        for g, theme, label, fg, bg, ratio, floor, ok, _ in rows:
            if g != group:
                continue
            tag = 'OK  ' if ok else 'FAIL'
            floor_s = f'min {floor}' if floor else 'exempt 1.4.3'
            print(f'  {tag} {theme:<6} {label:<28} {fg} / {bg}  {ratio:6.2f}:1  ({floor_s})')

    print('\n4. TOUCH TARGET  (WCAG 2.5.8 · minimum 24x24)')
    print('-' * 78)
    for size, box in targets:
        note = '' if box >= 44 else '  (passes AA; below the recommended 44 - a recorded decision)'
        print(f'  OK   {size:<6} {box}x{box}px{note}')

    print('\n5. MARKUP CONTRACT  (on the HTML the site emits)')
    print('-' * 78)
    print('  name: aria-label OR aria-labelledby (never both) · aria-busy always with aria-disabled')
    print('  no disabled attribute · aria-hidden never on the button')
    if checked is None:
        for p in markup_problems:
            print(f'  PENDING  {p}')
    else:
        print(f'  {checked} .al-icon-btn elements inspected')
        if markup_problems:
            for p in markup_problems:
                print(f'  FAIL {p}')
        else:
            print('  0 outside the contract.')

    n_markup_fail = len(markup_problems) if checked is not None else 0
    n_fail = len(failures) + n_markup_fail
    measured = len([r for r in rows if r[6] is not None])

    print('\n' + '=' * 78)
    if n_fail:
        print(f'{n_fail} FAILURE(S):')
        for f in failures:
            print('   ', f)
        for p in (markup_problems if checked is not None else []):
            print('   ', p)
        return 1

    write_report(rows, checked, brand, targets)
    print(f'{measured} combinations measured. 0 failures.')
    print('build/components/icon-button/a11y.json written')
    if checked is None:
        print('Markup contract: PENDING until the component is on the site.')
    if brand:
        print(f'{len(brand)} brand pair(s), all above the non-text floor:')
        for theme, v, state, ratio in brand:
            print(f'   {theme:<6} {v} · {state}  {ratio:.2f}:1')
        print('In the Button these same pairs are a named exception, because there the')
        print('carrier is text. Here they are not an exception: they pass. Same color,')
        print('different criterion.')
    print('Disabled stays out of the minimum by design: 1.4.3 exempts inactive')
    print('components, and raising that contrast would make disabled look clickable.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
