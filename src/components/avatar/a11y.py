"""
Accessibility QA for the Avatar.

As in the Button, Icon Button, Icon and Tag, validation is by RENDERED
COMBINATION - each color role against the effective background, not a loose
token pair. But the Avatar's background never varies: it is always
`avatar-bg`, solid, in all three types (including the Photo, where it is the
floor while the image loads). So the contrast measurement here is the
shortest in the system so far - two roles, two themes, four rows - because
there is no type x status combination to multiply.

TWO FLOORS, ON THE SAME COLOR PAIR

  `label` (initials) is text: 4.5:1 floor from 1.4.3.
  `icon` (the Icon type's glyph) is non-text: 3:1 floor from 1.4.11.
  Both resolve to the same hex today (both point to `text-primary`), but each
  one is measured against its own floor - not against the easier one, the same
  rule the Tag set for its label.

WHAT DOESN'T EXIST HERE, AND WHY

  No FOCUS RING section: the Avatar never gets focus (a finding of the audit),
  so there is no ring to measure. A deliberate omission, not a forgotten one.
  No TOUCH TARGET section: the Avatar is not actionable, so the 2.5.8 floor
  (minimum touch area) doesn't apply - it is not a control.

THE MARKUP CONTRACT IS THE HEART OF THIS GATE

  Three rules, all from usage rule 12:

    a) the `.al-avatar` wrapper is ALWAYS decorative (aria-hidden="true") OR
       carries the meaning (role="img" + a non-empty aria-label) - never
       neither, never both at the same time;
    b) the photo (`.al-avatar__photo`) ALWAYS has `alt=""`, because the name
       lives on the wrapper - a filled alt would duplicate the announcement;
    c) the icon (`.al-icon` inside the Avatar) is ALWAYS decorative on its own
       tag, because the Icon type's meaning (if any) lives on the wrapper,
       never on the glyph - the same contract icon.css already documents for
       the inside of any actionable element.

  That is really checkable on the emitted HTML, and it is what this section does.

Run: python3 a11y.py [path.html]
     with no argument, measures build/site/index.html
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import ROOT, TOKENS_JSON, SITE_HTML, comp_out  # noqa: E402
from contrast import cr  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
AVATAR = json.load(open(comp_out('avatar', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = AVATAR['resolved']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5          # 1.4.3 - the initials are text
NON_TEXT_FLOOR = 3.0      # 1.4.11 - the icon is a graphic element

SITE = SITE_HTML


def tok(name, theme):
    v = RES[f'avatar-{name}']
    return v[theme] if isinstance(v, dict) else v


# ─────────────────────────────────────────────── markup contract
OPEN_AVATAR = re.compile(r'<(\w+)\b([^>]*\bclass="[^"]*\bal-avatar\b[^"]*"[^>]*)>')
IMG_TAG = re.compile(r'<img\b[^>]*\bclass="[^"]*\bal-avatar__photo\b[^"]*"[^>]*/?>')
SVG_TAG = re.compile(r'<svg\b[^>]*\bclass="[^"]*\bal-icon\b[^"]*"[^>]*>')
ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')


def attrs_of(tag_str):
    return dict(ATTR.findall(tag_str))


def find_matching_close(html, start, elem):
    """Finds the </elem> that closes the tag opened at `start`, respecting the
    nesting of the SAME element (the wrapper is a <span>, and the Initials are
    a <span> too - closing at the first </span> would catch the child)."""
    open_re = re.compile(rf'<{elem}\b')
    close_re = re.compile(rf'</{elem}>')
    depth, pos = 1, start
    while depth > 0:
        cm = close_re.search(html, pos)
        if not cm:
            return None
        om = open_re.search(html, pos, cm.start())
        if om:
            depth += 1
            pos = om.end()
        else:
            depth -= 1
            pos = cm.end()
    return cm.start(), cm.end()


def markup_contract(path):
    """Enforces the contract of each .al-avatar on the HTML. See the module
    docstring for the three rules (a, b, c).

    Returns (checked, problems). checked = None when the HTML doesn't emit the
    component yet - the case until the playground is built. PENDING, not a
    failure: the gate starts counting by itself when the HTML shows up.
    """
    if not os.path.exists(path):
        return None, [f'{path} does not exist']

    html = open(path).read()
    for pat in (r'<style\b.*?</style>', r'<script\b.*?</script>', r'<!--.*?-->'):
        html = re.sub(pat, lambda m: '\n' * m.group(0).count('\n'), html, flags=re.S)

    checked, problems = 0, []

    for m in OPEN_AVATAR.finditer(html):
        elem, attr_str = m.group(1), m.group(2)
        attrs = attrs_of(attr_str)
        line = html.count('\n', 0, m.start()) + 1
        checked += 1

        # (a) decorative XOR carries the meaning - never neither, never both
        hidden = attrs.get('aria-hidden') == 'true'
        role_img = attrs.get('role') == 'img'
        label = attrs.get('aria-label', '').strip()

        if elem.lower() == 'button':
            problems.append(f'line {line}: .al-avatar is a <button> - it is content, '
                            f'not a control; a clickable avatar wraps an actionable OUTSIDE it')
        if 'role="button"' in attr_str:
            problems.append(f'line {line}: role="button" on the avatar - it is never '
                            f'actionable on its own')
        if re.search(r'\btabindex="0"', attr_str):
            problems.append(f'line {line}: tabindex="0" on the avatar - it stays out '
                            f'of the tab order by design')

        if hidden and role_img:
            problems.append(f'line {line}: aria-hidden="true" and role="img" together - '
                            f'contradictory, the screen reader doesn\'t know which to follow')
        elif not hidden and not role_img:
            problems.append(f'line {line}: neither aria-hidden nor role="img" - the '
                            f'contract requires one of the two, never neither')
        elif role_img and not label:
            problems.append(f'line {line}: role="img" without aria-label (or empty) - '
                            f'an avatar on its own with no accessible name')

        close = find_matching_close(html, m.end(), elem)
        inner = html[m.end():close[0]] if close else html[m.end():]

        img_m = IMG_TAG.search(inner)
        if img_m:
            img_attrs = attrs_of(img_m.group(0))
            if 'alt' not in img_attrs:
                problems.append(f'line {line}: .al-avatar__photo without an alt attribute - '
                                f'it has to exist and be empty, the name lives on the wrapper')
            elif img_attrs['alt'] != '':
                problems.append(f'line {line}: .al-avatar__photo with alt="'
                                f'{img_attrs["alt"]}" - it has to be empty, or the name '
                                f'is announced twice (rule 12)')

        svg_m = SVG_TAG.search(inner)
        if svg_m:
            svg_attrs = attrs_of(svg_m.group(0))
            if svg_attrs.get('aria-hidden') != 'true':
                problems.append(f'line {line}: .al-icon inside the avatar without '
                                f'aria-hidden="true" - the meaning lives on the wrapper, '
                                f'never on the glyph')
            if svg_attrs.get('focusable') != 'false':
                problems.append(f'line {line}: .al-icon inside the avatar without '
                                f'focusable="false" - inline SVG enters the tab order '
                                f'by itself in some browsers')

    if checked == 0:
        return None, ['no .al-avatar in the HTML - the component enters the site with '
                      'its playground; until then this gate stays pending']
    return checked, problems


def write_report(rows, checked, path_html):
    out = {
        'component': 'avatar',
        'criterion': 'WCAG 1.4.3 text (initials) + 1.4.11 non-text (icon)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path_html, ROOT),
        'markupChecked': checked,
        'markupPending': checked is None,
        'fails': sum(1 for r in rows if not r[5]),
        'noFocusRing': 'the avatar never gets focus - no ring section',
        'noTouchTarget': 'the avatar is not actionable - the 2.5.8 floor does not apply',
        'rows': [{'theme': t, 'what': w, 'fg': fg, 'bg': bg,
                  'ratio': round(ratio, 2), 'floor': floor, 'pass': ok}
                 for t, w, fg, bg, ratio, ok, floor in rows],
    }
    p = comp_out('avatar', 'a11y.json')
    json.dump(out, open(p, 'w'), indent=2, ensure_ascii=False)
    return p


def run(path_html):
    rows, failures = [], []
    floors = {'label': TEXT_FLOOR, 'icon': NON_TEXT_FLOOR}

    for theme in THEMES:
        bg = tok('bg', theme)
        for what, floor in floors.items():
            fg = tok(what, theme)
            ratio = cr(fg, bg)
            ok = ratio >= floor
            rows.append((theme, what, fg, bg, ratio, ok, floor))
            if not ok:
                failures.append((theme, what, ratio, floor))

    checked, mk_problems = markup_contract(path_html)

    print('=' * 74)
    print('AVATAR ACCESSIBILITY QA')
    print('=' * 74)
    print('\nCOLOR against the effective background (avatar-bg, the same in all three types)')
    for theme, what, fg, bg, ratio, ok, floor in rows:
        mark = 'ok' if ok else 'XX'
        criterion = '1.4.3 text' if what == 'label' else '1.4.11 non-text'
        print(f'  {mark} {theme:<5} {what:<6} {fg} on {bg}  {ratio:5.2f}  '
              f'floor {floor} ({criterion})')

    print('\nFOCUS RING')
    print('     n/a - the avatar never gets focus')
    print('\nTOUCH TARGET')
    print('     n/a - the avatar is not actionable, 2.5.8 does not apply')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path_html, ROOT)}')
    if checked is None:
        for p in mk_problems:
            print(f'     pending: {p}')
    else:
        print(f'     {checked} avatar(s) checked')
        for p in mk_problems:
            print(f'     PROBLEM: {p}')

    print('-' * 74)
    print(f'{len(rows)} combinations  |  pass: {len(rows) - len(failures)}  |  '
          f'fail: {len(failures)}  |  exceptions: 0')

    path = write_report(rows, checked, path_html)
    print(f'{os.path.relpath(path, ROOT)} written')

    if failures:
        print('-' * 74)
        print(f'{len(failures)} COMBINATION(S) FAIL:')
        for theme, what, ratio, floor in failures:
            print(f'   {theme} {what}: {ratio:.2f} < {floor}')
        return 1
    if checked is not None and mk_problems:
        print('-' * 74)
        print(f'{len(mk_problems)} MARKUP PROBLEM(S) - gate fails')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else SITE))
