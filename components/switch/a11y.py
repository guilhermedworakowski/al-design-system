"""
QA de acessibilidade do Switch.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - cada
papel de cor contra o fundo EFETIVO, nao par de token solto.

AS COMBINACOES INCLUEM AS QUE SO EXISTEM NO CODIGO

  O Figma tem cinco variantes num eixo so. O input nativo produz mais: ligado +
  foco e ligado + disabled. Foram decididas na etapa 3 e sao pintadas pelo
  switch.css - entao sao medidas aqui como qualquer outra. Ligado + hover nao
  entra: e identico ao ligado (o force vence o hover, regra 14).

O QUE O FUNDO EFETIVO MUDA AQUI

  1. ONDE O SWITCH E COLOCADO. Pagina nua (`bg-canvas`), faixa de secao
     (`bg-surface`) ou card/modal (`bg-surface-raised`). Vale a PIOR.

  2. A BORDA TEM DUAS VIZINHAS: a pagina por fora e o trilho por dentro.
     Detalhe que a etapa 3 nao podia ver: o trilho desligado e `bg-surface` -
     numa faixa de secao, trilho e pagina sao a MESMA cor, e quem desenha o
     controle e so a borda e a bolinha. Por isso a regra do rotulo visivel.

  3. A BOLINHA MEDE CONTRA O TRILHO EM QUE ESTA, nunca contra a pagina.

  4. COM FOCO, A VIZINHA EXTERNA E O RESPIRO DO ANEL (2px de `bg-canvas`), e a
     cor do anel sai do PROPRIO box-shadow - o ultimo hex da sombra composta.

DOIS PISOS, DE PROPOSITO

  Texto (rotulo)                              = 4,5:1 do 1.4.3.
  Nao-textual (borda, trilho, bolinha, anel)  = 3:1 do 1.4.11.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Cinco regras, todas das regras de uso (etapa 4):

    a) todo `.al-switch__input` e `<input type="checkbox" role="switch">`
       nativo, dentro de um `<label class="al-switch">`; nenhum outro elemento
       leva `role="switch"` e ninguem usa `aria-pressed` (regra 22);
    b) todo switch tem rotulo VISIVEL e nao-vazio em `.al-switch__label`, e o
       input nao usa `aria-label` nem `aria-labelledby` (regra 23 - e a regra
       que paga a borda de 1,47:1 e a bolinha de 1,96:1);
    c) nada de `aria-checked` no input: o estado vem de `checked`, e um
       atributo paralelo diverge do que a tela pinta;
    d) nada de `required` nem `aria-invalid`: o switch nao tem erro nem e
       obrigatorio (regra 20);
    e) a bolinha e decorativa: `aria-hidden="true"`.

ORDEM DE EXECUCAO - mesma do Select, do Checkbox e do Radio: roda DEPOIS do
HTML que ele mede.

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
SWITCH = json.load(open(os.path.join(HERE, 'tokens.json')))

RES = SWITCH['resolved']
PENDING = SWITCH['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# estado -> como o switch e pintado, e qual excecao cobre cada papel
STATES = {
    'default':          dict(border='switch-border',          track='switch-track',          thumb='switch-thumb',                  ring=False, rotulo='switch-label',
                             exc_borda='borda-abaixo-de-3-1',   exc_thumb='bolinha-abaixo-de-3-1'),
    'hover':            dict(border='switch-border-hover',    track='switch-track',          thumb='switch-thumb',                  ring=False, rotulo='switch-label',
                             exc_borda=None,                    exc_thumb='bolinha-abaixo-de-3-1'),
    'focus':            dict(border='switch-border',          track='switch-track',          thumb='switch-thumb',                  ring=True,  rotulo='switch-label',
                             exc_borda='borda-abaixo-de-3-1',   exc_thumb='bolinha-abaixo-de-3-1'),
    'checked':          dict(border='switch-border-checked',  track='switch-track-checked',  thumb='switch-thumb-checked',          ring=False, rotulo='switch-label',
                             exc_borda=None,                    exc_thumb=None),
    'checked-focus':    dict(border='switch-border-checked',  track='switch-track-checked',  thumb='switch-thumb-checked',          ring=True,  rotulo='switch-label',
                             exc_borda=None,                    exc_thumb=None),
    'disabled':         dict(border='switch-border-disabled', track='switch-track-disabled', thumb='switch-thumb-disabled',         ring=False, rotulo='switch-label-disabled',
                             exc_borda='disabled-abaixo-de-aa', exc_thumb='disabled-abaixo-de-aa'),
    'disabled-checked': dict(border='switch-border-disabled', track='switch-track-disabled', thumb='switch-thumb-checked-disabled', ring=False, rotulo='switch-label-disabled',
                             exc_borda='disabled-abaixo-de-aa', exc_thumb='disabled-abaixo-de-aa'),
}

# estados sem variante no Figma - pintados so pelo codigo (etapa 3)
SO_NO_CODIGO = ('checked-focus', 'disabled-checked')


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
    shadow = RES['switch-ring'][theme]
    hexes = re.findall(r'#[0-9a-fA-F]{6}', shadow)
    if not hexes:
        raise ValueError(f'switch-ring ({theme}): box-shadow sem cor legivel -> {shadow}')
    return hexes[-1]


def pior(fg, fundos):
    return min((cr(fg, bg), bg) for bg in fundos)


def medir():
    linhas = []
    for state, cfg in STATES.items():
        for theme, _ in THEMES:
            paginas = [sem(p, theme) for p in PAGINAS]
            track = tok(cfg['track'], theme)
            fora = [sem('bg-canvas', theme)] if cfg['ring'] else paginas
            nota_fora = 'respiro do anel (bg-canvas)' if cfg['ring'] else 'pagina (pior caso)'
            exc_dis = 'disabled-abaixo-de-aa' if state.startswith('disabled') else None

            # 1. a borda - vizinha da pagina por fora e do trilho por dentro
            fg_hex = tok(cfg['border'], theme)
            fundos = fora + ([track] if track.lower() != fg_hex.lower() else [])
            ratio, bg_hex = pior(fg_hex, fundos)
            linhas.append(dict(state=state, theme=theme, papel='borda',
                               token=cfg['border'], fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                               floor=NON_TEXT_FLOOR, contra=f'{nota_fora} + trilho',
                               exc=cfg['exc_borda']))

            # 2. o anel
            if cfg['ring']:
                ink = ring_ink(theme)
                ratio, bg_hex = pior(ink, [sem('bg-canvas', theme)] + paginas)
                linhas.append(dict(state=state, theme=theme, papel='anel de foco',
                                   token='switch-ring', fgHex=ink, bgHex=bg_hex, ratio=ratio,
                                   floor=NON_TEXT_FLOOR, contra='respiro + pagina', exc=None))

            # 3. a bolinha, contra o trilho em que ela esta
            fg_hex = tok(cfg['thumb'], theme)
            linhas.append(dict(state=state, theme=theme, papel='bolinha',
                               token=cfg['thumb'], fgHex=fg_hex, bgHex=track,
                               ratio=cr(fg_hex, track), floor=NON_TEXT_FLOOR,
                               contra='trilho', exc=cfg['exc_thumb']))

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
    """Tira <style> e <script> antes de procurar marcacao - o switch.css traz a
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

    inputs = re.findall(r'<input\b[^>]*class="[^"]*al-switch__input[^"]*"[^>]*>', html)
    blocos = re.findall(r'<label\b[^>]*class="[^"]*\bal-switch\b[^"]*"[^>]*>(.*?)</label>',
                        html, flags=re.S)
    dentro = sum(len(re.findall(r'al-switch__input', b)) for b in blocos)

    # (a)
    if dentro != len(inputs):
        achados.append(f'(a) {len(inputs) - dentro} input(s) fora de <label class="al-switch">')
    # So dentro de TAG: prosa pode citar role="switch" em <code>.
    for tag in re.findall(r'<([a-zA-Z]+)\b[^>]*\srole="switch"[^>]*>', html):
        if tag.lower() != 'input':
            achados.append(f'(a) <{tag} role="switch"> - o componente e o input nativo')
    if re.search(r'<[a-zA-Z][^>]*\saria-pressed=', html) and re.search(r'al-switch', html):
        for tag in re.findall(r'<[a-zA-Z][^>]*\saria-pressed=[^>]*>', html):
            if 'al-switch' in tag:
                achados.append(f'(a) aria-pressed num switch - o estado e do checkbox nativo: {tag[:70]}')

    for tag in inputs:
        if not re.search(r'\btype="checkbox"', tag):
            achados.append(f'(a) input sem type="checkbox": {tag[:70]}')
        if not re.search(r'\brole="switch"', tag):
            achados.append(f'(a) input sem role="switch" - seria anunciado como caixa de selecao: {tag[:70]}')
        if 'aria-label' in tag:
            achados.append(f'(b) input usa aria-label/aria-labelledby havendo rotulo visivel: {tag[:70]}')
        if 'aria-checked' in tag:
            achados.append(f'(c) aria-checked no input - o estado e o `checked` nativo: {tag[:70]}')
        if re.search(r'\srequired\b', tag) or 'aria-invalid' in tag:
            achados.append(f'(d) required/aria-invalid num switch - ele nao tem erro: {tag[:70]}')

    # (b) rotulo visivel e nao-vazio em cada bloco
    for b in blocos:
        m = re.search(r'<span\b[^>]*al-switch__label[^>]*>(.*?)</span>', b, flags=re.S)
        if not m or not texto(m.group(1)):
            achados.append('(b) switch sem rotulo visivel em .al-switch__label')

    # (e)
    for th in re.findall(r'<span\b[^>]*al-switch__thumb[^>]*>', html):
        if 'aria-hidden="true"' not in th:
            achados.append(f'(e) bolinha sem aria-hidden="true": {th[:60]}')

    return (achados, len(inputs))


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    linhas = medir()

    reprovas = [l for l in linhas if not l['pass'] and not l['exc']]
    excecoes = [l for l in linhas if not l['pass'] and l['exc']]
    passam = [l for l in linhas if l['pass']]

    print('=' * 78)
    print('QA DE ACESSIBILIDADE DO SWITCH')
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
    print('efeito da pagina (o que a etapa 3 nao podia ver):')
    for theme, _ in THEMES:
        tr = tok('switch-track', theme)
        sf = sem('bg-surface', theme)
        igual = 'MESMA cor' if tr.lower() == sf.lower() else f'{cr(tr, sf)}:1'
        print(f'  trilho desligado x faixa bg-surface [{theme:<5}]: {igual} - '
              f'o limite e so a borda e a bolinha')
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
    print(f'contrato de marcacao - {os.path.relpath(path, ROOT)}  ({n} switch(es) medido(s)):')
    if achados:
        for a in achados:
            print('   ', a)
    elif n == 0:
        print('    PENDENTE - nenhum switch neste HTML. Nada medido nao e nada errado.')
    else:
        print('    as cinco regras passam em todos os switches')
    print('-' * 78)

    json.dump({
        'component': 'switch',
        'criterion': 'WCAG 1.4.3 texto (rotulo) + 1.4.11 nao-textual (borda, bolinha, anel)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'pages': list(PAGINAS),
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n,
        'markupPending': n == 0,
        'markupRules': [
            'input type="checkbox" role="switch" nativo dentro de <label class="al-switch">; nenhum outro role="switch", sem aria-pressed',
            'rotulo visivel e nao-vazio, sem aria-label nem aria-labelledby',
            'sem aria-checked: o estado e o checked nativo',
            'sem required nem aria-invalid: o switch nao tem erro',
            'bolinha decorativa: aria-hidden="true"',
        ],
        'fails': len(reprovas),
        'exceptions': {k: len([l for l in excecoes if l['exc'] == k]) for k in PENDING},
        'codeOnlyStates': list(SO_NO_CODIGO),
        'rows': linhas,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'components/switch/a11y.json escrito ({len(linhas)} medicoes)')
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
