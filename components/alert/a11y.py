"""
QA de acessibilidade do Alert.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - papel
x status x tema - contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  O Alert e conteudo da pagina, com fundo opaco `alert-bg`
  (bg-surface-raised): titulo, descricao, icone, o X e os botoes so encostam
  no fundo do proprio Alert. Quem encosta na pagina e a BORDA - e a pagina e
  a tela (bg-canvas) ou a superficie (bg-surface). Sem Modal: o Alert mora no
  topo da pagina, nunca dentro de dialog (regra 9).

  O X e o Ghost das acoes sobre surface-raised usam os -raised
  (bg-hover-raised / bg-active-raised, licao do Modal 0.18.1): a tinta e
  medida contra o fundo de repouso, de hover e de pressionado. O anel de foco
  de todos os botoes e medido contra o fundo do Alert - par que os portoes do
  Button e do Icon Button, medidos sobre a pagina, nao cobrem.

  O rotulo do Primary encosta so no fundo do proprio botao (bg-brand), que nao
  muda dentro do Alert: e o par do portao do Button, com a excecao de marca
  herdada (rotulo branco 3,34:1). Nao e medido de novo aqui.

CINCO JULGAMENTOS

  1. Titulo e descricao contra o fundo do Alert: 4,5:1 do 1.4.3.
  2. Icone de status contra o fundo do Alert: 3:1 do 1.4.11. E o icone que
     carrega o status (regra 16), entao ele tem que passar.
  3. Borda de cada status contra o fundo do Alert e contra cada pagina
     (canvas, surface): 3:1. Decorativa no status, mas e ela que separa a
     caixa da pagina.
  4. X: tinta contra repouso, hover e pressionado. 3:1.
  5. Ghost das acoes: rotulo contra repouso, hover e pressionado, 4,5:1.
     Anel de foco (X, Ghost e Primary) contra o fundo do Alert, 3:1.
  Sem excecao de contraste nova: nenhuma foi declarada nas etapas 1 a 4.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido:

    a) .al-alert-slot e uma <div> fora de <template> e fora de inert, com no
       maximo um .al-alert dentro - um por pagina (regras 9 e 11);
    b) o Alert presente no carregamento (no slot, fora de <template>) nao
       tem role nem aria-live, nem ele nem o slot: e conteudo comum
       (regra 23). O role so aparece quando o alert.js insere depois;
    c) todo Alert inserido depois nasce de um <template> cujo unico filho e
       a <div class="al-alert"> (o alert.js clona dali);
    d) um, e so um, modificador de status: --success, --warning, --danger ou
       --info. Sem Neutral (regra 28);
    e) filhos = <div class="al-alert__body"> e, opcional,
       <div class="al-alert__actions">, nessa ordem;
    f) no corpo, primeiro filho = <svg class="al-icon al-icon--24
       al-alert__icon"> com role="img", aria-label com o nome do status
       (Sucesso, Aviso, Perigo, Informação), sem aria-hidden, e o desenho do
       icone do status: circle-check, triangle-alert, circle-alert, info
       (regras 15 e 16);
    g) depois, <div class="al-alert__text"> com <p class="al-alert__title">
       e <p class="al-alert__description">, os dois com texto - nada mais. A
       descricao e obrigatoria (regra 13). Nenhum heading em lugar nenhum do
       Alert: nem h1-h6, nem role="heading" (regra 26);
    h) o X, se existir, e o ultimo filho do corpo: <button type="button">
       Icon Button Ghost sm com a classe al-alert__close, data-al-alert-close,
       aria-label="Fechar aviso" e o icone dentro aria-hidden (regra 27);
    i) acoes: um ou dois <button type="button" class="al-btn ... al-btn--md">
       com rotulo; com dois, Ghost primeiro e Primary depois (regra 17). Nada
       interativo fora do X e das acoes - sem link, campo, tabindex ou
       contenteditable;
    j) as amostras congeladas do site (.al-alert fora de <template> e fora
       do slot) ficam sob `inert` e `aria-hidden` num ancestral. A marcacao
       delas cumpre (d) a (i) igual - e o que a documentacao mostra.

ORDEM DE EXECUCAO - mesma dos outros: roda DEPOIS do HTML que ele mede.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede site/index.html (piloto: sem pagina de QA separada)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from contrast import cr  # noqa: E402
from htmltree import Tree, walk, classes, has, ancestors, text_of  # noqa: E402
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
AL = json.load(open(os.path.join(HERE, 'tokens.json')))
IB = json.load(open(os.path.join(ROOT, 'components', 'icon-button', 'tokens.json')))
BT = json.load(open(os.path.join(ROOT, 'components', 'button', 'tokens.json')))
ICON_DIR = os.path.join(ROOT, 'components', 'icon', 'icons')

SEM = FOUND['color']['semantic']
ALIAS = AL['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5         # 1.4.3
NON_TEXT_FLOOR = 3.0     # 1.4.11

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface')
STATUS = {
    'success': ('Sucesso', 'circle-check'),
    'warning': ('Aviso', 'triangle-alert'),
    'danger':  ('Perigo', 'circle-alert'),
    'info':    ('Informação', 'info'),
}
CLOSE_CLASSES = {'al-icon-btn', 'al-icon-btn--ghost', 'al-icon-btn--sm', 'al-alert__close'}
CLOSE_LABEL = 'Fechar aviso'
INTERATIVOS = ('a', 'button', 'input', 'select', 'textarea', 'details', 'summary')
HEADINGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def al(role, theme):
    return sem(ALIAS[f'alert-{role}'], theme)


def row(theme, what, fg_name, fg, bg_name, bg, floor):
    ratio = round(cr(fg, bg), 2)
    return {'theme': theme, 'what': what, 'fg': fg_name, 'fgHex': fg,
            'bg': bg_name, 'bgHex': bg, 'ratio': ratio, 'floor': floor,
            'pass': ratio >= floor, 'invisible': fg.lower() == bg.lower(),
            'exception': None}


def contrast_rows():
    rows = []
    bg_name = ALIAS['alert-bg']
    x_ink = IB['alias']['icon-button-ghost-ink']
    ghost_label = BT['alias']['button-ghost-label']
    estados = (('repouso', bg_name), ('hover', 'bg-hover-raised'), ('pressionado', 'bg-active-raised'))
    for t in THEMES:
        bg = al('bg', t)
        # 1. texto
        rows.append(row(t, 'titulo', ALIAS['alert-title'], al('title', t), bg_name, bg, TEXT_FLOOR))
        rows.append(row(t, 'descricao', ALIAS['alert-description'], al('description', t), bg_name, bg,
                        TEXT_FLOOR))
        # 2. icone de status
        for s in STATUS:
            rows.append(row(t, f'{s} / icone', ALIAS[f'alert-{s}-icon'], al(f'{s}-icon', t),
                            bg_name, bg, NON_TEXT_FLOOR))
        # 3. borda contra o proprio fundo e contra a pagina
        for s in STATUS:
            for p in (bg_name,) + PAGINAS:
                rows.append(row(t, f'{s} / borda', ALIAS[f'alert-{s}-border'], al(f'{s}-border', t),
                                p, sem(p, t), NON_TEXT_FLOOR))
        # 4. o X
        for estado, fundo in estados:
            rows.append(row(t, f'X / {estado}', x_ink, sem(x_ink, t), fundo, sem(fundo, t), NON_TEXT_FLOOR))
        # 5. Ghost das acoes + anel de foco
        for estado, fundo in estados:
            rows.append(row(t, f'Ghost / {estado}', ghost_label, sem(ghost_label, t), fundo, sem(fundo, t),
                            TEXT_FLOOR))
        rows.append(row(t, 'anel de foco', 'shadow-focus-default', sem('shadow-focus-default', t),
                        bg_name, bg, NON_TEXT_FLOOR))
    return rows


# ─────────────────────────────────────────────── marcacao
def shape(svg_kids):
    """Assinatura do desenho: tag + atributos geometricos de cada filho."""
    return [(k['tag'], tuple(sorted((a, v) for a, v in k['attrs'].items()
                                    if a not in ('class', 'style')))) for k in svg_kids]


def icon_shape(name):
    raw = open(os.path.join(ICON_DIR, name + '.svg')).read()
    t = Tree()
    t.feed(raw[raw.find('<svg'):])
    svg = next(n for n in walk(t.root) if n['tag'] == 'svg')
    return shape(svg['kids'])


SHAPES = {s: icon_shape(icon) for s, (_, icon) in STATUS.items()}


def check_alert(el, problems, where):
    """Devolve (status, tem_acoes, tem_x) ou None."""
    ln = el['line']

    def bad(msg):
        problems.append(f'{where}linha {ln}: {msg}')

    # (d)
    mods = [s for s in STATUS if has(el, f'al-alert--{s}')]
    extra = [c for c in classes(el) if c.startswith('al-alert--') and c[10:] not in STATUS]
    if el['tag'] != 'div':
        bad('o Alert e uma <div class="al-alert">')
    if len(mods) != 1 or extra:
        bad(f'status {mods + extra} - um, e so um, entre success, warning, danger e info (regra 28)')
        return None
    status = mods[0]
    label, icon = STATUS[status]

    # (g) heading em qualquer profundidade
    for k in walk(el):
        if k['tag'] in HEADINGS or k['attrs'].get('role') == 'heading':
            bad(f'<{k["tag"]}> como heading dentro do Alert - o titulo e um <p> (regra 26)')
            break

    # (e)
    kids = el['kids']
    if not kids or kids[0]['tag'] != 'div' or not has(kids[0], 'al-alert__body'):
        bad('primeiro filho = <div class="al-alert__body">')
        return None
    if len(kids) > 2 or (len(kids) == 2 and (kids[1]['tag'] != 'div' or not has(kids[1], 'al-alert__actions'))):
        bad('depois do corpo, so uma <div class="al-alert__actions"> (opcional)')
        return None
    body = kids[0]
    actions = kids[1] if len(kids) == 2 else None

    bk = body['kids']
    if len(bk) not in (2, 3):
        bad(f'{len(bk)} filhos no corpo - icone, texto e, opcional, o X')
        return None
    ico, txt = bk[0], bk[1]
    close = bk[2] if len(bk) == 3 else None

    # (f)
    ia = ico['attrs']
    if ico['tag'] != 'svg' or not {'al-icon', 'al-icon--24', 'al-alert__icon'} <= set(classes(ico)):
        bad('primeiro filho do corpo = <svg class="al-icon al-icon--24 al-alert__icon"> (regra 15)')
    else:
        if ia.get('role') != 'img' or ia.get('aria-label') != label or 'aria-hidden' in ia:
            bad(f'icone de {status}: role="img" + aria-label="{label}", sem aria-hidden - '
                f'o icone carrega o status (regra 16)')
        if shape(ico['kids']) != SHAPES[status]:
            bad(f'icone de {status} nao e o {icon} (regra 15)')

    # (g)
    tk = txt['kids']
    if txt['tag'] != 'div' or not has(txt, 'al-alert__text'):
        bad('segundo filho do corpo = <div class="al-alert__text">')
    elif (len(tk) != 2
          or tk[0]['tag'] != 'p' or not has(tk[0], 'al-alert__title') or not text_of(tk[0])
          or tk[1]['tag'] != 'p' or not has(tk[1], 'al-alert__description') or not text_of(tk[1])):
        bad('o texto e <p class="al-alert__title"> + <p class="al-alert__description">, os dois com '
            'texto - a descricao e obrigatoria (regras 13 e 26)')

    # (h)
    if close is not None:
        ca = close['attrs']
        if (close['tag'] != 'button' or ca.get('type') != 'button'
                or not CLOSE_CLASSES <= set(classes(close)) or 'data-al-alert-close' not in ca):
            bad('terceiro filho do corpo = <button type="button" class="al-icon-btn al-icon-btn--ghost '
                'al-icon-btn--sm al-alert__close" data-al-alert-close> (regra 27)')
        else:
            if ca.get('aria-label') != CLOSE_LABEL:
                bad(f'o X se chama "{CLOSE_LABEL}" (regra 27)')
            svgs = [k for k in close['kids'] if k['tag'] == 'svg']
            if (len(close['kids']) != 1 or len(svgs) != 1
                    or svgs[0]['attrs'].get('aria-hidden') != 'true'
                    or svgs[0]['attrs'].get('focusable') != 'false'):
                bad('dentro do X, so o icone, com aria-hidden="true" focusable="false"')

    # (i)
    botoes = []
    if actions is not None:
        botoes = actions['kids']
        ok = 1 <= len(botoes) <= 2 and all(
            b['tag'] == 'button' and b['attrs'].get('type') == 'button'
            and {'al-btn', 'al-btn--md'} <= set(classes(b)) and text_of(b) for b in botoes)
        if not ok:
            bad('acoes = um ou dois <button type="button" class="al-btn ... al-btn--md"> com rotulo (regra 17)')
        elif len(botoes) == 2 and not (has(botoes[0], 'al-btn--ghost') and has(botoes[1], 'al-btn--primary')):
            bad('com duas acoes, Ghost primeiro e Primary depois (regra 17)')
    permitidos = [b for b in botoes] + ([close] if close is not None else [])
    for k in walk(el):
        if any(k is p or any(a is p for a in ancestors(k)) for p in permitidos):
            continue
        if (k['tag'] in INTERATIVOS or 'tabindex' in k['attrs']
                or 'contenteditable' in k['attrs']):
            bad(f'<{k["tag"]}> interativo dentro do Alert - so o X e as acoes')
            break
    return status, actions is not None, close is not None


def frozen(sob):
    return (any('inert' in x['attrs'] for x in sob)
            and any(x['attrs'].get('aria-hidden') == 'true' for x in sob))


def markup_contract(html):
    """Devolve (slots, presentes, templates, congelados, por_status, problemas)."""
    t = Tree()
    t.feed(html)
    nodes = list(walk(t.root))
    problems = []

    # (a)
    slots = [n for n in nodes if has(n, 'al-alert-slot')]
    for s in slots:
        sob = list(ancestors(s))
        if s['tag'] != 'div':
            problems.append(f'linha {s["line"]}: o slot e uma <div class="al-alert-slot">')
        if any(x['tag'] == 'template' for x in sob):
            problems.append(f'linha {s["line"]}: slot dentro de <template> - ele existe desde o carregamento')
        if any('inert' in x['attrs'] or x['attrs'].get('aria-hidden') == 'true' for x in [s] + sob):
            problems.append(f'linha {s["line"]}: slot sob inert ou aria-hidden - o Alert sumiria do leitor')
        # (b) o slot tambem nao e regiao viva no carregamento
        if s['attrs'].get('role') or 'aria-live' in s['attrs']:
            problems.append(f'linha {s["line"]}: slot com role/aria-live - presente ao carregar e '
                            f'conteudo comum (regra 23)')
        dentro = [n for n in walk(s) if has(n, 'al-alert')]
        if len(dentro) > 1:
            problems.append(f'linha {s["line"]}: {len(dentro)} Alerts no slot - um por pagina (regra 11)')

    present, tpls, frz = 0, 0, 0
    by_status = {s: 0 for s in STATUS}
    for n in nodes:
        if not has(n, 'al-alert'):
            continue
        sob = list(ancestors(n))
        tpl = next((x for x in sob if x['tag'] == 'template'), None)
        slot = next((x for x in sob if has(x, 'al-alert-slot')), None)
        if tpl is not None:
            # (c)
            tpls += 1
            if tpl['kids'] != [n]:
                problems.append(f'linha {tpl["line"]}: <template id="{tpl["attrs"].get("id", "")}"> tem que '
                                f'ter a .al-alert como unico filho - o alert.js clona dali')
            r = check_alert(n, problems, '')
            if r:
                by_status[r[0]] += 1
        elif slot is not None:
            # (b)
            present += 1
            for x in [n] + sob[:sob.index(slot)]:
                if x['attrs'].get('role') or 'aria-live' in x['attrs']:
                    problems.append(f'linha {n["line"]}: Alert presente no carregamento com role/aria-live - '
                                    f'e conteudo comum (regra 23)')
                    break
            check_alert(n, problems, 'presente, ')
        else:
            # (j)
            frz += 1
            if not frozen(sob):
                problems.append(f'linha {n["line"]}: .al-alert fora do slot e fora de <template> sem inert + '
                                f'aria-hidden - amostra que o teclado alcanca')
            check_alert(n, problems, 'amostra, ')
    return len(slots), present, tpls, frz, by_status, problems


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    fails = [r for r in rows if not r['pass']]

    print('=' * 74)
    print('QA DE ACESSIBILIDADE DO ALERT')
    print('=' * 74)
    for r in fails:
        nota = 'INVISIVEL - igual ao fundo' if r['invisible'] else 'REPROVA'
        print(f'  XX {r["theme"]:<5} {r["what"]:<22} sobre {r["bg"]:<18} '
              f'{r["fgHex"]} x {r["bgHex"]}  {r["ratio"]:5.2f}  {nota}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    by_status, slots, present, frz = {}, 0, 0, 0
    if not os.path.exists(path):
        tpls, mk = None, [f'{path} nao existe']
    else:
        slots, present, tpls, frz, by_status, mk = markup_contract(open(path, encoding='utf-8').read())
        if tpls == 0:
            tpls, mk = None, ['nenhum <template> com .al-alert no HTML - rode site.py antes']
    if tpls is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        resumo = ', '.join(f'{s} {n}' for s, n in by_status.items())
        print(f'     {slots} slot(s), {present} Alert presente(s) no carregamento, {tpls} template(s) - '
              f'{resumo}; {frz} amostra(s) congelada(s) sob inert; 10 regras (a-j)')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 74)
    print(f'{len(rows)} medicoes  |  passam: {len(rows) - len(fails)}  |  excecoes: 0  |  '
          f'reprovas: {len(fails)}')

    json.dump({
        'component': 'alert',
        'criterion': 'WCAG 1.4.3 texto + 1.4.11 nao-textual',
        'markupSource': os.path.relpath(path, ROOT),
        'markupSlots': slots,
        'markupPresent': present,
        'markupChecked': tpls,
        'markupByStatus': by_status,
        'markupFrozen': frz,
        'markupPending': tpls is None,
        'markupProblems': mk if tpls is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} escrito')

    falhou = bool(fails)
    if tpls is None or mk:
        print('-' * 74)
        print(f'{len(mk)} PROBLEMA(S) DE MARCACAO - portao reprova')
        falhou = True
    return 1 if falhou else 0


if __name__ == '__main__':
    sys.exit(run())
