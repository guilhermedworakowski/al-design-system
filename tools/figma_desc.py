"""
Writes build/figma-descriptions.json: the description and documentation link
of every AL component in the Figma library.

An agent that reads the Figma file through the Figma MCP sees a component's
description and nothing else about the code. This turns dist/components.json
into that description, so Figma and the package say the same thing and nobody
writes it by hand:

    A button triggers an action.
    Class: .al-btn
    CSS: al-design-system/components/button.css
    Rules: guidelines/button.md · MCP get_component button

The documentation link is the component's page on the site. Internal pieces
(Figma sets named "_<component>-...") get one line that sends to the
component. A designer note already in Figma stays below the generated block,
after a line with "—" (SEPARATOR); applying again replaces only the block.

The build can't reach Figma: it also writes build/figma-apply.js (from
tools/figma_apply.js, with the data inside), which is run through the Figma
MCP once per page, as a step of each new component and of each release
(CONTRIBUTING.md).

Runs after dist.py. Uses only the Python standard library (3.9 or newer).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import BUILD, ROOT, rel  # noqa: E402

SITE = 'https://al.guilhermedesignd.com'
SEPARATOR = '—'
# Figma internal pieces -> the component they belong to.
INTERNAL = {
    '_menu-item': 'menu', '_rating-star': 'rating', '_breadcrumb-more': 'breadcrumb',
    '_pagination-item': 'pagination', '_stepper-item': 'stepper',
    '_carousel-slide': 'carousel', '_carousel-dot': 'carousel',
}


def describe(slug, c):
    # Figma stores the description escaped as HTML: <, >, " and ' would reach
    # an agent as &lt; &gt; &quot; &#39;. None of them goes into the generated
    # text: the brackets go, quotes and apostrophes become typographic ones.
    return '\n'.join([
        c['summary'].replace('<', '').replace('>', '').replace('"', '\u201d').replace("'", '\u2019'),
        f"Class: .{c['root']}",
        f"CSS: al-design-system/{c['css']}" + (f" + al-design-system/{c['js']}" if c['js'] else ''),
        # the Icon has no usage rules on purpose: the MCP is the only pointer
        'Rules: ' + (f"{c['guidelines']} · " if c['guidelines'] else '') + f'MCP get_component {slug}',
    ])


def main():
    catalog = json.load(open(os.path.join(ROOT, 'dist', 'components.json'), encoding='utf-8'))
    comps = catalog['components']
    for piece, owner in INTERNAL.items():
        if owner not in comps:
            raise SystemExit(f'{piece} points to "{owner}", which is not a component')
    data = {
        'version': catalog['version'], 'separator': SEPARATOR,
        'components': {s: {'description': describe(s, c), 'link': f'{SITE}/#/{s}'}
                       for s, c in comps.items()},
        'internal': {p: {'description': f'Internal piece of {comps[o]["title"]}. '
                                        f'Do not use alone; use {o}.',
                         'link': f'{SITE}/#/{o}'}
                     for p, o in INTERNAL.items()},
    }
    for group in ('components', 'internal'):
        for k, v in data[group].items():
            if any(ch in v['description'] for ch in '<>"&\''):
                raise SystemExit(f'{k}: the Figma description has a character Figma escapes')
    path = os.path.join(BUILD, 'figma-descriptions.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    with open(os.path.join(ROOT, 'tools', 'figma_apply.js'), encoding='utf-8') as f:
        script = f.read().replace('__DATA__', json.dumps(data, ensure_ascii=False), 1)
    with open(os.path.join(BUILD, 'figma-apply.js'), 'w', encoding='utf-8') as f:
        f.write(script)
    print(f'{rel(path)}: {len(data["components"])} components, {len(data["internal"])} internal pieces')


if __name__ == '__main__':
    main()
