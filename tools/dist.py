"""
Assembles the published package (dist/) from build/ and src/.

    dist/
      al.css                   Foundation + the 23 components, in one file
      foundation.css           only the Foundation
      tokens.json              the Foundation tokens, to read from code
      components/<c>.css       the component's tokens + its CSS, in one file
      components/<c>.js        the behavior, for components that have a script
      icons/*.svg, icons.json  the icons (Lucide, ISC - see icons/NOTICE)
      icons/NOTICE

Users choose: the whole al.css, or foundation.css + the CSS of each component
they use. Every component CSS depends on the Foundation.

Runs at the end of build.py, after every gate: dist/ only exists if everything
passed. It deletes and rebuilds the whole folder each time, so no file from a
previous build is left behind.

Run: python3 tools/dist.py (or the full build: python3 build.py)
"""
import json
import os
import shutil
import sys

from paths import (COMPONENTS, DIST, FOUNDATION_CSS, SRC, TOKENS_JSON,
                   comp_out, comp_src, rel)


def read(path):
    return open(path, encoding='utf-8').read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)


def run():
    folders = sorted(os.listdir(os.path.join(SRC, 'components')))
    missing = sorted(set(folders) - set(COMPONENTS))
    if missing:
        print(f'Component missing from the COMPONENTS list in tools/paths.py: {", ".join(missing)}')
        print('Unless it is on the list, it does not go into the package.')
        return 1

    if os.path.exists(DIST):
        shutil.rmtree(DIST)

    version = json.load(open(TOKENS_JSON))['meta']['version']
    foundation = read(FOUNDATION_CSS)
    write(os.path.join(DIST, 'foundation.css'), foundation)
    shutil.copyfile(TOKENS_JSON, os.path.join(DIST, 'tokens.json'))

    # Same join the site does: the component's tokens, then its CSS.
    parts, scripts = [], []
    for c in COMPONENTS:
        css = read(comp_out(c, f'al-{c}-tokens.css')) + '\n' + read(comp_src(c, f'{c}.css'))
        write(os.path.join(DIST, 'components', f'{c}.css'), css)
        parts.append(css)
        js = comp_src(c, f'{c}.js')
        if os.path.exists(js):
            shutil.copyfile(js, os.path.join(DIST, 'components', f'{c}.js'))
            scripts.append(c)

    banner = (f'/* AL Design System {version} - Foundation + {len(COMPONENTS)} components.\n'
              f' * MIT. https://github.com/guilhermedworakowski/al-design-system\n'
              f' */\n')
    write(os.path.join(DIST, 'al.css'), banner + foundation + '\n' + '\n'.join(parts))

    icons = os.path.join(DIST, 'icons')
    shutil.copytree(comp_src('icon', 'icons'), icons)
    shutil.copyfile(comp_out('icon', 'icons.json'), os.path.join(icons, 'icons.json'))
    shutil.copyfile(comp_src('icon', 'NOTICE'), os.path.join(icons, 'NOTICE'))
    n_icons = len([f for f in os.listdir(icons) if f.endswith('.svg')])

    total = sum(os.path.getsize(os.path.join(d, f))
                for d, _, fs in os.walk(DIST) for f in fs)
    print(f'{rel(DIST)}/ assembled - version {version}')
    print(f'  al.css            : {os.path.getsize(os.path.join(DIST, "al.css")):,} bytes')
    print(f'  components        : {len(COMPONENTS)} CSS, {len(scripts)} JS ({", ".join(scripts)})')
    print(f'  icons             : {n_icons}')
    print(f'  total             : {total:,} bytes')
    return 0


if __name__ == '__main__':
    sys.exit(run())
