"""
Parity gate: the Node validator shipped in the package (dist/mcp) and the
Python checker the build uses (tools/contract.py) must give the same answer.

Both read the same rules (contract.json -> components.json), but each has its
own HTML reader and its own engine. This gate runs both on the site pages and
on broken copies of them (attributes stripped on purpose, so there is plenty
to find), and fails at the first finding one side reports and the other
doesn't. Runs after dist.py, which is what puts the Node side in place.

Needs Node (the release workflow has it). Run: python3 tools/parity.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import contract
from contractgate import SKIP
from htmltree import Tree
from paths import BUILD, COMPONENTS, DIST, rel

PAGES = [os.path.join(BUILD, 'site', 'index.html'), os.path.join(BUILD, 'site', 'pt', 'index.html')]
# Each one strips an attribute everywhere: hundreds of breaks, on every kind of rule.
BREAKS = {
    'no aria-hidden': r'\saria-hidden="true"',
    'no type': r'\stype="(?:button|checkbox|radio)"',
    'no aria-label': r'\saria-label="[^"]*"',
    'no role': r'\srole="[a-z]+"',
    'no id': r'\sid="[^"]*"',
}
# And one that empties labels, titles and names, for the "has visible text" checks.
EMPTY = (r'(class="[^"]*__(?:label|title|name|text|current)\b[^"]*"[^>]*>)[^<]+', r'\1')


def python_side(html):
    t = Tree()
    t.feed(html)
    return {c: contract.check(c, t, skip=SKIP)[0] for c in COMPONENTS}


def node_side(node, path):
    out = subprocess.run([node, os.path.join(DIST, 'mcp', 'al.mjs'), 'validate', '--json',
                          '--skip', SKIP, path], capture_output=True, text=True)
    if out.returncode not in (0, 1):
        raise RuntimeError(out.stderr.strip() or 'node failed')
    return {r['component']: r['findings'] for r in json.loads(out.stdout)['results']}


def run():
    node = shutil.which('node')
    if not node:
        print('Node not found - the parity gate needs it (the package ships a Node validator).')
        return 1
    cases = [(rel(p), open(p, encoding='utf-8').read()) for p in PAGES]
    base = cases[0][1]
    cases += [(f'{rel(PAGES[0])} ({name})', re.sub(pat, '', base)) for name, pat in BREAKS.items()]
    cases.append((f'{rel(PAGES[0])} (no text)', re.sub(*EMPTY, base)))

    problems, total = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, html in cases:
            path = os.path.join(tmp, 'page.html')
            open(path, 'w', encoding='utf-8').write(html)
            py, js = python_side(html), node_side(node, path)
            n = sum(len(v) for v in py.values())
            total += n
            for c in COMPONENTS:
                if py.get(c, []) != js.get(c, []):
                    only_py = [f for f in py.get(c, []) if f not in js.get(c, [])]
                    only_js = [f for f in js.get(c, []) if f not in py.get(c, [])]
                    problems.append(f'{name} - {c}: Python only {only_py[:2]}, Node only {only_js[:2]}'
                                    + ('' if only_py or only_js else ' (same findings, different order)'))
            print(f'  {name:<48} {n:>5} findings, same on both sides'
                  if not any(p.startswith(name + ' -') for p in problems) else f'  {name:<48} DIFFERENT')

    print('-' * 78)
    if problems:
        print(f'{len(problems)} DIFFERENCE(S) BETWEEN PYTHON AND NODE - GATE FAILS:')
        for p in problems[:20]:
            print('   ', p)
        return 1
    print(f'{len(cases)} pages, {total} findings: the Node validator and the build agree on every one.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
