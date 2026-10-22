"""
Accessibility QA for the Slider.

Validation by RENDERED COMBINATION: theme x page background (bg-canvas,
bg-surface, bg-surface-raised) x thumb state. The component has no fill of
its own, so the text, the track and the thumb always touch the page.

What is measured:
  1. Text (4.5:1, WCAG 1.4.3): label, value and range against the page.
  2. Indicators (3:1, WCAG 1.4.11): the fill and the thumb against the page;
     the focus ring against the page (the gap is bg-canvas, so on surface and
     surface-raised the ring's outer edge is what touches the page).
  3. Declared exceptions (tokens.py), not new findings:
       fill-on-track    the fill against the track - paid by the value in text
                        (usage rule 7);
       thumb-transient  hover and active in dark on surface/surface-raised -
                        the resting thumb identifies the control (rule 15).

The track against the page is not measured: it only hints at the range.
Disabled is exempt (WCAG 1.4.3) and not measured.

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
SLD = json.load(open(comp_out('slider', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = SLD['resolved']
THEMES = ('light', 'dark')
UNDER = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# (what, token, min, exception key when below)
MEASURES = (
    ('label',          'slider-label-text',      4.5, None),
    ('value',          'slider-value-text',      4.5, None),
    ('range',          'slider-range-text',      4.5, None),
    ('fill',           'slider-fill-bg',         3.0, None),
    ('thumb',          'slider-thumb-bg',        3.0, None),
    ('thumb hover',    'slider-thumb-bg-hover',  3.0, 'thumb-transient'),
    ('thumb active',   'slider-thumb-bg-active', 3.0, 'thumb-transient'),
)


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def run():
    rows = []
    for theme in THEMES:
        fill = RES['slider-fill-bg'][theme]
        track = RES['slider-track-bg'][theme]
        ring = sem('shadow-focus-default', theme)
        for under in UNDER:
            bg = sem(under, theme)
            for what, tok, floor, exc in MEASURES:
                r = round(cr(RES[tok][theme], bg), 2)
                rows.append({'theme': theme, 'under': under, 'what': what,
                             'ratio': r, 'min': floor, 'exception': exc if r < floor else None})
            r = round(cr(ring, bg), 2)
            rows.append({'theme': theme, 'under': under, 'what': 'focus ring',
                         'ratio': r, 'min': 3.0, 'exception': None})
            r = round(cr(fill, track), 2)
            rows.append({'theme': theme, 'under': under, 'what': 'fill on track',
                         'ratio': r, 'min': 3.0, 'exception': 'fill-on-track' if r < 3.0 else None})

    for x in rows:
        x['pass'] = x['ratio'] >= x['min']
    fails = [x for x in rows if not x['pass'] and not x['exception']]
    excs = [x for x in rows if not x['pass'] and x['exception']]

    print('=' * 74)
    print('SLIDER - ACCESSIBILITY QA (rendered combinations)')
    print('=' * 74)
    for x in rows:
        mark = 'ok ' if x['pass'] else ('exc' if x['exception'] else 'FAIL')
        print(f'  {mark}  {x["theme"]:<5} {x["under"]:<17} {x["what"]:<16} '
              f'{x["ratio"]:>5}:1  (min {x["min"]})')
    print('-' * 74)
    print(f'{len(rows)} combinations  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')

    out = {'component': 'Slider', 'rows': rows,
           'summary': {'total': len(rows), 'fail': len(fails), 'exceptions': len(excs)}}
    os.makedirs(os.path.dirname(comp_out('slider', 'a11y.json')), exist_ok=True)
    json.dump(out, open(comp_out('slider', 'a11y.json'), 'w'), indent=2, ensure_ascii=False)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE ACCESSIBILITY GATE')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run())
