"""
QA de acessibilidade do Input.

Como no Select, a validacao e por COMBINACAO RENDERIZADA - cada papel de cor
contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  1. A BORDA TROCA DE VIZINHO QUANDO O CAMPO RECEBE FOCO. Em repouso ela toca a
     pagina, que pode ser `bg-canvas` OU `bg-surface-raised` (campo dentro de
     card ou modal) - vale a pior. Com foco, o anel desenha um respiro de 2px
     em `bg-canvas` colado na borda, e a vizinha externa passa a ser sempre
     `bg-canvas`.

  2. A COR DO ANEL SAI DO PROPRIO box-shadow - o ultimo hex da sombra composta.

  3. A BORDA TEM DUAS VIZINHAS: por fora a pagina (ou o respiro do anel), por
     dentro o preenchimento do campo. Vale a PIOR.

  4. O READ-ONLY TEM FUNDO PROPRIO. Valor e afixo medem contra `bg-readonly`,
     e placeholder NAO e medido ali porque o CSS o torna transparente (regra
     22) - o contrato de marcacao abaixo cobra que o read-only tenha valor.

DOIS PISOS: texto 4,5:1 (1.4.3); borda e anel 3:1 (1.4.11).

O CONTRATO DE MARCACAO - oito regras, sete da etapa 4 e uma da licao do Select

    a) todo `.al-input__field` tem `id` e um `<label for>` de rotulo
       (`.al-input__label`) apontando para ele (regras 4 e 28);
    b) campo com `aria-invalid="true"` tem `aria-describedby`, o id existe e o
       texto la dentro nao esta vazio - a mensagem e obrigatoria (regras 17, 30);
    c) campo com afixo tem `aria-labelledby` com o id do rotulo e o id de cada
       afixo que aponta para ele (regra 29);
    d) nenhum campo usa `aria-label` havendo rotulo visivel (regra 28);
    e) nenhum campo usa `maxlength` - o limite nao trava a digitacao (regra 14);
    f) todo contador declara `aria-live` (regra 30);
    g) campo `readonly` tem `value` nao vazio - vazio mostra "—" (regra 22);
    h) o `id` do campo e UNICO no documento - senao o `<label for>` liga no
       primeiro elemento com aquele id. O playground do Select caiu nisso ate
       0.11.0 (`pg-select` era tambem o id da pagina) e nenhuma outra regra viu.

ORDEM DE EXECUCAO - roda DEPOIS do site.py (mesmo arranjo do Select). Enquanto
o site nao tiver Input, o JSON sai com `markupPending: true`.

Rodar: python3 a11y.py [caminho.html]     sem argumento, mede site/index.html
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
INPUT = json.load(open(os.path.join(HERE, 'tokens.json')))

RES = INPUT['resolved']
PENDING = INPUT['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface-raised')

BORDA = 'borda-abaixo-de-3-1'
OFF = 'disabled-abaixo-de-aa'

# estado -> papeis. `ring=None`: aquele estado nao desenha anel.
STATES = {
    'default':     dict(border='input-border',          surface='input-bg',          ring=None,               kind='normal', exc=BORDA),
    'hover':       dict(border='input-border-hover',    surface='input-bg',          ring=None,               kind='normal', exc=None),
    'focus':       dict(border='input-border-focus',    surface='input-bg',          ring='input-ring',       kind='normal', exc=None),
    'error':       dict(border='input-border-error',    surface='input-bg',          ring=None,               kind='erro',   exc=None),
    'focus-error': dict(border='input-border-error',    surface='input-bg',          ring='input-ring-error', kind='erro',   exc=None),
    'disabled':    dict(border='input-border-disabled', surface='input-bg-disabled', ring=None,               kind='off',    exc=OFF),
    'readonly':    dict(border='input-border-readonly', surface='input-bg-readonly', ring=None,               kind='ro',     exc=BORDA),
    # o read-only recebe foco (regra 23): o anel vale ali tambem
    'focus-readonly': dict(border='input-border-readonly', surface='input-bg-readonly', ring='input-ring', kind='ro', exc=BORDA),
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

            # 2. anel
            if cfg['ring']:
                ink = ring_ink(cfg['ring'], theme)
                ratio, bg = pior(ink, [sem('bg-canvas', theme)] + paginas)
                add(state, theme, 'anel de foco', cfg['ring'], ink, bg, ratio,
                    NON_TEXT_FLOOR, 'respiro + pagina', None)

            # 3. dentro do campo, contra o preenchimento
            if cfg['kind'] == 'off':
                dentro = [('texto', 'input-text-disabled', OFF)]
            elif cfg['kind'] == 'ro':
                dentro = [('valor', 'input-text-value', None),
                          ('afixo', 'input-affix', None)]
            else:
                dentro = [('placeholder', 'input-text-placeholder', None),
                          ('valor', 'input-text-value', None),
                          ('afixo', 'input-affix', None)]
            for papel, nome, exc in dentro:
                fg = tok(nome, theme)
                add(state, theme, papel, nome, fg, surface, cr(fg, surface),
                    TEXT_FLOOR, 'preenchimento do campo', exc)

            # 4. fora do campo, contra a pagina (pior caso)
            if cfg['kind'] == 'off':
                fora_campo = [('rotulo', 'input-label-disabled', OFF),
                              ('marca opcional', 'input-label-disabled', OFF),
                              ('contador', 'input-label-disabled', OFF)]
            elif cfg['kind'] == 'erro':
                fora_campo = [('rotulo', 'input-label-error', None),
                              ('marca opcional', 'input-optional', None),
                              ('contador', 'input-counter', None),
                              ('mensagem de erro', 'input-help-error', None)]
            else:
                fora_campo = [('rotulo', 'input-label', None),
                              ('marca opcional', 'input-optional', None),
                              ('contador', 'input-counter', None),
                              ('contador acima do limite', 'input-counter-error', None),
                              ('apoio', 'input-help', None)]
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
    """Tira <style> e <script> antes de procurar marcacao - o input.css traz a
    ANATOMIA num comentario, e a pagina o inlina. Licao do Select."""
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

    campos = re.findall(r'<input\b[^>]*class="[^"]*al-input__field[^"]*"[^>]*>', html)
    labels = re.findall(r'<label\b[^>]*>', html)
    rotulo_de = {}
    afixos_de = {}
    for lb in labels:
        alvo, cls = attr(lb, 'for'), attr(lb, 'class') or ''
        if not alvo:
            continue
        if 'al-input__label' in cls:
            rotulo_de[alvo] = attr(lb, 'id')
        elif 'al-input__affix' in cls:
            afixos_de.setdefault(alvo, []).append(attr(lb, 'id'))

    for tag in campos:
        cid = attr(tag, 'id')
        if not cid:
            achados.append(f'(a) <input> sem id: {tag[:70]}')
            continue
        n_id = len(re.findall(rf'\bid="{re.escape(cid)}"', html))
        if n_id > 1:
            achados.append(f'(h) id "{cid}" aparece {n_id} vezes - o <label for> pode ligar em outro elemento')
        if cid not in rotulo_de:
            achados.append(f'(a) nenhum <label class="al-input__label" for="{cid}">')
        if re.search(r'\baria-label=', tag) and cid in rotulo_de:
            achados.append(f'(d) campo "{cid}" usa aria-label havendo rotulo visivel')
        if re.search(r'\bmaxlength=', tag):
            achados.append(f'(e) campo "{cid}" usa maxlength - o limite nao trava a digitacao')

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
                        achados.append(f'(b) campo "{cid}" esta em erro e a mensagem "{ref}" esta vazia')

        afixos = afixos_de.get(cid, [])
        if afixos:
            nomes = (attr(tag, 'aria-labelledby') or '').split()
            faltam = [i for i in [rotulo_de.get(cid)] + afixos if i and i not in nomes]
            if not nomes:
                achados.append(f'(c) campo "{cid}" tem afixo e nao tem aria-labelledby')
            elif faltam:
                achados.append(f'(c) campo "{cid}": aria-labelledby nao inclui {faltam}')

        if re.search(r'\sreadonly\b', tag):
            if not (attr(tag, 'value') or '').strip():
                achados.append(f'(g) campo read-only "{cid}" esta vazio - usar "—" como valor')

    for sp in re.findall(r'<span\b[^>]*class="[^"]*al-input__counter[^"]*"[^>]*>', html):
        if 'aria-live=' not in sp:
            achados.append(f'(f) contador sem aria-live: {sp[:60]}')

    return (achados, len(campos))


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    linhas = medir()

    reprovas = [l for l in linhas if not l['pass'] and not l['exc']]
    excecoes = [l for l in linhas if not l['pass'] and l['exc']]
    passam = [l for l in linhas if l['pass']]

    print('=' * 78)
    print('QA DE ACESSIBILIDADE DO INPUT')
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
        print(f'  {state:<15} pior papel: {p["papel"]:<24} '
              f'{p["ratio"]:>6}:1 / {p["floor"]}  [{p["theme"]}] {marca}')
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

    achados, n_campos = marcacao(path)
    print(f'contrato de marcacao - {os.path.relpath(path, ROOT)}  ({n_campos} campo(s) medido(s)):')
    if n_campos == 0 and not achados:
        print('    PENDENTE - nenhum campo neste HTML. Rodar site/site.py e chamar')
        print('    este portao de novo (ver ORDEM DE EXECUCAO no cabecalho).')
    elif achados:
        for a in achados:
            print('   ', a)
    else:
        print('    as oito regras passam em todos os campos')
    print('-' * 78)

    json.dump({
        'component': 'input',
        'criterion': 'WCAG 1.4.3 texto (rotulo, marca, contador, valor, afixo, apoio) + '
                     '1.4.11 nao-textual (borda, anel)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n_campos,
        'markupPending': n_campos == 0,
        'markupRules': [
            'todo campo tem id e um <label for> de rotulo apontando para ele',
            'campo em erro tem aria-invalid="true" e aria-describedby para uma mensagem nao vazia',
            'campo com afixo tem aria-labelledby = rotulo + afixos',
            'nenhum campo usa aria-label havendo rotulo visivel',
            'nenhum campo usa maxlength',
            'todo contador declara aria-live',
            'campo read-only tem valor ("—" quando vazio)',
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
    print(f'components/input/a11y.json escrito ({len(linhas)} medicoes)')
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
