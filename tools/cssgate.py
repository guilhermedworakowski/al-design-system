"""
Component CSS gate, in one place.

Same idea as the alias gate in tokens.py, one layer up: a component's CSS may
not contain literal values. Every color, length, font weight and duration
comes in through var(--al-*). The gate also compares the tokens tokens.py
declared (in the generated al-<c>-tokens.css) with the ones the component's
CSS and JS consume:

  - orphan: a token declared and never used (the CSS forgot to apply it, or
    the token should never have been created);
  - invented: a --al-<c>-* custom property used but never declared (a token
    that only seems to exist). One the component's own CSS declares is a
    public adjustment point, not a token (e.g. the Icon's --al-icon-box), and
    passes.

Each src/components/<c>/check.py only states what is specific to the
component: what the gate can't reach (markup contracts, enforced by a11y.py on
the site's HTML), declared exceptions and extra checks. Example:

    from cssgate import gate
    sys.exit(gate('tooltip', outside_css=[...]))

CSS keywords (none, currentColor, Canvas...) are not literal values and pass:
the gate only looks for hex, color functions, numbers with units and weights.
"""
import os
import re

from paths import comp_src, comp_out, rel

HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')
FUNC_COLOR = re.compile(r'\b(rgba?|hsla?|oklch|lab|color)\s*\(')
# literal length outside var(): 12px, 1.5rem, 2em...
LENGTH = re.compile(r'(?<![\w-])\d*\.?\d+(px|rem|em|ch|vh|vw)\b')
DURATION = re.compile(r'(?<![\w-])\d*\.?\d+m?s\b')
# hard-coded font weight: font-weight: 500
WEIGHT = re.compile(r'font-weight\s*:\s*\d+')
# the JS reads a token from the computed CSS: token(el, 'delay-show')
JS_TOKEN = re.compile(r"token\([\w.]+, '([\w-]+)'\)")


def strip_comments(text):
    return re.sub(r'/\*.*?\*/', '', text, flags=re.S)


def title(c):
    return ' '.join(p.capitalize() for p in c.split('-'))


def gate(c, outside_css=(), exceptions=(), extra=None):
    """
    c            the component's folder name ('icon-button')
    outside_css  contracts this gate can't reach (they only go into the report)
    exceptions   [(name, value, start)] - the literal `value` on a line that
                 starts with `start` is accepted and listed as a declared
                 exception (e.g. the Sidebar's ('breakpoint', '1024px', '@media'))
    extra        function(body) -> (ok, lines) for a check of its own
    Returns 0 (pass) or 1 (fail).
    """
    target = comp_src(c, f'{c}.css')
    name = title(c)
    if not os.path.exists(target):
        print(f'{c}.css not found at {target}')
        return 1

    body = strip_comments(open(target).read())
    lines = body.split('\n')
    failures, declared_exc = [], []

    for i, line in enumerate(lines, 1):
        src = line.strip()
        hits = [('literal hex', m.group(0)) for m in HEX.finditer(line)]
        hits += [('color function', m.group(0) + '…)') for m in FUNC_COLOR.finditer(line)]
        hits += [('literal length', m.group(0)) for m in LENGTH.finditer(line)]
        hits += [('literal weight', m.group(0)) for m in WEIGHT.finditer(line)]
        hits += [('literal duration', m.group(0)) for m in DURATION.finditer(line)]
        for kind, val in hits:
            exc = next((n for n, v, start in exceptions if val == v and src.startswith(start)), None)
            if exc:
                declared_exc.append((i, exc, src))
            else:
                failures.append((i, kind, val, src))

    n_vars = len(set(re.findall(r'var\(\s*(--al-[\w-]+)', body)))
    used = set(re.findall(rf'var\(\s*(--al-{c}-[\w-]+)', body))
    js = comp_src(c, f'{c}.js')
    if os.path.exists(js):
        used |= {f'--al-{c}-{n}' for n in JS_TOKEN.findall(open(js).read())}

    tokens_css = comp_out(c, f'al-{c}-tokens.css')
    declared = set()
    if os.path.exists(tokens_css):
        declared = set(re.findall(rf'^\s*(--al-{c}-[\w-]+)\s*:',
                                  open(tokens_css).read(), flags=re.M))
    local = set(re.findall(rf'(--al-{c}-[\w-]+)\s*:', body))
    orphans = sorted(declared - used)
    invented = sorted(used - declared - local)

    print('=' * 70)
    print(f'{name.upper()} CSS GATE')
    print('=' * 70)
    print(f'  file                     : src/components/{c}/{c}.css')
    print(f'  custom properties used   : {n_vars}  ({len(used)} from the {name} layer)')
    print(f'  declared tokens          : {len(declared)}')
    if local:
        print(f'  public adjustment in CSS : {", ".join(sorted(local))}')
    print(f'  lines                    : {len(lines)}')
    print('-' * 70)
    for contract in outside_css:
        print(f'outside the reach of this gate: {contract}')
    if outside_css:
        print('-' * 70)
    for ln, exc, src in declared_exc:
        print(f'declared exception `{exc}`: line {ln:>3}  {src[:52]}')

    ok = True
    if extra:
        extra_ok, extra_lines = extra(body)
        for t in extra_lines:
            print(t)
        ok = ok and extra_ok

    # With no declared token, the two counts below measure nothing: orphan
    # comes out empty and invented would flag everything. A missing or empty
    # tokens file is a tokens.py failure, and the gate fails before counting.
    if not declared:
        print(f'NO {name.upper()} TOKEN DECLARED IN {rel(tokens_css)} - GATE FAILS:')
        print(f'   the file does not exist or declares no --al-{c}-*.')
        print(f'   Run the component\'s tokens.py and check its output.')
        return 1

    if invented:
        print(f'{len(invented)} {name.upper()} CUSTOM PROPERTY(IES) THAT DO NOT EXIST IN THE TOKEN LAYER:')
        for t in invented:
            print('   ', t)
        ok = False

    if orphans:
        print(f'{len(orphans)} TOKEN(S) DECLARED AND NEVER USED - GATE FAILS:')
        for t in orphans:
            print('   ', t)
        print('   a token nobody consumes is a token that only seems to exist: either')
        print('   the CSS forgot to apply it, or the token should never have been created.')
        ok = False

    if failures:
        print(f'{len(failures)} LITERAL VALUE(S) - GATE FAILS:')
        for ln, kind, val, src in failures:
            print(f'   line {ln:>3}  {kind:<20} {val:<12} {src[:44]}')
        ok = False

    if not ok:
        return 1
    print(f'0 literal color, length, weight or duration values'
          f'{f" ({len(declared_exc)} declared exception(s))" if declared_exc else ""}.')
    print(f'{len(declared)} tokens declared, {len(used - local)} consumed, 0 orphans.')
    return 0
