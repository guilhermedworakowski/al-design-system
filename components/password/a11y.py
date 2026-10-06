"""
QA de acessibilidade do Password.

Como no Input, a validacao e por COMBINACAO RENDERIZADA - cada papel de cor
contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  1. A BORDA TROCA DE VIZINHO QUANDO O CAMPO RECEBE FOCO. Em repouso ela toca a
     pagina (`bg-canvas` ou `bg-surface-raised` - vale a pior). Com foco, o
     anel desenha um respiro de 2px em `bg-canvas` colado na borda.

  2. A COR DO ANEL SAI DO PROPRIO box-shadow - o ultimo hex da sombra composta.

  3. O ANEL DO OLHO VIVE DENTRO DO CAMPO. O respiro de 2px dele e `bg-canvas`,
     nao o fundo do campo: no escuro e um contorno #181818 dentro de #3E3E3E
     (aceito na etapa 3). O anel e medido contra as DUAS coisas que tocam a
     cor dele - o respiro e o preenchimento do campo - e vale a pior. Ele e
     sempre o anel padrao, inclusive com o campo em erro (regra 19).

  4. O OLHO E GRAFICO: piso 3:1 (1.4.11), contra o preenchimento do campo.

DOIS PISOS: texto 4,5:1 (1.4.3); borda, anel e olho 3:1 (1.4.11).

O CONTRATO DE MARCACAO - dez regras da etapa 4, mais o id unico

    a) todo `.al-password__field` tem `id` e um `<label for>` de rotulo
       apontando para ele (regras 4 e 29);
    b) campo com `aria-invalid="true"` tem `aria-describedby`, o id existe e o
       texto la dentro nao esta vazio (regras 8 e 29);
    c) nenhum campo usa `aria-label` havendo rotulo visivel (regra 29);
    d) nenhum campo usa `maxlength` (regra 12);
    e) o campo nasce `type="password"` (regra 13);
    f) o campo declara `autocomplete` current-password ou new-password,
       `spellcheck="false"` e `autocapitalize="none"` (regras 25-26);
    g) o olho e `<button type="button">` com `aria-controls` = id do campo e
       `aria-label` nao vazio (regra 28);
    h) os icones do olho sao `aria-hidden="true" focusable="false"`
       (contrato do Icon);
    i) campo desabilitado -> o botao do olho tambem `disabled` (regra 20);
    j) o `id` do campo e UNICO no documento (licao do Select, 0.11.0).

ORDEM DE EXECUCAO - roda DEPOIS do site.py (mesmo arranjo do Input). Sem
argumento mede site/index.html; enquanto o site nao tiver Password, o JSON sai
com `markupPending: true`.

Rodar: python3 a11y.py [caminho.html]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
PW = json.load(open(os.path.join(HERE, 'tokens.json')))

RES = PW['resolved']
PENDING = PW['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface-raised')

BORDA = 'borda-abaixo-de-3-1'
OFF = 'disabled-abaixo-de-aa'

# estado -> papeis. `ring`: anel do CAMPO. `toggle_ring`: o olho pode estar
# focado naquele estado (no disabled, nao: botao desabilitado nao recebe foco).
STATES = {
    'default':     dict(border='password-border',          surface='password-bg',          ring=None,                  kind='normal', exc=BORDA, toggle_ring=True),
    'hover':       dict(border='password-border-hover',    surface='password-bg',          ring=None,                  kind='normal', exc=None,  toggle_ring=False),
    'focus':       dict(border='password-border-focus',    surface='password-bg',          ring='password-ring',       kind='normal', exc=None,  toggle_ring=False),
    'error':       dict(border='password-border-error',    surface='password-bg',          ring=None,                  kind='erro',   exc=None,  toggle_ring=True),
    'focus-error': dict(border='password-border-error',    surface='password-bg',          ring='password-ring-error', kind='erro',   exc=None,  toggle_ring=False),
    'disabled':    dict(border='password-border-disabled', surface='password-bg-disabled', ring=None,                  kind='off',    exc=OFF,   toggle_ring=False),
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
    return round((max(la, lb) + 0.05) / (min(la, lb) + 0.05), 2)


def tok(name, theme):
    return RES[name][theme]


def sem(name, theme):
    return FOUND['color']['semantic'][name][0 if theme == 'light' else 1]


def ring_ink(name, theme):
    hexes = re.findall(r'#[0-9a-fA-F]{6}', RES[name][theme])
    if not hexes:
        raise ValueError(f'{name} ({theme}): box-shadow sem cor legivel')
    return hexes[-1]


def pior(fg, fundos):
    return min((cr(fg, bg), bg) for bg in fundos)


def medir():
    linhas = []

    def add(state, theme, papel, token, fg, bg, ratio, floor, contra, exc):
        linhas.append(dict(state=state, theme=theme, papel=papel, token=token,
                           fgHex=fg, bgHex=bg, ratio=ratio, floor=floor,
                           contra=contra, exc=exc))

    for state, cfg in STATES.items():
        for theme, _ in THEMES:
            surface = tok(cfg['surface'], theme)
            paginas = [sem(p, theme) for p in PAGINAS]

            # 1. borda
            if cfg['ring']:
                fora, nota = [sem('bg-canvas', theme)], 'respiro do anel (bg-canvas)'
            else:
                fora, nota = paginas, 'pagina (pior de canvas / surface-raised)'
            fg = tok(cfg['border'], theme)
            ratio, bg = pior(fg, fora + [surface])
            add(state, theme, 'borda', cfg['border'], fg, bg, ratio,
                NON_TEXT_FLOOR, f'{nota} + preenchimento', cfg['exc'])

            # 2. anel do campo
            if cfg['ring']:
                ink = ring_ink(cfg['ring'], theme)
                ratio, bg = pior(ink, [sem('bg-canvas', theme)] + paginas)
                add(state, theme, 'anel do campo', cfg['ring'], ink, bg, ratio,
                    NON_TEXT_FLOOR, 'respiro + pagina', None)

            # 3. anel do olho - dentro do campo
            if cfg['toggle_ring']:
                ink = ring_ink('password-toggle-ring', theme)
                ratio, bg = pior(ink, [sem('bg-canvas', theme), surface])
                add(state, theme, 'anel do olho', 'password-toggle-ring', ink, bg, ratio,
                    NON_TEXT_FLOOR, 'respiro (bg-canvas) + preenchimento', None)

            # 4. dentro do campo
            if cfg['kind'] == 'off':
                dentro = [('texto', 'password-text-disabled', TEXT_FLOOR, OFF),
                          ('olho', 'password-toggle-icon-disabled', NON_TEXT_FLOOR, OFF)]
            else:
                dentro = [('placeholder', 'password-text-placeholder', TEXT_FLOOR, None),
                          ('valor', 'password-text-value', TEXT_FLOOR, None),
                          ('olho', 'password-toggle-icon', NON_TEXT_FLOOR, None)]
            for papel, nome, floor, exc in dentro:
                fg = tok(nome, theme)
                add(state, theme, papel, nome, fg, surface, cr(fg, surface),
                    floor, 'preenchimento do campo', exc)

            # 5. fora do campo, contra a pagina (pior caso)
            if cfg['kind'] == 'off':
                fora_campo = [('rotulo', 'password-label-disabled', OFF)]
            elif cfg['kind'] == 'erro':
                fora_campo = [('rotulo', 'password-label-error', None),
                              ('mensagem de erro', 'password-help-error', None)]
            else:
                fora_campo = [('rotulo', 'password-label', None)]
            for papel, nome, exc in fora_campo:
                fg = tok(nome, theme)
                ratio, bg = pior(fg, paginas)
                add(state, theme, papel, nome, fg, bg, ratio,
                    TEXT_FLOOR, 'pagina (pior caso)', exc)

    for l in linhas:
        l['pass'] = l['ratio'] >= l['floor']
    return linhas


# ------------------------------------------------------- contrato de marcacao
def so_marcacao(html):
    """Tira <style> e <script> antes de procurar marcacao - o password.css traz
    a ANATOMIA num comentario, e a pagina o inlina. Licao do Select."""
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)
    return html


def attr(tag, nome):
    m = re.search(rf'\b{nome}="([^"]*)"', tag)
    return m.group(1) if m else None


def marcacao(path):
    if not os.path.exists(path):
        return ([f'HTML nao encontrado em {path} - contrato de marcacao NAO medido'], 0)

    html = so_marcacao(open(path, encoding='utf-8').read())
    achados = []

    rotulo_de = {}
    for lb in re.findall(r'<label\b[^>]*>', html):
        if 'al-password__label' in (attr(lb, 'class') or '') and attr(lb, 'for'):
            rotulo_de[attr(lb, 'for')] = True

    # cada componente inteiro, para casar campo e botao do mesmo bloco
    blocos = re.findall(r'<div class="al-password">(.*?)</div>\s*(?:<p\b[^>]*>.*?</p>\s*)?</div>',
                        html, flags=re.S)
    n_campos = 0
    for bloco in blocos:
        campo = re.search(r'<input\b[^>]*al-password__field[^>]*>', bloco)
        if not campo:
            continue
        n_campos += 1
        tag = campo.group(0)
        cid = attr(tag, 'id')
        if not cid:
            achados.append(f'(a) <input> sem id: {tag[:70]}')
            continue
        n_id = len(re.findall(rf'\bid="{re.escape(cid)}"', html))
        if n_id > 1:
            achados.append(f'(j) id "{cid}" aparece {n_id} vezes')
        if cid not in rotulo_de:
            achados.append(f'(a) nenhum <label class="al-password__label" for="{cid}">')
        if re.search(r'\baria-label=', tag) and cid in rotulo_de:
            achados.append(f'(c) campo "{cid}" usa aria-label havendo rotulo visivel')
        if re.search(r'\bmaxlength=', tag):
            achados.append(f'(d) campo "{cid}" usa maxlength')
        if attr(tag, 'type') != 'password':
            achados.append(f'(e) campo "{cid}" nao nasce type="password"')
        if attr(tag, 'autocomplete') not in ('current-password', 'new-password'):
            achados.append(f'(f) campo "{cid}": autocomplete deve ser current-password ou new-password')
        if attr(tag, 'spellcheck') != 'false' or attr(tag, 'autocapitalize') != 'none':
            achados.append(f'(f) campo "{cid}": falta spellcheck="false" ou autocapitalize="none"')

        if 'aria-invalid="true"' in tag:
            desc = attr(tag, 'aria-describedby')
            if not desc:
                achados.append(f'(b) campo "{cid}" esta em erro e nao tem aria-describedby')
            else:
                for ref in desc.split():
                    m = re.search(rf'<(\w+)\b[^>]*\bid="{re.escape(ref)}"[^>]*>(.*?)</\1>', html, flags=re.S)
                    if not m:
                        achados.append(f'(b) campo "{cid}" descreve por "{ref}", que nao existe')
                    elif not re.sub(r'<[^>]+>', '', m.group(2)).strip():
                        achados.append(f'(b) campo "{cid}": a mensagem "{ref}" esta vazia')

        botao = re.search(r'<button\b[^>]*al-password__toggle[^>]*>(.*?)</button>', bloco, flags=re.S)
        if not botao:
            achados.append(f'(g) campo "{cid}" sem botao do olho')
            continue
        btag = re.match(r'<button\b[^>]*>', botao.group(0)).group(0)
        if attr(btag, 'type') != 'button':
            achados.append(f'(g) olho de "{cid}" sem type="button" - enviaria o formulario')
        if attr(btag, 'aria-controls') != cid:
            achados.append(f'(g) olho de "{cid}": aria-controls nao aponta para o campo')
        if not (attr(btag, 'aria-label') or '').strip():
            achados.append(f'(g) olho de "{cid}" sem aria-label')
        for svg in re.findall(r'<svg\b[^>]*>', botao.group(1)):
            if 'aria-hidden="true"' not in svg or 'focusable="false"' not in svg:
                achados.append(f'(h) icone do olho de "{cid}" sem aria-hidden/focusable')
        if re.search(r'\sdisabled\b', tag) and not re.search(r'\sdisabled\b', btag):
            achados.append(f'(i) campo "{cid}" desabilitado e o olho nao')

    return (achados, n_campos)


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    linhas = medir()

    reprovas = [l for l in linhas if not l['pass'] and not l['exc']]
    excecoes = [l for l in linhas if not l['pass'] and l['exc']]
    passam = [l for l in linhas if l['pass']]

    print('=' * 78)
    print('QA DE ACESSIBILIDADE DO PASSWORD')
    print('=' * 78)
    print(f'  combinacoes medidas : {len(linhas)}  ({len(STATES)} estados x 2 temas x papeis visiveis)')
    print(f'  passam              : {len(passam)}')
    print(f'  excecoes declaradas : {len(excecoes)}')
    print(f'  reprovas            : {len(reprovas)}')
    print('-' * 78)
    for state in STATES:
        do_estado = [l for l in linhas if l['state'] == state]
        p = min(do_estado, key=lambda l: l['ratio'] / l['floor'])
        marca = 'EXC' if p['exc'] and not p['pass'] else ('ok' if p['pass'] else 'XX')
        print(f'  {state:<12} pior papel: {p["papel"]:<18} '
              f'{p["ratio"]:>6}:1 / {p["floor"]}  [{p["theme"]}] {marca}')
    print('-' * 78)
    print('anel do olho (vive dentro do campo - o que a etapa 3 nao podia ver):')
    for theme, _ in THEMES:
        l = next(l for l in linhas if l['state'] == 'default' and l['theme'] == theme
                 and l['papel'] == 'anel do olho')
        print(f'  [{theme:<5}] {l["ratio"]}:1 contra {l["bgHex"]} (pior entre respiro e preenchimento)')
    print('-' * 78)
    if excecoes:
        print(f'excecoes conscientes - {len(excecoes)} medicoes, nenhuma e achado novo:')
        for chave in PENDING:
            n = [l for l in excecoes if l['exc'] == chave]
            if n:
                print(f'   {chave}: {len(n)} medicoes, '
                      f'{min(l["ratio"] for l in n)}:1 a {max(l["ratio"] for l in n)}:1')
    print('-' * 78)

    achados, n_campos = marcacao(path)
    print(f'contrato de marcacao - {os.path.relpath(path, ROOT)}  ({n_campos} campo(s) medido(s)):')
    if n_campos == 0 and not achados:
        print('    PENDENTE - nenhum campo neste HTML. Rodar site/site.py e chamar')
        print('    este portao de novo (ver ORDEM DE EXECUCAO no cabecalho).')
    elif achados:
        for a in achados:
            print('   ', a)
    else:
        print('    as dez regras passam em todos os campos')
    print('-' * 78)

    json.dump({
        'component': 'password',
        'criterion': 'WCAG 1.4.3 texto (rotulo, valor, placeholder, erro) + '
                     '1.4.11 nao-textual (borda, aneis, olho)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n_campos,
        'markupPending': n_campos == 0,
        'markupRules': [
            'todo campo tem id e um <label for> de rotulo apontando para ele',
            'campo em erro tem aria-invalid="true" e aria-describedby para uma mensagem nao vazia',
            'nenhum campo usa aria-label havendo rotulo visivel',
            'nenhum campo usa maxlength',
            'o campo nasce type="password"',
            'autocomplete current/new-password, spellcheck="false", autocapitalize="none"',
            'olho e <button type="button"> com aria-controls e aria-label',
            'icones do olho com aria-hidden="true" focusable="false"',
            'campo desabilitado -> olho desabilitado',
            'o id do campo e unico no documento',
        ],
        'fails': len(reprovas),
        'exceptions': {k: len([l for l in excecoes if l['exc'] == k]) for k in PENDING},
        'rows': linhas,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'components/password/a11y.json escrito ({len(linhas)} medicoes)')
    print('-' * 78)

    if reprovas:
        print(f'{len(reprovas)} COMBINACAO(OES) REPROVAM:')
        for l in reprovas:
            print(f'   {l["state"]}/{l["theme"]} {l["papel"]}: {l["ratio"]}:1 < {l["floor"]} '
                  f'(contra {l["contra"]})')
        return 1
    if achados and n_campos:
        print(f'{len(achados)} QUEBRA(S) DE CONTRATO DE MARCACAO - PORTAO REPROVA.')
        return 1
    if n_campos == 0:
        print('contraste renderizado: em ordem. Marcacao: PENDENTE, nada medido ainda.')
        return 0
    print('contraste renderizado e contrato de marcacao: tudo em ordem.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
