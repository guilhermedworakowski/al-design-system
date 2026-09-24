"""
QA de acessibilidade do Radio.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - cada
papel de cor contra o fundo EFETIVO, nao par de token solto.

AS COMBINACOES INCLUEM AS QUE SO EXISTEM NO CODIGO

  O Figma tem seis variantes num eixo so. O input nativo produz mais: marcado +
  foco, erro + foco, erro + marcado, marcado + disabled. Elas foram decididas
  na etapa 3 e sao pintadas pelo radio.css - entao sao medidas aqui como
  qualquer outra. O portao nao mede o que o Figma desenhou; mede o que o
  navegador pinta.

O QUE O FUNDO EFETIVO MUDA AQUI

  1. ONDE O RADIO E COLOCADO. Pagina nua (`bg-canvas`), faixa de secao
     (`bg-surface`) ou card/modal (`bg-surface-raised`). Vale a PIOR.

  2. NO RADIO, QUEM DESENHA O LIMITE E SEMPRE A BORDA - A DIFERENCA PARA O
     CHECKBOX. Marcado nao pinta o fundo: a borda laranja fica entre a pagina
     por fora e o anel `bg` por dentro, e e medida contra os dois. O ponto e
     medido contra o anel `bg` que o cerca.

  3. COM FOCO, A VIZINHA EXTERNA E O RESPIRO DO ANEL. O anel desenha 2px de
     `bg-canvas` colado no circulo, independente de onde ele foi colocado.

  4. A COR DO ANEL SAI DO PROPRIO box-shadow - o ultimo hex da sombra
     composta. Sem definicao paralela para divergir do CSS.

DOIS PISOS, DE PROPOSITO

  Texto (rotulo)                    = 4,5:1 do 1.4.3.
  Nao-textual (borda, ponto, anel)  = 3:1 do 1.4.11.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Seis regras, todas das regras de uso (etapa 4):

    a) todo `.al-radio__input` e `<input type="radio">` nativo, dentro de um
       `<label class="al-radio">`, e ninguem escreve `role="radio"` (regras 11
       e 25);
    b) todo radio tem rotulo VISIVEL e nao-vazio em `.al-radio__label`, e nao
       usa `aria-label` (regra 27 - e a regra que paga a borda de 1,57:1);
    c) todo radio tem `name`, e cada `name` junta DUAS opcoes ou mais - radio
       sozinho nao existe (regras 3 e 5);
    d) os radios de um `name` moram no mesmo `<fieldset>`, com `<legend>`
       nao-vazio - e a pergunta, que a aplicacao monta (regra 6);
    e) o erro e da pergunta: `aria-invalid="true"` vai no `<fieldset>`, com
       `aria-describedby` para um id que existe - nunca no radio, onde a ARIA
       nao o preve (regras 21, 22 e 26);
    f) o ponto e decorativo: `aria-hidden="true"`.

ORDEM DE EXECUCAO - mesma do Select e do Checkbox: roda DEPOIS do HTML que
ele mede.

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
RADIO = json.load(open(os.path.join(HERE, 'tokens.json')))

RES = RADIO['resolved']
PENDING = RADIO['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# estado -> como o circulo e pintado.
#   ponto:  token do ponto, ou None se o circulo esta vazio
#   rotulo: token do rotulo
STATES = {
    'default':          dict(border='radio-border',          fill='radio-bg',          ponto=None,                 ring=False, rotulo='radio-label',          exc_limite='borda-abaixo-de-3-1'),
    'hover':            dict(border='radio-border-hover',    fill='radio-bg-hover',    ponto=None,                 ring=False, rotulo='radio-label',          exc_limite=None),
    'focus':            dict(border='radio-border-focus',    fill='radio-bg',          ponto=None,                 ring=True,  rotulo='radio-label',          exc_limite=None),
    'checked':          dict(border='radio-border-checked',  fill='radio-bg',          ponto='radio-dot',          ring=False, rotulo='radio-label',          exc_limite=None),
    'checked-focus':    dict(border='radio-border-checked',  fill='radio-bg',          ponto='radio-dot',          ring=True,  rotulo='radio-label',          exc_limite=None),
    'error':            dict(border='radio-border-error',    fill='radio-bg',          ponto=None,                 ring=False, rotulo='radio-label-error',    exc_limite=None),
    'error-focus':      dict(border='radio-border-error',    fill='radio-bg',          ponto=None,                 ring=True,  rotulo='radio-label-error',    exc_limite=None),
    'error-checked':    dict(border='radio-border-checked',  fill='radio-bg',          ponto='radio-dot',          ring=False, rotulo='radio-label-error',    exc_limite=None),
    'disabled':         dict(border='radio-border-disabled', fill='radio-bg-disabled', ponto=None,                 ring=False, rotulo='radio-label-disabled', exc_limite='disabled-abaixo-de-aa'),
    'disabled-checked': dict(border='radio-border-disabled', fill='radio-bg-disabled', ponto='radio-dot-disabled', ring=False, rotulo='radio-label-disabled', exc_limite='disabled-abaixo-de-aa'),
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
    shadow = RES['radio-ring'][theme]
    hexes = re.findall(r'#[0-9a-fA-F]{6}', shadow)
    if not hexes:
        raise ValueError(f'radio-ring ({theme}): box-shadow sem cor legivel -> {shadow}')
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
            exc_dis = 'disabled-abaixo-de-aa' if state.startswith('disabled') else None

            # 1. o limite do circulo - sempre a borda (cabecalho, item 2)
            fg_hex = tok(cfg['border'], theme)
            ratio, bg_hex = pior(fg_hex, fora + [fill])
            linhas.append(dict(state=state, theme=theme, papel='borda',
                               token=cfg['border'], fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                               floor=NON_TEXT_FLOOR, contra=f'{nota_fora} + fundo do circulo',
                               exc=cfg['exc_limite']))

            # 2. o anel
            if cfg['ring']:
                ink = ring_ink(theme)
                ratio, bg_hex = pior(ink, [sem('bg-canvas', theme)] + paginas)
                linhas.append(dict(state=state, theme=theme, papel='anel de foco',
                                   token='radio-ring', fgHex=ink, bgHex=bg_hex, ratio=ratio,
                                   floor=NON_TEXT_FLOOR, contra='respiro + pagina', exc=None))

            # 3. o ponto, contra o anel de fundo que o cerca
            if cfg['ponto']:
                fg_hex = tok(cfg['ponto'], theme)
                linhas.append(dict(state=state, theme=theme, papel='ponto',
                                   token=cfg['ponto'], fgHex=fg_hex, bgHex=fill,
                                   ratio=cr(fg_hex, fill), floor=NON_TEXT_FLOOR,
                                   contra='fundo do circulo', exc=exc_dis))

            # 4. o rotulo, contra a pagina
            fg_hex = tok(cfg['rotulo'], theme)
            ratio, bg_hex = pior(fg_hex, paginas)
            linhas.append(dict(state=state, theme=theme, papel='rotulo',
                               token=cfg['rotulo'], fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                               floor=TEXT_FLOOR, contra='pagina (pior caso)', exc=exc_dis))

    for l in linhas:
        l['pass'] = l['ratio'] >= l['floor']
        l['soNoCodigo'] = l['state'] in SO_NO_CODIGO
    return linhas


# ------------------------------------------------------- contrato de marcacao
def so_marcacao(html):
    """Tira <style> e <script> antes de procurar marcacao - o radio.css traz a
    ANATOMIA num comentario, e a pagina de QA o inlina. Licao do Select."""
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)
    return html


def texto(fragmento):
    return re.sub(r'<[^>]+>', '', fragmento).strip()


def marcacao(path):
    if not os.path.exists(path):
        return ([f'HTML nao encontrado em {path} - contrato de marcacao NAO medido'], 0)

    html = so_marcacao(open(path, encoding='utf-8').read())
    achados = []

    inputs = re.findall(r'<input\b[^>]*class="[^"]*al-radio__input[^"]*"[^>]*>', html)
    blocos = re.findall(r'<label\b[^>]*class="[^"]*\bal-radio\b[^"]*"[^>]*>(.*?)</label>',
                        html, flags=re.S)
    dentro = sum(len(re.findall(r'al-radio__input', b)) for b in blocos)

    # (a)
    if dentro != len(inputs):
        achados.append(f'(a) {len(inputs) - dentro} input(s) fora de <label class="al-radio">')
    # So dentro de TAG: prosa pode citar role="radio" em <code> para dizer que nao se usa.
    if re.search(r'<[a-zA-Z][^>]*\srole="radio"', html):
        achados.append('(a) role="radio" na pagina - o componente e o input nativo')

    nomes = {}
    for tag in inputs:
        if not re.search(r'\btype="radio"', tag):
            achados.append(f'(a) input sem type="radio": {tag[:70]}')
        if 'aria-label' in tag:
            achados.append(f'(b) input usa aria-label havendo rotulo visivel: {tag[:70]}')
        if 'aria-invalid' in tag:
            achados.append(f'(e) aria-invalid no radio - o erro e da pergunta e vai no fieldset: {tag[:70]}')
        m = re.search(r'\bname="([^"]+)"', tag)
        if not m:
            achados.append(f'(c) radio sem name: {tag[:70]}')
        else:
            nomes[m.group(1)] = nomes.get(m.group(1), 0) + 1

    # (b) rotulo visivel e nao-vazio em cada bloco
    for b in blocos:
        m = re.search(r'<span\b[^>]*al-radio__label[^>]*>(.*?)</span>', b, flags=re.S)
        if not m or not texto(m.group(1)):
            achados.append('(b) radio sem rotulo visivel em .al-radio__label')

    # (c) cada pergunta tem duas opcoes ou mais
    for nome, n in nomes.items():
        if n < 2:
            achados.append(f'(c) name="{nome}" tem um radio so - radio sozinho nao existe')

    # (d) e (e) - por fieldset. Fieldset nao se aninha nas paginas do AL; se
    # aninhar um dia, este recorte passa a mentir e precisa virar parser.
    fieldsets = re.findall(r'(<fieldset\b[^>]*>)(.*?)</fieldset>', html, flags=re.S)
    nome_em = {}
    for abre, corpo in fieldsets:
        dentro_fs = re.findall(r'<input\b[^>]*al-radio__input[^>]*\bname="([^"]+)"', corpo)
        if not dentro_fs:
            continue
        lg = re.search(r'<legend\b[^>]*>(.*?)</legend>', corpo, flags=re.S)
        if not lg or not texto(lg.group(1)):
            achados.append(f'(d) fieldset com radios sem <legend> visivel: {abre[:60]}')
        for nome in dentro_fs:
            nome_em.setdefault(nome, set()).add(abre)
        if 'aria-invalid="true"' in abre:
            m = re.search(r'aria-describedby="([^"]+)"', abre)
            if not m:
                achados.append(f'(e) pergunta em erro sem aria-describedby: {abre[:60]}')
            else:
                for ref in m.group(1).split():
                    if not re.search(rf'\bid="{re.escape(ref)}"', html):
                        achados.append(f'(e) pergunta descreve por "{ref}", que nao existe')
    for nome in nomes:
        onde = nome_em.get(nome)
        if not onde:
            achados.append(f'(d) name="{nome}" fora de <fieldset> - a pergunta nao e anunciada')
        elif len(onde) > 1:
            achados.append(f'(d) name="{nome}" espalhado por {len(onde)} fieldsets')

    # (f)
    for dot in re.findall(r'<span\b[^>]*al-radio__dot[^>]*>', html):
        if 'aria-hidden="true"' not in dot:
            achados.append(f'(f) ponto sem aria-hidden="true": {dot[:60]}')

    return (achados, len(inputs))


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    linhas = medir()

    reprovas = [l for l in linhas if not l['pass'] and not l['exc']]
    excecoes = [l for l in linhas if not l['pass'] and l['exc']]
    passam = [l for l in linhas if l['pass']]

    print('=' * 78)
    print('QA DE ACESSIBILIDADE DO RADIO')
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
    print(f'contrato de marcacao - {os.path.relpath(path, ROOT)}  ({n} radio(s) medido(s)):')
    if achados:
        for a in achados:
            print('   ', a)
    elif n == 0:
        print('    PENDENTE - nenhum radio neste HTML. Nada medido nao e nada errado.')
    else:
        print('    as seis regras passam em todos os radios')
    print('-' * 78)

    json.dump({
        'component': 'radio',
        'criterion': 'WCAG 1.4.3 texto (rotulo) + 1.4.11 nao-textual (borda, ponto, anel)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'pages': list(PAGINAS),
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n,
        'markupPending': n == 0,
        'markupRules': [
            'input type="radio" nativo dentro de <label class="al-radio">, sem role="radio"',
            'rotulo visivel e nao-vazio, sem aria-label',
            'todo radio tem name, e cada name junta duas opcoes ou mais',
            'os radios de um name moram num so <fieldset> com <legend> visivel',
            'erro no fieldset: aria-invalid="true" + aria-describedby que existe; nunca no radio',
            'ponto decorativo: aria-hidden="true"',
        ],
        'fails': len(reprovas),
        'exceptions': {k: len([l for l in excecoes if l['exc'] == k]) for k in PENDING},
        'codeOnlyStates': list(SO_NO_CODIGO),
        'rows': linhas,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'components/radio/a11y.json escrito ({len(linhas)} medicoes)')
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
