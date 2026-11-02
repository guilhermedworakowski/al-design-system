"""
Markup contract gate, for every component at once.

Reads each src/components/<c>/contract.json and checks it on the HTML the site
emits (tools/contract.py does the checking). It fails when:

  - a component has no contract.json - every component goes in the catalog
    with its rules, the agent can't be left guessing;
  - the HTML breaks a rule;
  - none of a component's rules matches an element on the site - nothing
    measured is not nothing wrong. A single rule with no match (a case the
    site doesn't show, like <a class="al-btn">) is listed, not failed: the
    sabotages are what prove each rule bites.

Runs after the site, like the a11y.py files that measure HTML.

Run: python3 tools/contractgate.py [page.html] (or the full build: python3 build.py)
"""
import os
import sys

import contract
from htmltree import Tree
from paths import COMPONENTS, SITE_HTML, rel

# What the site shows but nobody uses: samples under inert (the "All states"
# grids) and the gallery thumbnails, which are pictures made of components.
SKIP = '[inert], .card-thumb'


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else SITE_HTML
    tree = Tree()
    tree.feed(open(path, encoding='utf-8').read())

    problems, unexercised, total = [], [], 0
    print(f'markup contract - {rel(path)}')
    for c in COMPONENTS:
        if not os.path.exists(contract.path_of(c)):
            problems.append(f'{c}: no contract.json')
            continue
        data = contract.load(c)
        findings, n = contract.check(c, tree, data, skip=SKIP)
        problems += [f'{c}: {f}' for f in findings]
        live = [r for r in data.get('rules', []) if not r.get('absent')]
        idle = [r['id'] for r in live if not contract.select(tree, r['on'])]
        if live and len(idle) == len(live):
            problems.append(f'{c}: no rule matches anything on the site - nothing measured')
        elif idle:
            unexercised.append(f'{c}: {", ".join(idle)}')
        total += len(data.get('rules', []))
        print(f'  {c:<14} {len(data.get("rules", [])):>3} rules  {len(data.get("manual", [])):>3} manual  '
              f'{n:>4} elements  {"ok" if not findings else str(len(findings)) + " break(s)"}')

    print('-' * 78)
    if unexercised:
        print('rules with no match on the site (proved by the sabotages, not by the page):')
        for u in unexercised:
            print('   ', u)
        print('-' * 78)
    if problems:
        print(f'{len(problems)} PROBLEM(S) - GATE FAILS:')
        for p in problems:
            print('   ', p)
        return 1
    print(f'{total} rules on {len(COMPONENTS)} components: all in order.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
