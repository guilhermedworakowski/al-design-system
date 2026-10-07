"""
Camada de tokens do Divider.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> divider-color             (hifen)
  Figma  -> color                     (collection `15. Divider`)
Sao camadas diferentes. Nunca colapsar uma na outra.

PRIMEIRO COMPONENTE DO TIER 3 (07/10/2026)

  Component set `divider`, node 304:1076, pagina `Tier 3` do Figma. Um eixo
  `Orientation` (Horizontal / Vertical). Uma espessura so (precedente Polaris),
  sem recuo, sem texto no meio, sem cor de marca ou de status.

A LINHA E O COMPONENTE - POR ISSO `color` E `thickness`

  Nos outros componentes a borda contorna uma caixa e o token se chama
  `border` / `border-width`. Aqui a linha e o proprio componente; `color` e
  `thickness` sao os nomes do Spectrum e do Material e leem igual nas duas
  orientacoes. No Figma a linha e um retangulo PREENCHIDO de 1px, nao um
  contorno - a espessura e a altura (ou a largura, na vertical).

COMPRIMENTO E MARGEM NAO TEM TOKEN

  Horizontal ocupa a largura do conteiner, vertical acompanha a altura dele.
  O espaco em volta e decisao do layout (etapa 1). Os 158/160 do Figma sao
  medida de exemplo.

ANUNCIADO OU DECORATIVO E MARCACAO, NAO TOKEN

  Opcao A de Gui (07/10/2026): `<hr>` anunciado ("separador") e o padrao;
  decorativo (`aria-hidden`) e escolha de quem usa. Visualmente identicos.

UMA EXCECAO DECLARADA DE CONTRASTE

  Ver PENDING.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'foundation'))

from build import SEM                     # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))   # noqa: E402

# --------------------------------------------------------------- cor
COLOR = {
    'color': 'border-subtle',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'thickness': 'border.width.1',
}

PENDING = {
    'linha-abaixo-de-3-1': (
        'A linha usa `border-subtle`: 1.32:1 sobre a tela e 1.23:1 sobre superficie no claro, '
        '1.66:1 / 1.36:1 no escuro - abaixo dos 3:1 do WCAG 1.4.11. O criterio so vale para '
        'objeto grafico NECESSARIO para entender o conteudo, e o divisor nunca pode ser a '
        'unica pista do agrupamento: espaco ou titulo fazem esse papel, e o leitor de tela '
        'ouve "separador" no <hr>. Decisao de Gui na etapa 1 (07/10/2026): manter o subtle. '
        'Quem sustenta a excecao e a regra de uso da etapa 4. NAO "corrigir" escurecendo.'
    ),
}

# Fundos onde o divisor e colocado. Nao sao tokens do Divider.
BACKGROUNDS = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (papel, token do divider, fundo, piso, chave da excecao em PENDING)
COMBOS = [
    ('linha-na-tela',       'color', 'canvas',  3.0, 'linha-abaixo-de-3-1'),
    ('linha-em-superficie', 'color', 'surface', 3.0, 'linha-abaixo-de-3-1'),
]


# ---------------------------------------------------------------- portao
def resolve_foundation(path):
    """Segue um caminho pontuado dentro de tokens.json. Levanta se nao existir."""
    node = FOUND
    for part in path.split('.'):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(path)
        node = node[part]
    return node


def contrast_rows():
    """Mede a linha contra cada fundo nos dois temas, contra o piso 3:1 do 1.4.11."""
    rows = []
    for what, fg_role, bg_role, min_ratio, exc in COMBOS:
        fg_ref, bg_ref = COLOR[fg_role], BACKGROUNDS[bg_role]
        for theme, i in (('light', 0), ('dark', 1)):
            ratio = round(cr(SEM[fg_ref][i], SEM[bg_ref][i]), 2)
            rows.append({
                'theme': theme, 'what': what,
                'fg': fg_ref, 'bg': bg_ref,
                'ratio': ratio, 'min': min_ratio,
                'pass': ratio >= min_ratio,
                'exception': exc,
            })
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'divider-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref}) - todo valor de cor nasce alias do semantico')
            continue
        if ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for role, ref in GEOM.items():
        name = f'divider-{role}'
        alias[name] = ref
        try:
            resolved[name] = resolve_foundation(ref)
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    if problems:
        print(f'{len(problems)} TOKEN(S) REPROVAM O PORTAO DE ALIAS:')
        for p in problems:
            print('   ', p)
        return 1

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO DIVIDER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<30} -> {alias[name]}')
    print('-' * 74)
    print(f'contraste: {len(rows)} medicoes  |  passam: {len(rows) - len(fails) - len(excs)}  |  '
          f'excecoes declaradas: {len(excs)}  |  reprovas: {len(fails)}')
    for r in rows:
        print(f'  {r["what"]:<22} {r["theme"]:<6} {r["ratio"]}:1  (piso {r["min"]})')
    for chave in PENDING:
        n = sum(1 for r in excs if r['exception'] == chave)
        print(f'  excecao "{chave}": {n} medicoes')
    print('-' * 74)

    if fails:
        print(f'{len(fails)} COMBINACAO(OES) REPROVAM O PORTAO DE CONTRASTE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1

    print(f'{len(alias)} tokens, todos alias da Foundation. 0 valores soltos.')

    out = {
        'meta': {
            'component': 'Divider',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '304:1076',
            'figmaCollection': '15. Divider',
            'variants': ['horizontal', 'vertical'],
            'sizes': [],
            'states': [],
            'nota': (
                'Linha de 1px em border-subtle, horizontal ou vertical. Sem estado, sem '
                'tamanho, sem recuo: comprimento e margem sao do layout. <hr> anunciado e o '
                'padrao (opcao A); decorativo e marcacao, nao token. Uma excecao de '
                'contraste declarada em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/divider/tokens.json escrito')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def css_ref(ref):
    """Traduz a referencia da Foundation para a custom property equivalente."""
    if ref.startswith('border.width.'):
        return f'var(--al-border-width-{ref.split(".")[2]})'
    return f'var(--al-{ref})'          # semantico de cor


def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Divider')
    w(' * GERADO por components/divider/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Sem bloco de tema: cada token aponta para um semantico, e o tema troca')
    w(' * no :root - o mesmo elemento onde estes alias sao declarados.')
    w(' */')
    w('')
    w(':root {')
    for role, ref in COLOR.items():
        w(f'  --al-divider-{role}: {css_ref(ref)};')
    for role, ref in GEOM.items():
        w(f'  --al-divider-{role}: {css_ref(ref)};')
    w('}')
    w('')

    texto = '\n'.join(L)
    faltando = [n for n in alias if f'--al-{n}:' not in texto]
    if faltando:
        raise AssertionError(f'tokens fora do CSS: {faltando}')

    path = os.path.join(HERE, 'al-divider-tokens.css')
    open(path, 'w').write(texto)
    print(f'components/divider/al-divider-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
