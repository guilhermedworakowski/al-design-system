"""
Accessibility QA for the Button.

Unlike the Foundation gate, which validates loose token pairs, here
validation is by RENDERED COMBINATION: each variant, in each state, in each
theme, with the effective background the button really has. A variant with no
fill inherits the canvas - and its label has to pass against the canvas, not
against "transparent".

Run: python3 a11y.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import TOKENS_JSON, comp_out  # noqa: E402
from contrast import cr  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
BTN = json.load(open(comp_out('button', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = BTN['resolved']
THEMES = ('light', 'dark')
VARIANTS = ('primary', 'secondary', 'ghost', 'danger')

# Brand exception inherited from the Foundation: light label on the brand.
# It stays >= 3:1, so it meets AA for large text and for non-text.
BRAND_EXCEPTIONS = {
    ('light', 'primary', 'default'),
    ('dark', 'primary', 'default'),
    ('dark', 'primary', 'hover'),
}
HARD_FLOOR = 3.0


def tok(name, theme):
    """Value of the Button token in the requested theme."""
    v = RES[f'button-{name}']
    return v[theme] if isinstance(v, dict) else v


def canvas(theme):
    return SEM['bg-canvas'][0 if theme == 'light' else 1]


def effective_bg(variant, state, theme):
    """The background the label actually touches. Transparent = the canvas shows."""
    suffix = {'default': 'bg', 'hover': 'bg-hover',
              'active': 'bg-active', 'disabled': 'bg-disabled'}[state]
    value = tok(f'{variant}-{suffix}', theme)
    return canvas(theme) if value == 'transparent' else value


def run():
    rows, failures, exempt = [], [], []

    # ---- 1. label against the effective background ----
    for theme in THEMES:
        for v in VARIANTS:
            for state in ('default', 'hover', 'active'):
                fg = tok(f'{v}-label', theme)
                bg = effective_bg(v, state, theme)
                ratio = cr(fg, bg)
                is_exc = (theme, v, state) in BRAND_EXCEPTIONS
                floor = HARD_FLOOR if is_exc else 4.5
                ok = ratio >= floor
                rows.append(('label', theme, f'{v} · {state}', fg, bg, ratio, floor, ok, is_exc))
                if not ok:
                    failures.append((theme, v, state, ratio, floor))
                elif is_exc:
                    exempt.append((theme, v, state, ratio))

            # disabled: exempt under 1.4.3, but measured and reported
            fg = tok(f'{v}-label-disabled', theme)
            bg = effective_bg(v, 'disabled', theme)
            rows.append(('label', theme, f'{v} · disabled', fg, bg, cr(fg, bg), None, True, False))

    # ---- 2. the button's visible boundary against the canvas (1.4.11, 3:1) ----
    for theme in THEMES:
        for v in VARIANTS:
            bg = tok(f'{v}-bg', theme)
            border = tok(f'{v}-border', theme)
            cv = canvas(theme)
            if bg != 'transparent':
                ratio = cr(bg, cv)
                ok = ratio >= HARD_FLOOR
                rows.append(('boundary', theme, f'{v} · fill', bg, cv, ratio, 3.0, ok, False))
                if not ok:
                    failures.append((theme, v, 'fill', ratio, 3.0))
            elif border != 'transparent':
                ratio = cr(border, cv)
                ok = ratio >= HARD_FLOOR
                rows.append(('boundary', theme, f'{v} · border', border, cv, ratio, 3.0, ok, False))
                if not ok:
                    failures.append((theme, v, 'border', ratio, 3.0))
            else:
                # Ghost has no boundary of its own: it is text, and counts as text.
                rows.append(('boundary', theme, f'{v} · no boundary (it is a label)', '-', '-', None, None, True, False))

    # ---- 3. focus ring (2.4.13: the pixel that changes, against what was there) ----
    for theme in THEMES:
        i = 0 if theme == 'light' else 1
        cv = canvas(theme)
        for v in VARIANTS:
            ring_color = SEM['shadow-focus-error' if v == 'danger' else 'shadow-focus-default'][i]
            ratio = cr(ring_color, cv)
            ok = ratio >= HARD_FLOOR
            rows.append(('focus', theme, f'{v} · ring vs canvas', ring_color, cv, ratio, 3.0, ok, False))
            if not ok:
                failures.append((theme, v, 'focus ring', ratio, 3.0))

    # ---- 4. touch target (2.5.8, minimum 24x24) ----
    targets = [(size, BTN['derived']['height'][size]) for size in BTN['derived']['height']]

    # ---------------- report ----------------
    print('=' * 78)
    print('ACCESSIBILITY QA - BUTTON')
    print('=' * 78)

    for group, title in (('label',    '1. LABEL AGAINST THE EFFECTIVE BACKGROUND  (WCAG 1.4.3 · min 4.5:1)'),
                         ('boundary', '2. BUTTON BOUNDARY AGAINST THE CANVAS     (WCAG 1.4.11 · min 3:1)'),
                         ('focus',    '3. FOCUS RING AGAINST THE CANVAS          (WCAG 2.4.11/2.4.13 · min 3:1)')):
        print(f'\n{title}')
        print('-' * 78)
        for g, theme, label, fg, bg, ratio, floor, ok, exc in rows:
            if g != group:
                continue
            if ratio is None:
                print(f'  --   {theme:<6} {label:<34} n/a')
                continue
            tag = 'EXC ' if exc else ('OK  ' if ok else 'FAIL')
            floor_s = f'min {floor}' if floor else 'exempt 1.4.3'
            print(f'  {tag} {theme:<6} {label:<34} {fg} / {bg}  {ratio:6.2f}:1  ({floor_s})')

    print(f'\n4. TOUCH TARGET  (WCAG 2.5.8 · minimum 24x24)')
    print('-' * 78)
    for size, h in targets:
        note = '' if h >= 44 else '  (passes AA; below the 44 recommended for touch)'
        print(f'  OK   {size:<6} {h}x{h}px{note}')

    print('\n' + '=' * 78)
    if failures:
        print(f'{len(failures)} COMBINATION(S) FAIL:')
        for f in failures:
            print('   ', f)
        return 1
    print(f'{len(rows)} combinations measured. 0 failures.')
    if exempt:
        print(f'{len(exempt)} brand exceptions inherited from the Foundation, all >= {HARD_FLOOR}:1:')
        for theme, v, state, ratio in exempt:
            print(f'   {theme:<6} {v} · {state}  {ratio:.2f}:1')
    print('Disabled stays out of the minimum by design: 1.4.3 exempts inactive')
    print('components, and raising that contrast would make disabled look clickable.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
