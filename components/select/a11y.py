"""
QA de acessibilidade do Select.

Como no Button, Icon Button, Icon, Tag e Avatar, a validacao e por COMBINACAO
RENDERIZADA - cada papel de cor contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI, E QUE A ETAPA 3 NAO PODIA VER

  1. A BORDA TROCA DE VIZINHO QUANDO O CAMPO RECEBE FOCO. Em repouso ela toca a
     pagina, que pode ser `bg-canvas` OU `bg-surface-raised` (campo dentro de
     card ou modal) - o portao mede a pior das duas. Com foco, o anel desenha
     um respiro de 2px em `bg-canvas` colado na borda, entao a vizinha externa
     passa a ser `bg-canvas` SEMPRE, independente de onde o campo foi colocado.
     Isso e ordem de camada, nao par de token: so aparece medindo o renderizado.

  2. A COR DO ANEL SAI DO PROPRIO box-shadow. `select-ring` resolve para a
     sombra composta ("0 0 0 2px #FFF, 0 0 0 4px #FC5000"), e este portao le o
     ULTIMO hex da string - a cor que de fato pinta o anel. Nao ha definicao
     paralela para divergir do CSS.

  3. A BORDA TEM DUAS VIZINHAS. Por fora a pagina (ou o respiro do anel), por
     dentro o preenchimento do campo. Vale a PIOR das duas: borda que some por
     dentro nao desenha limite nenhum.

DOIS PISOS, DE PROPOSITO

  Texto (rotulo, marca, valor, apoio) = 4,5:1 do 1.4.3.
  Nao-textual (borda, seta, anel)     = 3:1 do 1.4.11.
  Cada papel contra o piso que e dele, nunca contra o mais facil.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Num campo de formulario, quase tudo que da errado e marcacao, nao estilo - e
  marcacao so existe na saida renderizada. Cinco regras, todas da etapa 4:

    a) todo `.al-select__field` tem `id`, e existe um `<label for>` apontando
       para ele (regras 5 e 24);
    b) campo com `aria-invalid="true"` tem `aria-describedby`, e o id apontado
       existe de verdade no documento (regra 26);
    c) o placeholder e a primeira <option> com `value=""` e `selected`, nunca
       um atributo inventado (regra 12);
    d) a seta e decorativa: `aria-hidden="true"` e `focusable="false"` na
       propria tag - o sentido mora no rotulo (contrato do icon.css);
    e) nenhum campo usa `aria-label` havendo rotulo visivel, porque o nome
       anunciado tem que bater com o texto que a pessoa le (regra 24);
    f) o `id` do campo e UNICO no documento. Sem isso o `<label for>` liga no
       primeiro elemento com aquele id, que pode nao ser o campo - foi o que
       aconteceu no playground do site ate 0.11.0: o campo chamava `pg-select`,
       o mesmo id do conteiner da pagina, e o rotulo apontava para a pagina.
       As regras (a) a (e) passavam todas; so contar o id pegou.

  Regra escrita numa pagina envelhece; regra medida quebra o build.

ORDEM DE EXECUCAO - este portao roda DEPOIS do site.py

  Mesmo arranjo que o Icon ja usa, e pela mesma razao mecanica: o portao
  precisa do HTML emitido para cobrar marcacao, e o site precisa do `a11y.json`
  que este portao escreve para montar a aba de Acessibilidade. As duas geracoes
  convergem numa passada - nao ha loop. Enquanto o site ainda nao tiver Select,
  o JSON sai com `markupPending: true` e o portao diz isso em voz alta.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede site/index.html
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
SELECT = json.load(open(os.path.join(HERE, 'tokens.json')))

RES = SELECT['resolved']
PENDING = SELECT['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

# Onde o campo pode ser colocado. A borda em repouso tem que se virar contra as
# duas: pagina nua e superficie elevada (card, modal).
PAGINAS = ('bg-canvas', 'bg-surface-raised')

# estado -> papeis. `ring=None` significa que aquele estado nao desenha anel.
STATES = {
    'default':     {'border': 'select-border',          'surface': 'select-bg',          'ring': None,                'erro': False, 'off': False},
    'hover':       {'border': 'select-border-hover',    'surface': 'select-bg',          'ring': None,                'erro': False, 'off': False},
    'active':      {'border': 'select-border-active',   'surface': 'select-bg',          'ring': None,                'erro': False, 'off': False},
    'focus':       {'border': 'select-border-focus',    'surface': 'select-bg',          'ring': 'select-ring',       'erro': False, 'off': False},
    'error':       {'border': 'select-border-error',    'surface': 'select-bg',          'ring': None,                'erro': True,  'off': False},
    'focus-error': {'border': 'select-border-error',    'surface': 'select-bg',          'ring': 'select-ring-error', 'erro': True,  'off': False},
    'disabled':    {'border': 'select-border-disabled', 'surface': 'select-bg-disabled', 'ring': None,                'erro': False, 'off': True},
}


def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def cr(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def tok(name, theme):
    """Hex de um token do Select no tema pedido."""
    return RES[name][theme]


def sem(name, theme):
    return FOUND['color']['semantic'][name][0 if theme == 'light' else 1]


def ring_ink(name, theme):
    """A cor que pinta o anel, lida do PROPRIO box-shadow que o CSS emite -
    o ultimo hex da sombra composta. Sem definicao paralela para divergir."""
    shadow = RES[name][theme]
    hexes = re.findall(r'#[0-9a-fA-F]{6}', shadow)
    if not hexes:
        raise ValueError(f'{name} ({theme}): box-shadow sem cor legivel -> {shadow}')
    return hexes[-1]


def pior(fg, fundos):
    """A pior razao entre um primeiro plano e as superficies que ele toca."""
    medidas = [(cr(fg, bg), bg) for bg in fundos]
    return min(medidas)


def medir():
    linhas = []
    for state, cfg in STATES.items():
        for theme, _ in THEMES:
            surface = tok(cfg['surface'], theme)
            paginas = [sem(p, theme) for p in PAGINAS]

            # 1. a borda. Por fora: o respiro do anel quando ha foco, senao a
            #    pagina (pior caso). Por dentro: o preenchimento do campo.
            if cfg['ring']:
                fora = [sem('bg-canvas', theme)]
                nota_fora = 'respiro do anel (bg-canvas)'
            else:
                fora = paginas
                nota_fora = 'pagina (pior de canvas / surface-raised)'
            fg_hex = tok(cfg['border'], theme)
            ratio, bg_hex = pior(fg_hex, fora + [surface])
            linhas.append(dict(
                state=state, theme=theme, papel='borda', ratio=ratio,
                token=f'select-{cfg["border"].split("select-")[-1]}'
                      if cfg['border'].startswith('select-') else cfg['border'],
                fgHex=fg_hex, bgHex=bg_hex,
                floor=NON_TEXT_FLOOR, contra=f'{nota_fora} + preenchimento',
                exc='borda-abaixo-de-3-1' if cfg['border'] in
                    ('select-border', 'select-border-disabled') else None))

            # 2. o anel, quando existe. Por dentro o proprio respiro em
            #    bg-canvas, por fora a pagina.
            if cfg['ring']:
                ink = ring_ink(cfg['ring'], theme)
                ratio, bg_hex = pior(ink, [sem('bg-canvas', theme)] + paginas)
                linhas.append(dict(
                    state=state, theme=theme, papel='anel de foco', ratio=ratio,
                    token=cfg['ring'], fgHex=ink, bgHex=bg_hex,
                    floor=NON_TEXT_FLOOR, contra='respiro + pagina', exc=None))

            # 3. o que vive DENTRO do campo, contra o preenchimento dele
            if cfg['off']:
                dentro = [('texto', 'select-text-disabled', TEXT_FLOOR, 'disabled-abaixo-de-aa'),
                          ('seta', 'select-icon-disabled', NON_TEXT_FLOOR, 'disabled-abaixo-de-aa')]
            else:
                dentro = [('placeholder', 'select-text-placeholder', TEXT_FLOOR, None),
                          ('valor', 'select-text-value', TEXT_FLOOR, None),
                          ('seta', 'select-icon', NON_TEXT_FLOOR, None)]
            for papel, token_nome, floor, exc in dentro:
                fg_hex = tok(token_nome, theme)
                linhas.append(dict(
                    state=state, theme=theme, papel=papel,
                    token=token_nome, fgHex=fg_hex, bgHex=surface,
                    ratio=cr(fg_hex, surface),
                    floor=floor, contra='preenchimento do campo', exc=exc))

            # 4. o que vive FORA do campo, contra a pagina (pior caso)
            if cfg['off']:
                fora_campo = [('rotulo', 'select-label-disabled', 'disabled-abaixo-de-aa'),
                              ('marca opcional', 'select-label-disabled', 'disabled-abaixo-de-aa')]
            elif cfg['erro']:
                fora_campo = [('rotulo', 'select-label-error', None),
                              ('marca opcional', 'select-optional', None),
                              ('apoio', 'select-help-error', None)]
            else:
                fora_campo = [('rotulo', 'select-label', None),
                              ('marca opcional', 'select-optional', None),
                              ('apoio', 'select-help', None)]
            for papel, token_nome, exc in fora_campo:
                fg_hex = tok(token_nome, theme)
                ratio, bg_hex = pior(fg_hex, paginas)
                linhas.append(dict(
                    state=state, theme=theme, papel=papel,
                    token=token_nome, fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                    floor=TEXT_FLOOR, contra='pagina (pior caso)', exc=exc))

    for l in linhas:
        l['pass'] = l['ratio'] >= l['floor']
    return linhas


# ------------------------------------------------------- contrato de marcacao
def so_marcacao(html):
    """Tira <style> e <script> antes de procurar marcacao.

    Nao e zelo: o select.css traz a ANATOMIA num comentario de cabecalho, com
    um <select> e um <label> de exemplo dentro. A pagina de QA inlina esse CSS,
    entao sem esta limpeza o portao media o exemplo do comentario como se fosse
    um campo de verdade - e ele PASSAVA, porque o exemplo esta correto. Portao
    que aprova lendo comentario tambem reprova lendo comentario.
    """
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)
    return html


def marcacao(path):
    """Le o HTML renderizado e cobra as cinco regras. Devolve (achados, contagem)."""
    if not os.path.exists(path):
        return ([f'HTML nao encontrado em {path} - contrato de marcacao NAO medido'], 0)

    html = so_marcacao(open(path, encoding='utf-8').read())
    achados = []

    campos = re.findall(r'<select\b[^>]*class="[^"]*al-select__field[^"]*"[^>]*>', html)
    ids_label = dict(re.findall(r'<label\b[^>]*for="([^"]+)"[^>]*>(.*?)</label>', html, flags=re.S))

    for tag in campos:
        m_id = re.search(r'\bid="([^"]+)"', tag)
        if not m_id:
            achados.append(f'(a) <select> sem id: {tag[:70]}')
            continue
        sid = m_id.group(1)
        n_id = len(re.findall(rf'\bid="{re.escape(sid)}"', html))
        if n_id > 1:
            achados.append(f'(f) id "{sid}" aparece {n_id} vezes - o <label for> pode ligar em outro elemento')
        if sid not in ids_label:
            achados.append(f'(a) nenhum <label for="{sid}"> aponta para este campo')
        if 'aria-label' in tag and sid in ids_label:
            achados.append(f'(e) campo "{sid}" usa aria-label havendo rotulo visivel')
        if re.search(r'aria-invalid="true"', tag):
            m_desc = re.search(r'aria-describedby="([^"]+)"', tag)
            if not m_desc:
                achados.append(f'(b) campo "{sid}" esta em erro e nao tem aria-describedby')
            else:
                for ref in m_desc.group(1).split():
                    if not re.search(rf'\bid="{re.escape(ref)}"', html):
                        achados.append(f'(b) campo "{sid}" descreve por "{ref}", que nao existe')

    # (c) placeholder: primeira <option> vazia tem que estar selecionada
    for bloco in re.findall(r'<select\b[^>]*al-select__field.*?</select>', html, flags=re.S):
        vazias = re.findall(r'<option\b[^>]*value=""[^>]*>', bloco)
        for op in vazias:
            if 'selected' not in op:
                achados.append(f'(c) <option value=""> sem selected: {op[:60]}')

    # (d) a seta e decorativa
    for svg in re.findall(r'<svg\b[^>]*al-select__chevron[^>]*>', html):
        if 'aria-hidden="true"' not in svg:
            achados.append(f'(d) seta sem aria-hidden="true": {svg[:60]}')
        if 'focusable="false"' not in svg:
            achados.append(f'(d) seta sem focusable="false": {svg[:60]}')

    return (achados, len(campos))


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    linhas = medir()

    reprovas = [l for l in linhas if not l['pass'] and not l['exc']]
    excecoes = [l for l in linhas if not l['pass'] and l['exc']]
    passam = [l for l in linhas if l['pass']]

    print('=' * 78)
    print('QA DE ACESSIBILIDADE DO SELECT')
    print('=' * 78)
    print(f'  combinacoes medidas : {len(linhas)}  (7 estados x 2 temas x papeis visiveis)')
    print(f'  passam              : {len(passam)}')
    print(f'  excecoes declaradas : {len(excecoes)}')
    print(f'  reprovas            : {len(reprovas)}')
    print('-' * 78)

    for state in STATES:
        do_estado = [l for l in linhas if l['state'] == state]
        pior_l = min(do_estado, key=lambda l: l['ratio'] / l['floor'])
        marca = 'EXC' if pior_l['exc'] and not pior_l['pass'] else ('ok' if pior_l['pass'] else 'XX')
        print(f'  {state:<12} pior papel: {pior_l["papel"]:<15} '
              f'{pior_l["ratio"]:>6}:1 / {pior_l["floor"]}  [{pior_l["theme"]}] {marca}')

    print('-' * 78)
    print('efeito da ordem de camada (o que a etapa 3 nao podia ver):')
    for theme, _ in THEMES:
        rep = next(l for l in linhas if l['state'] == 'default' and l['theme'] == theme and l['papel'] == 'borda')
        foc = next(l for l in linhas if l['state'] == 'focus' and l['theme'] == theme and l['papel'] == 'borda')
        print(f'  borda [{theme:<5}] repouso {rep["ratio"]}:1 contra a pagina  ->  '
              f'foco {foc["ratio"]}:1 contra o respiro do anel')
    print('-' * 78)

    if excecoes:
        print(f'excecoes conscientes - {len(excecoes)} medicoes, nenhuma e achado novo:')
        for chave in PENDING:
            n = [l for l in excecoes if l['exc'] == chave]
            if n:
                faixa = f'{min(l["ratio"] for l in n)}:1 a {max(l["ratio"] for l in n)}:1'
                print(f'   {chave}: {len(n)} medicoes, {faixa}')
    print('-' * 78)

    achados, n_campos = marcacao(path)
    print(f'contrato de marcacao - {os.path.relpath(path, ROOT)}  '
          f'({n_campos} campo(s) medido(s)):')
    if achados:
        for a in achados:
            print('   ', a)
    elif n_campos == 0:
        # zero campo nao e zero problema: e nada medido. Dizer "passa" aqui
        # seria a pior mentira que um portao pode contar.
        print('    PENDENTE - nenhum campo neste HTML. Rodar site/site.py e chamar')
        print('    este portao de novo (ver ORDEM DE EXECUCAO no cabecalho).')
    else:
        print('    as seis regras passam em todos os campos')
    print('-' * 78)

    # O site le este arquivo para montar a aba de Acessibilidade.
    json.dump({
        'component': 'select',
        'criterion': 'WCAG 1.4.3 texto (rotulo, marca, valor, apoio) + '
                     '1.4.11 nao-textual (borda, seta, anel)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n_campos,
        'markupPending': n_campos == 0,
        'markupRules': [
            'todo campo tem id e um <label for> apontando para ele',
            'campo em erro tem aria-invalid="true" e aria-describedby que existe',
            'o placeholder e a primeira <option value=""> selecionada',
            'a seta e decorativa: aria-hidden="true" e focusable="false"',
            'nenhum campo usa aria-label havendo rotulo visivel',
            'o id do campo e unico no documento',
        ],
        'fails': len(reprovas),
        'exceptions': {k: len([l for l in excecoes if l['exc'] == k]) for k in PENDING},
        'layerEffect': [
            {'theme': theme,
             'rest': next(l['ratio'] for l in linhas if l['state'] == 'default'
                          and l['theme'] == theme and l['papel'] == 'borda'),
             'focused': next(l['ratio'] for l in linhas if l['state'] == 'focus'
                             and l['theme'] == theme and l['papel'] == 'borda')}
            for theme, _ in THEMES],
        'rows': linhas,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'components/select/a11y.json escrito ({len(linhas)} medicoes)')
    print('-' * 78)

    if reprovas:
        print(f'{len(reprovas)} COMBINACAO(OES) REPROVAM:')
        for l in reprovas:
            print(f'   {l["state"]}/{l["theme"]} {l["papel"]}: {l["ratio"]}:1 < {l["floor"]} '
                  f'(contra {l["contra"]})')
        return 1
    if achados:
        if n_campos == 0:
            print('contrato de marcacao PENDENTE - o site ainda nao emite Select.')
            print('Rodar site/site.py e chamar este portao de novo (ver ORDEM no cabecalho).')
            return 0
        print(f'{len(achados)} QUEBRA(S) DE CONTRATO DE MARCACAO - PORTAO REPROVA.')
        return 1

    if n_campos == 0:
        print('contraste renderizado: em ordem. Marcacao: PENDENTE, nada medido ainda.')
        return 0
    print('contraste renderizado e contrato de marcacao: tudo em ordem.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
