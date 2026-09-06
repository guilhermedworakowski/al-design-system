"""
Portao do desenho do Icon, e gerador do manifesto.

Os outros portoes do AL olham para token e para CSS. Este olha para o ARQUIVO
DO ICONE, e existe por um motivo especifico: o risco desta pasta nao e alguem
escrever um valor errado, e alguem colar aqui um icone de outra familia. Um
Material ou um Font Awesome no meio de 70 Lucide passa despercebido no diff e
so aparece na tela, torto, meses depois.

O que ele exige de cada arquivo, e o porque de cada exigencia:

  viewBox 0 0 24 24    o grid. Sem ele o icone nao escala junto com os outros.
  stroke-width 2       a espessura da familia no grid de 24.
  stroke currentColor  o mecanismo de cor do componente. Um `stroke="#000"`
                       aqui ignora o tema e nao ha CSS que salve.
  fill none            desenho de traco, nao de massa.
  linecap/linejoin     round nos dois. E o que separa Lucide de Feather.
  sem atributo class   a classe e do consumidor (`al-icon`), nao do arquivo.

Rodar: python3 icons.py     (escreve icons.json, nao redirecionar stdout)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
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
        print(f'pasta nao encontrada: {ICONS}')
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
                problems.append(f'{name}: {key} e "{got}", esperado "{want}"')

        if 'class' in a:
            problems.append(f'{name}: tem atributo class="{a["class"]}" - a classe e do consumidor')

        # cor cravada em qualquer lugar do desenho, nao so no <svg>
        inner = body[body.find('>', body.find('<svg')) + 1:]
        for m in HEX.finditer(inner):
            problems.append(f'{name}: cor literal {m.group(0)} dentro do desenho')

    print('=' * 70)
    print('PORTAO DO DESENHO DO ICON')
    print('=' * 70)
    print(f'  pasta      : components/icon/icons/')
    print(f'  arquivos   : {len(files)}')
    print(f'  familia    : Lucide - grid 24, traco 2, cap e join redondos')
    print(f'  licenca    : ISC (ver components/icon/NOTICE) - o resto do AL e MIT')
    print('-' * 70)

    if problems:
        print(f'{len(problems)} ICONE(S) FORA DA FAMILIA - PORTAO REPROVA:')
        for p in problems:
            print('   ', p)
        return 1

    print(f'{len(files)} icones, todos no mesmo grid e na mesma espessura.')

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
    path = os.path.join(HERE, 'icons.json')
    json.dump(manifest, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f'components/icon/icons.json escrito ({len(names)} nomes)')
    return 0


if __name__ == '__main__':
    sys.exit(run())
