"""
Camada de tokens do Tag.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> tag-filled-success-bg       (hifen)
  Figma  -> tag/filled/success/bg       (pasta)
Sao camadas diferentes. Nunca colapsar uma na outra.

POR QUE O TIPO VEM ANTES DO STATUS

  O Tag tem duas dimensoes de variante, e elas nao sao simetricas. `Type`
  (filled/outlined) decide QUAIS PAPEIS EXISTEM: o filled tem preenchimento e
  borda transparente; o outlined tem fundo transparente e borda colorida.
  `Status` so troca QUAL COR entra em cada papel.

  Por isso o tipo ocupa o mesmo lugar que `primary`/`secondary`/`ghost`/
  `danger` ocupam no Button - e o status desce um nivel.

O ROTULO DO OUTLINED NAO E `text-on-solid`

  Parece detalhe e nao e. Sem preenchimento, o rotulo do outlined nao esta
  sobre um solido - esta sobre a tela. `text-on-solid` vale #FFFFFF no tema
  claro e #181818 no escuro, que sao exatamente os dois `bg-canvas`: usa-lo
  ali da contraste 1.00 nos dois temas, texto invisivel. O outlined usa a
  tinta de STATUS (`text-success`, `text-danger`, ...), medida contra a tela.

  Foi o achado 6 da auditoria. Fica escrito aqui para nao voltar.

ZERO EXCECAO DE CONTRASTE

  O Button tem tres excecoes de marca porque o laranja da marca nao alcanca
  4.5:1 com branco em cima. O Tag nao tem nenhuma - o status Brand ficou
  deliberadamente fora desta versao, e sem ele nenhum par desce do piso.
  E o primeiro componente do AL a fechar em zero excecoes CARREGANDO TEXTO
  (o Icon Button fecha em zero, mas contra o piso de 3:1 do 1.4.11).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'foundation'))

from build import SEM                     # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))   # noqa: E402

TRANSPARENT = 'transparent'   # ausencia de cor, nao uma escolha de cor

# ---------------------------------------------------------------- cor
# Duas dimensoes: tipo -> status -> papel.
#
# A borda do filled existe e e transparente. Nao e enfeite: e ela que faz o
# filled ocupar a MESMA CAIXA do outlined. Sem ela, a borda de 1px do outlined
# cresceria a caixa em 2px nos dois eixos e uma linha de filtros misturando os
# dois tipos desalinharia. Mesmo mecanismo do Button.
COLOR = {
  'filled': {
    'success': {'bg': 'bg-success', 'label': 'text-on-solid', 'border': TRANSPARENT},
    'warning': {'bg': 'bg-warning', 'label': 'text-on-solid', 'border': TRANSPARENT},
    'error':   {'bg': 'bg-danger',  'label': 'text-on-solid', 'border': TRANSPARENT},
    'info':    {'bg': 'bg-info',    'label': 'text-on-solid', 'border': TRANSPARENT},
    # O cinza claro do neutral pede tinta escura, nao a de solido.
    'neutral': {'bg': 'bg-active',  'label': 'text-primary',  'border': TRANSPARENT},
  },
  'outlined': {
    'success': {'label': 'text-success', 'border': 'border-success'},
    'warning': {'label': 'text-warning', 'border': 'border-warning'},
    'error':   {'label': 'text-danger',  'border': 'border-danger'},
    'info':    {'label': 'text-info',    'border': 'border-info'},
    # Nao existe `border-neutral`; border-strong e o cinza de contorno do sistema.
    'neutral': {'label': 'text-primary', 'border': 'border-strong'},
  },
}

# UM token, nao cinco. O fundo do outlined nao varia por status - cinco tokens
# com o mesmo valor seriam cinco lugares para errar a mesma coisa.
TYPE_SHARED = {
  'outlined': {'bg': TRANSPARENT},
}

# ------------------------------------------------------------- dismiss
# O X e focavel: quando a propriedade booleana `Icon` liga, a tag deixa de ser
# read-only e entra na ordem de tabulacao. Anel de foco e o mesmo do Button e
# do Icon Button - aponta para a sombra composta da Foundation, nao para a cor
# crua, que e o que mantem cor-de-estado dentro do portao de contraste.
#
# NAO ha token de tinta do X: ele herda a cor do rotulo via currentColor, que
# ja varia por tipo e status. Dez tokens para reproduzir dez valores que o CSS
# herda sozinho seriam ruido. Mesma decisao do spinner do Icon Button.
#
# NAO ha token de hover: por decisao do Gui o X nao tem fundo de hover, so
# muda o cursor. `cursor` e palavra-chave, nao valor de escala.
DISMISS = {
  'ring': 'focusRing.default',
}

# ------------------------------------------------------------ geometria
# padding-x e padding-y separados, ao contrario do Icon Button: o Tag e
# retangular, como o Button.
#
# O gap e space.8 nos dois tamanhos - o mesmo do Button, que e o que faz um Tag
# dismissivel e um Button conviverem sem ritmo interno diferente.
SIZE = {
  'sm': {'padding-x': 'space.8',  'padding-y': 'space.2',
         'gap': 'space.8', 'font': 'type.styles.label-sm', 'icon-size': 'iconSize.16'},
  'md': {'padding-x': 'space.12', 'padding-y': 'space.4',
         'gap': 'space.8', 'font': 'type.styles.label-md', 'icon-size': 'iconSize.20'},
}

SHARED = {
  'radius':       'radius.full',
  'border-width': 'border.width.1',
}

# Registrado, nao esquecido: o alvo do X e menor que os 24px do WCAG 2.5.8.
# Mesma familia de tradeoff do sm do Button (36 contra os 44 do Carbon), e a
# saida e a mesma - regra de uso, nao geometria. A etapa 4 fecha essa regra.
PENDING = {
  'alvo-do-x': ('16px no sm e 20px no md, abaixo dos 24px do WCAG 2.5.8. '
                'Decisao consciente: sem expansao por pseudo-elemento. A regra de uso '
                'reserva o sm dismissivel para interface de ponteiro.'),
}


# ---------------------------------------------------------------- portao
def resolve_foundation(path):
    """Segue um caminho pontuado dentro de tokens.json. Levanta se nao existir."""
    node = FOUND
    for part in path.split('.'):
        if isinstance(node, list):
            match = next((s for s in node if s and s[0] == part), None)
            if match is None:
                raise KeyError(path)
            node = match
            continue
        if not isinstance(node, dict) or part not in node:
            raise KeyError(path)
        node = node[part]
    return node


def bind_color(name, ref, alias, resolved, problems):
    """Um token de cor: registra o alias e resolve nos dois temas, ou reprova."""
    alias[name] = ref
    if ref == TRANSPARENT:
        resolved[name] = {'light': TRANSPARENT, 'dark': TRANSPARENT}
        return
    if ref.startswith('#'):
        problems.append(f'{name}: hex solto ({ref}) - todo valor de cor nasce alias do semantico')
        return
    if ref not in SEM:
        problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
        return
    light, dark = SEM[ref]
    resolved[name] = {'light': light, 'dark': dark}


def contrast_rows():
    """As combinacoes renderizadas do componente, medidas com o motor da
    Foundation. Filled mede o rotulo contra o proprio preenchimento; outlined
    mede o rotulo e a borda contra a tela E contra a superficie, porque sem
    preenchimento e o fundo da pagina que entra por baixo."""
    rows = []
    for status, roles in COLOR['filled'].items():
        for theme, i in (('light', 0), ('dark', 1)):
            rows.append({
                'theme': theme, 'type': 'filled', 'status': status, 'what': 'rotulo',
                'fg': roles['label'], 'bg': roles['bg'],
                'ratio': round(cr(SEM[roles['label']][i], SEM[roles['bg']][i]), 2),
                'min': 4.5,
            })
    for status, roles in COLOR['outlined'].items():
        for under in ('bg-canvas', 'bg-surface'):
            for theme, i in (('light', 0), ('dark', 1)):
                rows.append({
                    'theme': theme, 'type': 'outlined', 'status': status, 'what': f'rotulo sobre {under}',
                    'fg': roles['label'], 'bg': under,
                    'ratio': round(cr(SEM[roles['label']][i], SEM[under][i]), 2),
                    'min': 4.5,
                })
                rows.append({
                    'theme': theme, 'type': 'outlined', 'status': status, 'what': f'borda sobre {under}',
                    'fg': roles['border'], 'bg': under,
                    'ratio': round(cr(SEM[roles['border']][i], SEM[under][i]), 2),
                    'min': 3.0,
                })
    for r in rows:
        r['pass'] = r['ratio'] >= r['min']
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for tipo, statuses in COLOR.items():
        for status, roles in statuses.items():
            for role, ref in roles.items():
                bind_color(f'tag-{tipo}-{status}-{role}', ref, alias, resolved, problems)

    for tipo, roles in TYPE_SHARED.items():
        for role, ref in roles.items():
            bind_color(f'tag-{tipo}-{role}', ref, alias, resolved, problems)

    for role, ref in DISMISS.items():
        name = f'tag-dismiss-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for size, roles in SIZE.items():
        for role, ref in roles.items():
            name = f'tag-{size}-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    for role, ref in SHARED.items():
        name = f'tag-{role}'
        alias[name] = ref
        try:
            resolved[name] = resolve_foundation(ref)
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    # Altura derivada - NAO vira token. A borda e absorvida pelo padding
    # (padding: calc(pad - border-width)), entao ela nao entra na conta e os
    # dois tipos fecham no mesmo numero.
    heights = {}
    for size in SIZE:
        pad_y = resolve_foundation(SIZE[size]['padding-y'])
        leading = resolve_foundation(SIZE[size]['font'])[2]
        heights[size] = pad_y * 2 + leading

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO TAG')
    print('=' * 74)
    for name in sorted(alias):
        ref = alias[name]
        tag = 'transparente' if ref == TRANSPARENT else f'-> {ref}'
        print(f'  {name:<32} {tag}')
    print('-' * 74)
    for size in SIZE:
        print(f'altura derivada {size}: {heights[size]}px  (padding-y x2 + entrelinha; '
              f'a borda e absorvida pelo padding)')
    print('filled e outlined ocupam a mesma caixa: a borda de 1px do outlined '
          'nao cresce a tag')

    print('-' * 74)
    print(f'contraste: {len(rows)} medicoes  |  passam: {len(rows) - len(fails)}  |  '
          f'reprovam: {len(fails)}  |  excecoes: 0')
    pior = min(rows, key=lambda r: r['ratio'] / r['min'])
    print(f'pior margem: {pior["type"]} {pior["status"]} {pior["what"]} ({pior["theme"]}) '
          f'= {pior["ratio"]}:1 contra piso {pior["min"]}')

    for k, v in PENDING.items():
        print(f'pendente: {k} - {v}')
    print('-' * 74)

    if problems:
        print(f'{len(problems)} TOKEN(S) REPROVAM O PORTAO DE ALIAS:')
        for p in problems:
            print('   ', p)
        return 1
    if fails:
        print(f'{len(fails)} COMBINACAO(OES) REPROVAM O PORTAO DE CONTRASTE:')
        for f in fails:
            print(f'    {f["type"]} {f["status"]} {f["what"]} ({f["theme"]}): '
                  f'{f["ratio"]}:1 < {f["min"]}')
        return 1

    n_alias = sum(1 for r in alias.values() if r != TRANSPARENT)
    n_tr = len(alias) - n_alias
    print(f'{len(alias)} tokens: {n_alias} alias da Foundation, {n_tr} transparentes.')
    print('0 valores soltos.')

    out = {
        'meta': {
            'component': 'Tag',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '160:484',
            'types': list(COLOR),
            'statuses': list(COLOR['filled']),
            'sizes': list(SIZE),
            'states': ['default'],
            'nota': (
                'Tag read-only por padrao: fora da ordem de tabulacao, sem foco, sem '
                'hover. A propriedade booleana `dismissible` liga um X focavel - so ele '
                'entra na ordem de tabulacao, e so ele tem anel. O X nao gera token de '
                'tinta: herda o rotulo por currentColor. Zero excecao de contraste; o '
                'status Brand ficou fora desta versao por decisao.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': {'height': heights},
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/tag/tokens.json escrito')
    write_css(alias, heights)
    return 0


# ---------------------------------------------------------------- css
def css_ref(ref):
    """Traduz a referencia da Foundation para a custom property equivalente."""
    if ref == TRANSPARENT:
        return 'transparent'
    if ref.startswith('focusRing.'):
        return f'var(--al-focus-ring-{ref.split(".")[1]})'
    if ref.startswith('space.'):
        return f'var(--al-space-{ref.split(".")[1]})'
    if ref.startswith('radius.'):
        return f'var(--al-radius-{ref.split(".")[1]})'
    if ref.startswith('border.width.'):
        return f'var(--al-border-width-{ref.split(".")[2]})'
    if ref.startswith('iconSize.'):
        return f'var(--al-icon-size-{ref.split(".")[1]})'
    if ref.startswith('type.styles.'):
        return ref.split('.')[2]          # tratado a parte: um estilo vira tres vars
    return f'var(--al-{ref})'             # semantico de cor


def write_css(alias, heights):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Tag')
    w(' * GERADO por components/tag/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui, e isso e o ponto: cada token aponta para um')
    w(' * semantico, e o tema troca no :root - o mesmo elemento onde estes alias')
    w(' * sao declarados. Entao o :root re-substitui todos eles de uma vez.')
    w(' *')
    w(' * O tipo vem antes do status no nome porque e o tipo que decide quais')
    w(' * papeis existem; o status so troca a cor de cada papel.')
    w(' */')
    w('')
    w(':root {')

    for tipo, statuses in COLOR.items():
        w('')
        w(f'  /* {tipo} */')
        for role, ref in TYPE_SHARED.get(tipo, {}).items():
            w(f'  --al-tag-{tipo}-{role}: {css_ref(ref)};')
        for status, roles in statuses.items():
            for role, ref in roles.items():
                w(f'  --al-tag-{tipo}-{status}-{role}: {css_ref(ref)};')

    w('')
    w('  /* dismiss - so o X e focavel; a tag em si nunca recebe foco */')
    for role, ref in DISMISS.items():
        w(f'  --al-tag-dismiss-{role}: {css_ref(ref)};')

    for size, roles in SIZE.items():
        w('')
        w(f'  /* tamanho {size} - altura resultante: {heights[size]}px */')
        for role, ref in roles.items():
            if ref.startswith('type.styles.'):
                style = resolve_foundation(ref)
                w(f'  --al-tag-{size}-font-size: var(--al-font-size-'
                  f'{"xs" if style[1] == 12 else "sm"});')
                w(f'  --al-tag-{size}-line-height: var(--al-line-height-'
                  f'{"xs" if style[2] == 16 else "sm"});')
                w(f'  --al-tag-{size}-font-weight: var(--al-font-weight-medium);')
                w(f'  --al-tag-{size}-tracking: {style[4]};')
                continue
            w(f'  --al-tag-{size}-{role}: {css_ref(ref)};')

    w('')
    w('  /* compartilhado */')
    for role, ref in SHARED.items():
        w(f'  --al-tag-{role}: {css_ref(ref)};')
    w('}')
    w('')

    path = os.path.join(HERE, 'al-tag-tokens.css')
    open(path, 'w').write('\n'.join(L))
    print(f'components/tag/al-tag-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
