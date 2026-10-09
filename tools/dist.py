"""
Monta o pacote publicado (dist/) a partir de build/ e src/.

    dist/
      al.css                   Foundation + os 23 componentes, num arquivo so
      foundation.css           so a Foundation
      tokens.json              os tokens da Foundation, para ler por codigo
      components/<c>.css       tokens do componente + CSS dele, num arquivo
      components/<c>.js        o comportamento, nos componentes que tem script
      icons/*.svg, icons.json  os icones (Lucide, ISC - ver icons/NOTICE)
      icons/NOTICE

Quem usa escolhe: al.css inteiro, ou foundation.css + o CSS de cada componente
que for usar. Todo CSS de componente depende da Foundation.

Roda no fim do build.py, depois de todos os portoes: dist/ so existe se tudo
passou. Apaga e remonta a pasta inteira a cada vez, para nao sobrar arquivo de
um build anterior.

Rodar: python3 tools/dist.py (ou o build completo: python3 build.py)
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
    pastas = sorted(os.listdir(os.path.join(SRC, 'components')))
    fora = sorted(set(pastas) - set(COMPONENTS))
    if fora:
        print(f'Componente fora da lista COMPONENTS de tools/paths.py: {", ".join(fora)}')
        print('Sem entrar na lista, ele nao vai para o pacote.')
        return 1

    if os.path.exists(DIST):
        shutil.rmtree(DIST)

    version = json.load(open(TOKENS_JSON))['meta']['version']
    foundation = read(FOUNDATION_CSS)
    write(os.path.join(DIST, 'foundation.css'), foundation)
    shutil.copyfile(TOKENS_JSON, os.path.join(DIST, 'tokens.json'))

    # Mesma juncao que o site faz: tokens do componente, depois o CSS dele.
    parts, scripts = [], []
    for c in COMPONENTS:
        css = read(comp_out(c, f'al-{c}-tokens.css')) + '\n' + read(comp_src(c, f'{c}.css'))
        write(os.path.join(DIST, 'components', f'{c}.css'), css)
        parts.append(css)
        js = comp_src(c, f'{c}.js')
        if os.path.exists(js):
            shutil.copyfile(js, os.path.join(DIST, 'components', f'{c}.js'))
            scripts.append(c)

    banner = (f'/* AL Design System {version} - Foundation + {len(COMPONENTS)} componentes.\n'
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
    print(f'{rel(DIST)}/ montado - versao {version}')
    print(f'  al.css            : {os.path.getsize(os.path.join(DIST, "al.css")):,} bytes')
    print(f'  componentes       : {len(COMPONENTS)} CSS, {len(scripts)} JS ({", ".join(scripts)})')
    print(f'  icones            : {n_icons}')
    print(f'  total             : {total:,} bytes')
    return 0


if __name__ == '__main__':
    sys.exit(run())
