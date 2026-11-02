"""
Writes build/site/llms.txt: the map of the AL Design System for an agent.

The site is one HTML page of about 3 MB per language, routed by #hash. An agent
that fetches al.guilhermedesignd.com/#menu gets the whole page and can't tell
where the Menu starts. llms.txt (llmstxt.org) is the plain-text door next to
it: what AL is, how to install it, and for each component a link to its usage
rules and to the CSS whose header holds the markup contract.

The links point to the raw files on GitHub's main branch, the same branch the
site is published from, so the map and what it points to never disagree. The
component list and each description come from the repo (paths.COMPONENTS and
the first sentence of each guidelines.md): a new component enters by itself.

Runs after the site (it writes inside build/site/). Uses only the Python
standard library (3.9 or newer).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import BUILD, COMPONENTS, TOKENS_JSON, comp_src, out, rel  # noqa: E402

REPO = 'guilhermedworakowski/al-design-system'
RAW = f'https://raw.githubusercontent.com/{REPO}/main'
SITE = 'https://al.guilhermedesignd.com'
TOKENS = 'https://cdn.jsdelivr.net/npm/al-design-system/dist/tokens.json'
TARGET = os.path.join(BUILD, 'site', 'llms.txt')

# The Icon has no guidelines (guidegate.NO_GUIDELINES): its line is written here.
ICON = ('Icon', 'Inline SVG that inherits the text color; the drawings live in '
        'dist/icons/ and the class goes on the <svg> itself.')


def name_and_summary(c):
    """('Number field', 'The number field holds ...') from the guidelines header."""
    if c == 'icon':
        return ICON
    text = open(comp_src(c, 'guidelines.md'), encoding='utf-8').read()
    title = re.match(r'# (.+?) · ', text).group(1)
    header = text.split('\n## ', 1)[0].split('\n')
    summary = next(l for l in header[1:] if l.strip() and not l.startswith('- '))
    return title, summary.replace('**', '').strip()


def build():
    version = json.load(open(TOKENS_JSON))['meta']['version']
    lines = [
        '# AL Design System',
        '',
        '> Open-source design system in plain CSS, with a little vanilla JavaScript '
        'only where CSS can\'t reach, and no dependencies. Foundation tokens (OKLCH '
        f'color, light and dark themes) and {len(COMPONENTS)} components. Every rendered '
        'combination is checked for WCAG 2.1 AA contrast and every component\'s markup '
        f'contract is enforced by the build. Current version: {version}.',
        '',
        'Install with `npm install al-design-system` and import `al-design-system/al.css` '
        '(or `foundation.css` plus `components/<name>.css`). Components that need '
        'behavior ship a `components/<name>.js` next to the CSS.',
        '',
        'How to read a component: its CSS opens with a MARKUP CONTRACT block - the HTML '
        'to write, the modifier axes and the notes. Its guidelines.md holds the numbered '
        'usage rules (when to use, content, behavior, accessibility). State comes from '
        'the markup (native elements and ARIA attributes), never from a state class. '
        'Never write a literal color, size or duration: use the --al-* tokens.',
        '',
        '## Docs',
        '',
        f'- [README]({RAW}/README.md): install, structure, themes, the build gates',
        # tokens.json is generated (build/ is out of git): the published copy
        # on npm is the one that exists
        f'- [Tokens]({TOKENS}): primitives, semantic colors as [light, dark], type, '
        'space, radius, motion and the contrast report of every allowed '
        'text/background pair',
        f'- [Site]({SITE}): live examples, playground and contrast report (one HTML page)',
        '',
        '## Components',
        '',
    ]
    for c in COMPONENTS:
        name, summary = name_and_summary(c)
        css = f'{RAW}/src/components/{c}/{c}.css'
        if c == 'icon':
            lines.append(f'- [{name}]({css}): {summary} The CSS header holds the markup contract.')
        else:
            lines.append(f'- [{name}]({RAW}/src/components/{c}/guidelines.md): {summary} '
                         f'Markup contract: {css}')
    lines += [
        '',
        '## Optional',
        '',
        f'- [CHANGELOG]({RAW}/CHANGELOG.md): what changed in each version',
        f'- [CONTRIBUTING]({RAW}/CONTRIBUTING.md): how the repository works and what a pull request needs',
        '',
    ]
    return '\n'.join(lines)


if __name__ == '__main__':
    text = build()
    open(out(TARGET), 'w', encoding='utf-8').write(text)
    print(f'{rel(TARGET)} written: {len(COMPONENTS)} components, {len(text):,} bytes.')
