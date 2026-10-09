"""
QA de acessibilidade do Textarea.

Como no Select e no Input, a validacao e por COMBINACAO RENDERIZADA - cada papel de cor
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

  4. O READ-ONLY TEM FUNDO PROPRIO. O valor mede contra `bg-readonly`, e o
     placeholder NAO e medido ali porque o CSS o torna transparente (regra
     24) - o contrato de marcacao abaixo cobra que o read-only tenha conteudo.

  Diferenca para o Input: nao ha afixo, e a caixa e a propria <textarea> -
  as cores que o navegador pinta saem do mesmo elemento que recebe o estado.

DOIS PISOS: texto 4,5:1 (1.4.3); borda e anel 3:1 (1.4.11).

O CONTRATO DE MARCACAO - oito regras, todas da etapa 4

    a) todo `.al-textarea__field` tem `id` e um `<label for>` de rotulo
       (`.al-textarea__label`) apontando para ele (regras 4 e 27);
    b) campo com `aria-invalid="true"` tem `aria-describedby`, o id existe e o
       texto la dentro nao esta vazio - a mensagem e obrigatoria (regras 19, 28);
    c) o campo e `<textarea>` nativo - nenhum outro elemento leva a classe
       `al-textarea__field`, e nada leva `contenteditable` no lugar (regra 26);
    d) nenhum campo usa `aria-label` havendo rotulo visivel (regra 27);
    e) nenhum campo usa `maxlength` - o limite nao trava a digitacao (regra 16);
    f) todo contador declara `aria-live` (regra 28);
    g) campo `readonly` tem conteudo nao vazio - vazio mostra "—" (regra 24);
    h) todo campo declara `rows` >= 3 (regras 9 e 10) e o `id` e UNICO no
       documento (licao do Select ate o 0.11.0).

ORDEM DE EXECUCAO - roda DEPOIS do site.py (mesmo arranjo do Select). Enquanto
o site nao tiver Textarea, o JSON sai com `markupPending: true`.

Rodar: python3 a11y.py [caminho.html]     sem argumento, mede build/site/index.html
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import ROOT, TOKENS_JSON, SITE_HTML, comp_out  # noqa: E402
# este portao compara a razao ja arredondada em 2 casas, como sempre fez
from contrast import cr2 as cr  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
TA = json.load(open(comp_out('textarea', 'tokens.json')))

RES = TA['resolved']
PENDING = TA['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('textarea', 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface-raised')

BORDA = 'borda-abaixo-de-3-1'
OFF = 'disabled-abaixo-de-aa'

# estado -> papeis. `ring=None`: aquele estado nao desenha anel.
STATES = {
    'default':     dict(border='textarea-border',          surface='textarea-bg',          ring=None,               kind='normal', exc=BORDA),
    'hover':       dict(border='textarea-border-hover',    surface='textarea-bg',          ring=None,               kind='normal', exc=None),
    'focus':       dict(border='textarea-border-focus',    surface='textarea-bg',          ring='textarea-ring',       kind='normal', exc=None),
    'error':       dict(border='textarea-border-error',    surface='textarea-bg',          ring=None,               kind='erro',   exc=None),
    'focus-error': dict(border='textarea-border-error',    surface='textarea-bg',          ring='textarea-ring-error', kind='erro',   exc=None),
    'disabled':    dict(border='textarea-border-disabled', surface='textarea-bg-disabled', ring=None,               kind='off',    exc=OFF),
    'readonly':    dict(border='textarea-border-readonly', surface='textarea-bg-readonly', ring=None,               kind='ro',     exc=BORDA),
    # o read-only recebe foco (regra 24): o anel vale ali tambem
    'focus-readonly': dict(border='textarea-border-readonly', surface='textarea-bg-readonly', ring='textarea-ring', kind='ro', exc=BORDA),
}


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
                dentro = [('texto', 'textarea-text-disabled', OFF)]
            elif cfg['kind'] == 'ro':
                dentro = [('valor', 'textarea-text-value', None)]
            else:
                dentro = [('placeholder', 'textarea-text-placeholder', None),
                          ('valor', 'textarea-text-value', None)]
            for papel, nome, exc in dentro:
                fg = tok(nome, theme)
                add(state, theme, papel, nome, fg, surface, cr(fg, surface),
                    TEXT_FLOOR, 'preenchimento do campo', exc)

            # 4. fora do campo, contra a pagina (pior caso)
            if cfg['kind'] == 'off':
                fora_campo = [('rotulo', 'textarea-label-disabled', OFF),
                              ('marca opcional', 'textarea-label-disabled', OFF),
                              ('contador', 'textarea-label-disabled', OFF)]
            elif cfg['kind'] == 'erro':
                fora_campo = [('rotulo', 'textarea-label-error', None),
                              ('marca opcional', 'textarea-optional', None),
                              ('contador', 'textarea-counter', None),
                              ('mensagem de erro', 'textarea-help-error', None)]
            else:
                fora_campo = [('rotulo', 'textarea-label', None),
                              ('marca opcional', 'textarea-optional', None),
                              ('contador', 'textarea-counter', None),
                              ('contador acima do limite', 'textarea-counter-error', None),
                              ('apoio', 'textarea-help', None)]
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
    """Tira <style> e <script> antes de procurar marcacao - o textarea.css traz a
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

    # (c) a classe do campo so pode estar numa <textarea>
    for m in re.finditer(r'<(\w+)\b[^>]*class="[^"]*al-textarea__field[^"]*"[^>]*>', html):
        if m.group(1).lower() != 'textarea':
            achados.append(f'(c) al-textarea__field em <{m.group(1)}> - use <textarea> nativo')
    if re.search(r'class="[^"]*al-textarea[^"]*"[^>]*contenteditable|contenteditable[^>]*class="[^"]*al-textarea', html):
        achados.append('(c) contenteditable dentro do Textarea - use <textarea> nativo')

    campos = re.findall(r'(<textarea\b[^>]*class="[^"]*al-textarea__field[^"]*"[^>]*>)(.*?)</textarea>',
                        html, flags=re.S)
    rotulo_de = {}
    for lb in re.findall(r'<label\b[^>]*>', html):
        alvo, cls = attr(lb, 'for'), attr(lb, 'class') or ''
        if alvo and 'al-textarea__label' in cls:
            rotulo_de[alvo] = attr(lb, 'id')

    for tag, conteudo in campos:
        cid = attr(tag, 'id')
        if not cid:
            achados.append(f'(a) <textarea> sem id: {tag[:70]}')
            continue
        n_id = len(re.findall(rf'\bid="{re.escape(cid)}"', html))
        if n_id > 1:
            achados.append(f'(h) id "{cid}" aparece {n_id} vezes - o <label for> pode ligar em outro elemento')
        rows = attr(tag, 'rows')
        if not rows or not rows.isdigit() or int(rows) < 3:
            achados.append(f'(h) campo "{cid}" sem rows >= 3 (tem: {rows})')
        if cid not in rotulo_de:
            achados.append(f'(a) nenhum <label class="al-textarea__label" for="{cid}">')
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

        if re.search(r'\sreadonly\b', tag) and not conteudo.strip():
            achados.append(f'(g) campo read-only "{cid}" esta vazio - usar "—" como conteudo')

    for sp in re.findall(r'<span\b[^>]*class="[^"]*al-textarea__counter[^"]*"[^>]*>', html):
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
    print('QA DE ACESSIBILIDADE DO TEXTAREA')
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
        'component': 'textarea',
        'criterion': 'WCAG 1.4.3 texto (rotulo, marca, contador, valor, apoio) + '
                     '1.4.11 nao-textual (borda, anel)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n_campos,
        'markupPending': n_campos == 0,
        'markupRules': [
            'todo campo tem id e um <label for> de rotulo apontando para ele',
            'campo em erro tem aria-invalid="true" e aria-describedby para uma mensagem nao vazia',
            'o campo e <textarea> nativo, nunca contenteditable',
            'nenhum campo usa aria-label havendo rotulo visivel',
            'nenhum campo usa maxlength',
            'todo contador declara aria-live',
            'campo read-only tem conteudo ("—" quando vazio)',
            'todo campo declara rows >= 3 e o id e unico no documento',
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
    print(f'build/components/textarea/a11y.json escrito ({len(linhas)} medicoes)')
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
