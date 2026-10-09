"""
Drawing gate for the Icon, and manifest generator.

The other AL gates look at tokens and CSS. This one looks at the ICON FILE,
and it exists for a specific reason: the risk in this folder is not someone
writing a wrong value, it is someone pasting in an icon from another family. A
Material or Font Awesome icon among 70 Lucide ones slips past the diff and only
shows up on screen, crooked, months later.

What it requires of each file, and why:

  viewBox 0 0 24 24    the grid. Without it the icon doesn't scale with the others.
  stroke-width 2       the family's stroke weight on the 24 grid.
  stroke currentColor  the component's color mechanism. A `stroke="#000"` here
                       ignores the theme and no CSS can save it.
  fill none            a stroke drawing, not a filled shape.
  linecap/linejoin     round on both. It is what separates Lucide from Feather.
  no class attribute   the class belongs to the consumer (`al-icon`), not the file.

Run: python3 icons.py     (writes icons.json, don't redirect stdout)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import comp_out  # noqa: E402
ICONS = os.path.join(HERE, 'icons')

EXPECTED = {
    'viewBox': '0 0 24 24',
    'stroke-width': '2',
    'stroke': 'currentColor',
    'fill': 'none',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
}

HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')


def attrs(svg):
    head = svg[svg.find('<svg'):svg.find('>', svg.find('<svg')) + 1]
    return dict(re.findall(r'([\w-]+)="([^"]*)"', head))


def run():
    if not os.path.isdir(ICONS):
        print(f'folder not found: {ICONS}')
        return 1

    files = sorted(f for f in os.listdir(ICONS) if f.endswith('.svg'))
    problems, names = [], []

    for f in files:
        name = f[:-4]
        names.append(name)
        raw = open(os.path.join(ICONS, f)).read()
        body = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
        a = attrs(body)

        for key, want in EXPECTED.items():
            got = a.get(key)
            if got != want:
                problems.append(f'{name}: {key} is "{got}", expected "{want}"')

        if 'class' in a:
            problems.append(f'{name}: has a class="{a["class"]}" attribute - the class belongs to the consumer')

        # a hard-coded color anywhere in the drawing, not only on the <svg>
        inner = body[body.find('>', body.find('<svg')) + 1:]
        for m in HEX.finditer(inner):
            problems.append(f'{name}: literal color {m.group(0)} inside the drawing')

    print('=' * 70)
    print('ICON DRAWING GATE')
    print('=' * 70)
    print(f'  folder     : src/components/icon/icons/')
    print(f'  files      : {len(files)}')
    print(f'  family     : Lucide - grid 24, stroke 2, round cap and join')
    print(f'  license    : ISC (see src/components/icon/NOTICE) - the rest of AL is MIT')
    print('-' * 70)

    if problems:
        print(f'{len(problems)} ICON(S) OUTSIDE THE FAMILY - GATE FAILS:')
        for p in problems:
            print('   ', p)
        return 1

    print(f'{len(files)} icons, all on the same grid and with the same stroke weight.')

    manifest = {
        'component': 'icon',
        'family': 'lucide',
        'source': 'lucide-static v1.41.0',
        'license': 'ISC',
        'grid': 24,
        'strokeWidth': 2,
        'count': len(names),
        'icons': names,
    }
    path = comp_out('icon', 'icons.json')
    json.dump(manifest, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f'build/components/icon/icons.json written ({len(names)} names)')
    return 0


if __name__ == '__main__':
    sys.exit(run())
