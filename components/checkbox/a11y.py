"""
QA de acessibilidade do Checkbox.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - cada
papel de cor contra o fundo EFETIVO, nao par de token solto.

AS COMBINACOES INCLUEM AS QUE SO EXISTEM NO CODIGO

  O Figma tem sete variantes num eixo so. O input nativo produz mais: marcado +
  foco, erro + marcado, marcado + disabled. Elas foram decididas na etapa 3 e
  sao pintadas pelo checkbox.css - entao sao medidas aqui como qualquer outra.
  O portao nao mede o que o Figma desenhou; mede o que o navegador pinta.

O QUE O FUNDO EFETIVO MUDA AQUI

  1. ONDE O CHECKBOX E COLOCADO. Pagina nua (`bg-canvas`), faixa de secao
     (`bg-surface`) ou card/modal (`bg-surface-raised`). O Checkbox vive em
     listas de configuracao, que costumam morar em `bg-surface` - por isso ele
     entra aqui, alem das duas paginas que o Select mede. Vale a PIOR.

  2. QUEM DESENHA O LIMITE MUDA COM O ESTADO. Desmarcada, e a borda - contra a
     pagina por fora e o preenchimento por dentro. Marcada, borda e
     preenchimento sao a mesma cor, entao o limite e o PREENCHIMENTO inteiro
     contra a pagina. Medir a borda da caixa marcada contra o proprio fundo
     daria 1:1 e reprovaria uma caixa perfeitamente visivel.

  3. COM FOCO, A VIZINHA EXTERNA E O RESPIRO DO ANEL. O anel desenha 2px de
     `bg-canvas` colado na caixa, independente de onde ela foi colocada.

  4. A COR DO ANEL SAI DO PROPRIO box-shadow - o ultimo hex da sombra
     composta. Sem definicao paralela para divergir do CSS.

DOIS PISOS, DE PROPOSITO

  Texto (rotulo)                         = 4,5:1 do 1.4.3.
  Nao-textual (borda, caixa, glifo, anel) = 3:1 do 1.4.11.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Cinco regras, todas das regras de uso (etapa 4):

    a) todo `.al-checkbox__input` e `<input type="checkbox">` nativo, dentro de
       um `<label class="al-checkbox">` (regras 9 e 21);
    b) todo checkbox tem rotulo VISIVEL e nao-vazio em `.al-checkbox__label`, e
       nao usa `aria-label` (regra 23 - e a regra que paga a borda de 1,57:1);
    c) checkbox com `aria-invalid="true"` tem `aria-describedby`, e o id
       apontado existe no documento (regras 19 e 22 - o erro em texto e do
       formulario, mas tem que existir);
    d) os glifos sao decorativos: `aria-hidden="true"` e `focusable="false"`;
    e) ninguem escreve `indeterminate` como atributo HTML: ele nao existe, e o
       navegador o ignora em silencio. Indeterminado so por JS (regra 8).

ORDEM DE EXECUCAO - mesma do Select: roda DEPOIS do HTML que ele mede.

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
CHECKBOX = json.load(open(os.path.join(HERE, 'tokens.json')))

RES = CHECKBOX['resolved']
PENDING = CHECKBOX['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# estado -> como a caixa e pintada.
#   marcada: o limite e o preenchimento, nao a borda (ver cabecalho, item 2)
#   glifo:   token do check/traco, ou None se a caixa esta vazia
#   rotulo:  token do rotulo
STATES = {
    'default':           dict(border='checkbox-border',          fill='checkbox-bg',          marcada=False, glifo=None,                     ring=False, rotulo='checkbox-label',          exc_limite='borda-abaixo-de-3-1'),
    'hover':             dict(border='checkbox-border-hover',    fill='checkbox-bg-hover',    marcada=False, glifo=None,                     ring=False, rotulo='checkbox-label',          exc_limite=None),
    'focus':             dict(border='checkbox-border-focus',    fill='checkbox-bg',          marcada=False, glifo=None,                     ring=True,  rotulo='checkbox-label',          exc_limite=None),
    'checked':           dict(border='checkbox-border-checked',  fill='checkbox-bg-checked',  marcada=True,  glifo='checkbox-icon',          ring=False, rotulo='checkbox-label',          exc_limite=None),
    'checked-focus':     dict(border='checkbox-border-checked',  fill='checkbox-bg-checked',  marcada=True,  glifo='checkbox-icon',          ring=True,  rotulo='checkbox-label',          exc_limite=None),
    'indeterminate':     dict(border='checkbox-border-checked',  fill='checkbox-bg-checked',  marcada=True,  glifo='checkbox-icon',          ring=False, rotulo='checkbox-label',          exc_limite=None),
    'error':             dict(border='checkbox-border-error',    fill='checkbox-bg',          marcada=False, glifo=None,                     ring=False, rotulo='checkbox-label-error',    exc_limite=None),
    'error-focus':       dict(border='checkbox-border-error',    fill='checkbox-bg',          marcada=False, glifo=None,                     ring=True,  rotulo='checkbox-label-error',    exc_limite=None),
    'error-checked':     dict(border='checkbox-border-checked',  fill='checkbox-bg-checked',  marcada=True,  glifo='checkbox-icon',          ring=False, rotulo='checkbox-label-error',    exc_limite=None),
    'disabled':          dict(border='checkbox-border-disabled', fill='checkbox-bg-disabled', marcada=False, glifo=None,                     ring=False, rotulo='checkbox-label-disabled', exc_limite='disabled-abaixo-de-aa'),
    'disabled-checked':  dict(border='checkbox-border-disabled', fill='checkbox-bg-disabled', marcada=False, glifo='checkbox-icon-disabled', ring=False, rotulo='checkbox-label-disabled', exc_limite='disabled-abaixo-de-aa'),
}

# estados sem variante no Figma - pintados so pelo codigo (etapa 3)
SO_NO_CODIGO = ('checked-focus', 'error-focus', 'error-checked', 'disabled-checked')


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
    return RES[name][theme]


def sem(name, theme):
    return FOUND['color']['semantic'][name][0 if theme == 'light' else 1]


def ring_ink(theme):
    """A cor que pinta o anel, lida do PROPRIO box-shadow - o ultimo hex."""
    shadow = RES['checkbox-ring'][theme]
    hexes = re.findall(r'#[0-9a-fA-F]{6}', shadow)
    if not hexes:
        raise ValueError(f'checkbox-ring ({theme}): box-shadow sem cor legivel -> {shadow}')
    return hexes[-1]


def pior(fg, fundos):
    return min((cr(fg, bg), bg) for bg in fundos)


def medir():
    linhas = []
    for state, cfg in STATES.items():
        for theme, _ in THEMES:
            paginas = [sem(p, theme) for p in PAGINAS]
            fill = tok(cfg['fill'], theme)
            fora = [sem('bg-canvas', theme)] if cfg['ring'] else paginas
            nota_fora = 'respiro do anel (bg-canvas)' if cfg['ring'] else 'pagina (pior caso)'

            # 1. o limite da caixa
            if cfg['marcada']:
                ratio, bg_hex = pior(fill, fora)
                linhas.append(dict(state=state, theme=theme, papel='caixa marcada',
                                   token=cfg['fill'], fgHex=fill, bgHex=bg_hex, ratio=ratio,
                                   floor=NON_TEXT_FLOOR, contra=nota_fora, exc=None))
            else:
                fg_hex = tok(cfg['border'], theme)
                ratio, bg_hex = pior(fg_hex, fora + [fill])
                linhas.append(dict(state=state, theme=theme, papel='borda',
                                   token=cfg['border'], fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                                   floor=NON_TEXT_FLOOR, contra=f'{nota_fora} + preenchimento',
                                   exc=cfg['exc_limite']))

            # 2. o anel
            if cfg['ring']:
                ink = ring_ink(theme)
                ratio, bg_hex = pior(ink, [sem('bg-canvas', theme)] + paginas)
                linhas.append(dict(state=state, theme=theme, papel='anel de foco',
                                   token='checkbox-ring', fgHex=ink, bgHex=bg_hex, ratio=ratio,
                                   floor=NON_TEXT_FLOOR, contra='respiro + pagina', exc=None))

            # 3. o glifo, contra o preenchimento da caixa
            if cfg['glifo']:
                fg_hex = tok(cfg['glifo'], theme)
                exc = 'disabled-abaixo-de-aa' if state.startswith('disabled') else None
                linhas.append(dict(state=state, theme=theme,
                                   papel='traco' if state == 'indeterminate' else 'check',
                                   token=cfg['glifo'], fgHex=fg_hex, bgHex=fill,
                                   ratio=cr(fg_hex, fill), floor=NON_TEXT_FLOOR,
                                   contra='preenchimento da caixa', exc=exc))

            # 4. o rotulo, contra a pagina
            fg_hex = tok(cfg['rotulo'], theme)
            ratio, bg_hex = pior(fg_hex, paginas)
            exc = 'disabled-abaixo-de-aa' if state.startswith('disabled') else None
            linhas.append(dict(state=state, theme=theme, papel='rotulo',
                               token=cfg['rotulo'], fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                               floor=TEXT_FLOOR, contra='pagina (pior caso)', exc=exc))

    for l in linhas:
        l['pass'] = l['ratio'] >= l['floor']
        l['soNoCodigo'] = l['state'] in SO_NO_CODIGO
    return linhas


# ------------------------------------------------------- contrato de marcacao
def so_marcacao(html):
    """Tira <style> e <script> antes de procurar marcacao - o checkbox.css traz
    a ANATOMIA num comentario, e a pagina de QA o inlina. Licao do Select."""
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)
    return html


def marcacao(path):
    if not os.path.exists(path):
        return ([f'HTML nao encontrado em {path} - contrato de marcacao NAO medido'], 0)

    html = so_marcacao(open(path, encoding='utf-8').read())
    achados = []

    inputs = re.findall(r'<input\b[^>]*class="[^"]*al-checkbox__input[^"]*"[^>]*>', html)
    blocos = re.findall(r'<label\b[^>]*class="[^"]*\bal-checkbox\b[^"]*"[^>]*>(.*?)</label>',
                        html, flags=re.S)
    dentro = sum(len(re.findall(r'al-checkbox__input', b)) for b in blocos)

    # (a)
    if dentro != len(inputs):
        achados.append(f'(a) {len(inputs) - dentro} input(s) fora de <label class="al-checkbox">')
    for tag in inputs:
        if not re.search(r'\btype="checkbox"', tag):
            achados.append(f'(a) input sem type="checkbox": {tag[:70]}')
        if 'aria-label' in tag:
            achados.append(f'(b) input usa aria-label havendo rotulo visivel: {tag[:70]}')
        if re.search(r'\sindeterminate(\s|=|>|/)', tag):
            achados.append(f'(e) atributo indeterminate na marcacao - nao existe, usar JS: {tag[:70]}')
        if 'aria-invalid="true"' in tag:
            m = re.search(r'aria-describedby="([^"]+)"', tag)
            if not m:
                achados.append(f'(c) checkbox em erro sem aria-describedby: {tag[:70]}')
            else:
                for ref in m.group(1).split():
                    if not re.search(rf'\bid="{re.escape(ref)}"', html):
                        achados.append(f'(c) checkbox descreve por "{ref}", que nao existe')
    if re.search(r'role="checkbox"', html):
        achados.append('(a) role="checkbox" na pagina - o componente e o input nativo')

    # (b) rotulo visivel e nao-vazio em cada bloco
    for b in blocos:
        m = re.search(r'<span\b[^>]*al-checkbox__label[^>]*>(.*?)</span>', b, flags=re.S)
        if not m or not re.sub(r'<[^>]+>', '', m.group(1)).strip():
            achados.append('(b) checkbox sem rotulo visivel em .al-checkbox__label')

    # (d)
    for svg in re.findall(r'<svg\b[^>]*al-checkbox__(?:check|dash)[^>]*>', html):
        if 'aria-hidden="true"' not in svg:
            achados.append(f'(d) glifo sem aria-hidden="true": {svg[:60]}')
        if 'focusable="false"' not in svg:
            achados.append(f'(d) glifo sem focusable="false": {svg[:60]}')

    return (achados, len(inputs))


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    linhas = medir()

    reprovas = [l for l in linhas if not l['pass'] and not l['exc']]
    excecoes = [l for l in linhas if not l['pass'] and l['exc']]
    passam = [l for l in linhas if l['pass']]

    print('=' * 78)
    print('QA DE ACESSIBILIDADE DO CHECKBOX')
    print('=' * 78)
    print(f'  combinacoes medidas : {len(linhas)}  ({len(STATES)} estados x 2 temas x papeis visiveis;'
          f' {len(SO_NO_CODIGO)} estados so existem no codigo)')
    print(f'  passam              : {len(passam)}')
    print(f'  excecoes declaradas : {len(excecoes)}')
    print(f'  reprovas            : {len(reprovas)}')
    print('-' * 78)
    for state in STATES:
        do_estado = [l for l in linhas if l['state'] == state]
        p = min(do_estado, key=lambda l: l['ratio'] / l['floor'])
        marca = 'EXC' if p['exc'] and not p['pass'] else ('ok' if p['pass'] else 'XX')
        cod = ' (so no codigo)' if state in SO_NO_CODIGO else ''
        print(f'  {state:<17} pior: {p["papel"]:<14} {p["ratio"]:>6}:1 / {p["floor"]}'
              f'  [{p["theme"]}] {marca}{cod}')
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
                print(f'   {chave}: {len(n)} medicoes, '
                      f'{min(l["ratio"] for l in n)}:1 a {max(l["ratio"] for l in n)}:1')
    print('-' * 78)

    achados, n = marcacao(path)
    print(f'contrato de marcacao - {os.path.relpath(path, ROOT)}  ({n} checkbox(es) medido(s)):')
    if achados:
        for a in achados:
            print('   ', a)
    elif n == 0:
        print('    PENDENTE - nenhum checkbox neste HTML. Nada medido nao e nada errado.')
    else:
        print('    as cinco regras passam em todos os checkboxes')
    print('-' * 78)

    json.dump({
        'component': 'checkbox',
        'criterion': 'WCAG 1.4.3 texto (rotulo) + 1.4.11 nao-textual (borda, caixa, glifo, anel)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'pages': list(PAGINAS),
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n,
        'markupPending': n == 0,
        'markupRules': [
            'input type="checkbox" nativo dentro de <label class="al-checkbox">',
            'rotulo visivel e nao-vazio, sem aria-label',
            'em erro: aria-invalid="true" + aria-describedby que existe',
            'glifos decorativos: aria-hidden="true" e focusable="false"',
            'indeterminate nunca como atributo HTML - so por JS',
        ],
        'fails': len(reprovas),
        'exceptions': {k: len([l for l in excecoes if l['exc'] == k]) for k in PENDING},
        'codeOnlyStates': list(SO_NO_CODIGO),
        'rows': linhas,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'components/checkbox/a11y.json escrito ({len(linhas)} medicoes)')
    print('-' * 78)

    if reprovas:
        print(f'{len(reprovas)} COMBINACAO(OES) REPROVAM:')
        for l in reprovas:
            print(f'   {l["state"]}/{l["theme"]} {l["papel"]}: {l["ratio"]}:1 < {l["floor"]} '
                  f'(contra {l["contra"]})')
        return 1
    if achados and n > 0:
        print(f'{len(achados)} QUEBRA(S) DE CONTRATO DE MARCACAO - PORTAO REPROVA.')
        return 1
    if n == 0:
        print('contraste renderizado: em ordem. Marcacao: PENDENTE, nada medido ainda.')
        return 0
    print('contraste renderizado e contrato de marcacao: tudo em ordem.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
