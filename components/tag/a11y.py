"""
QA de acessibilidade do Tag.

Como no Button e no Icon Button, a validacao e por COMBINACAO RENDERIZADA -
cada tipo, cada status, cada tema, contra o fundo efetivo que o elemento
realmente tem na tela. Tipo sem preenchimento encosta na TELA, nao em
"transparente" - e, como a tag costuma viver dentro de um card, encosta tambem
em bg-surface. Os dois fundos sao medidos.

O QUE MUDA EM RELACAO AO ICON BUTTON

  La o portador do sentido e um icone: piso de 3:1, criterio 1.4.11.
  Aqui o portador e um ROTULO DE TEXTO: piso de 4,5:1, criterio 1.4.3.
  E por isso que o status Brand saiu do escopo - branco sobre bg-brand da
  3,34:1, que passa como icone e reprova como texto. Mesma cor, criterio
  diferente, decisao diferente.

O LIMITE DO PILL NAO E PORTAO, E RELATORIO

  No Icon Button o limite visivel do componente e medido como portao, porque
  sem rotulo o proprio desenho e a unica coisa que informa que existe um
  acionavel ali. Aqui nao: quem informa e o texto. O contorno do pill e
  decoracao, e o 1.4.11 cobra contraste de elemento grafico NECESSARIO para
  entender o conteudo - o que este nao e.

  A consequencia concreta e o filled neutral, que da 1,32:1 contra a tela clara.
  Isso foi medido e aceito na etapa 1 (achado 5). Fica medido e listado aqui
  como ISENTO, nunca como reprova - e nunca some do relatorio, para ninguem
  "corrigir" achando que escapou.

O CONTRATO DE MARCACAO

  Dois contratos deste componente nao vivem no CSS:

    a) a tag read-only NAO e focavel e NAO e acionavel - ela e conteudo;
    b) o X precisa de aria-label que INCLUA o rotulo da tag. Numa lista de seis
       filtros, seis botoes chamados "Remover" sao indistinguiveis por leitor
       de tela.

  O (b) e verificavel de verdade: da para extrair o texto da tag e conferir se
  ele aparece dentro do aria-label. E o que a secao de marcacao faz.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede site/index.html (o componente entra la na etapa 7)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
TAG = json.load(open(os.path.join(HERE, 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = TAG['resolved']
THEMES = ('light', 'dark')
TYPES = ('filled', 'outlined')
STATUSES = ('success', 'warning', 'error', 'info', 'neutral')

TEXT_FLOOR = 4.5          # 1.4.3 - o rotulo e texto
NON_TEXT_FLOOR = 3.0      # 1.4.11 - o anel de foco e elemento nao-textual

# Os dois fundos onde uma tag realmente aparece. bg-surface importa porque tag
# quase sempre vive dentro de card, tabela ou painel, nao solta na tela.
UNDERS = ('bg-canvas', 'bg-surface')

SITE = os.path.join(ROOT, 'site', 'index.html')


def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def cr(a, b):
    l1, l2 = sorted((lum(a), lum(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def tok(name, theme):
    v = RES[f'tag-{name}']
    return v[theme] if isinstance(v, dict) else v


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def effective_bg(tipo, status, theme, under):
    """Fundo que o rotulo realmente encosta. Transparente = o fundo aparece."""
    key = f'{tipo}-{status}-bg' if tipo == 'filled' else f'{tipo}-bg'
    value = tok(key, theme)
    return sem(under, theme) if value == 'transparent' else value


# ─────────────────────────────────────────────── contrato de marcacao
OPEN_TAG = re.compile(r'<(\w+)\b([^>]*\bclass="[^"]*\bal-tag\b[^"]*"[^>]*)>')
DISMISS = re.compile(r'<button\b[^>]*\bclass="[^"]*\bal-tag__dismiss\b[^"]*"[^>]*>')


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()


def markup_contract(path):
    """Cobra o contrato de cada .al-tag no HTML.

    Regras, todas da etapa 4:
      23/24  a tag read-only nao e focavel nem acionavel - nada de <button>,
             role="button" ou tabindex no proprio .al-tag
      25     o X tem aria-label nao vazio E que inclui o rotulo da tag
      -      o X e type="button": dentro de <form> o padrao do HTML e submit
      -      o svg dentro do X e decorativo: aria-hidden

    Retorna (checked, problems). checked = None quando o HTML ainda nao emite o
    componente - o caso ate a etapa 7 montar o playground. Isso e PENDENTE, nao
    aprovacao: o portao passa a valer sozinho quando o HTML aparecer.
    """
    if not os.path.exists(path):
        return None, [f'{path} nao existe']

    html = open(path).read()
    for pat in (r'<style\b.*?</style>', r'<script\b.*?</script>', r'<!--.*?-->'):
        html = re.sub(pat, lambda m: '\n' * m.group(0).count('\n'), html, flags=re.S)

    checked, problems = 0, []

    for m in OPEN_TAG.finditer(html):
        elem, attrs = m.group(1), m.group(2)
        if re.search(r'\bal-tag__', attrs):      # o proprio X, tratado abaixo
            continue
        checked += 1
        line = html.count('\n', 0, m.start()) + 1
        if elem.lower() == 'button':
            problems.append(f'linha {line}: a tag e <button> - ela e conteudo, '
                            f'nao controle; so o X e acionavel')
        if 'role="button"' in attrs:
            problems.append(f'linha {line}: role="button" na tag - clicar no rotulo '
                            f'nao faz nada, e anuncia-la como botao mente')
        if re.search(r'\btabindex="0"', attrs):
            problems.append(f'linha {line}: tabindex="0" na tag - a read-only fica '
                            f'fora da ordem de tabulacao')

    for m in DISMISS.finditer(html):
        tagstr = m.group(0)
        line = html.count('\n', 0, m.start()) + 1

        label = re.search(r'aria-label="([^"]*)"', tagstr)
        if not (label and label.group(1).strip()):
            problems.append(f'linha {line}: X sem aria-label - botao mudo para '
                            f'leitor de tela')
        else:
            # o rotulo da tag e o texto entre a abertura do .al-tag e o X
            start = html.rfind('class="', 0, m.start())
            open_m = None
            for om in OPEN_TAG.finditer(html[:m.start()]):
                if not re.search(r'\bal-tag__', om.group(2)):
                    open_m = om
            texto = strip_tags(html[open_m.end():m.start()]) if open_m else ''
            if texto and texto.lower() not in label.group(1).lower():
                problems.append(
                    f'linha {line}: aria-label "{label.group(1)}" nao inclui o rotulo '
                    f'"{texto}" - numa lista de filtros, varios "Remover" sao '
                    f'indistinguiveis por leitor de tela')

        if not re.search(r'type="button"', tagstr):
            problems.append(f'linha {line}: X sem type="button" - dentro de <form> '
                            f'o padrao do HTML e submit')

    n_dismiss = len(DISMISS.findall(html))
    for m in DISMISS.finditer(html):
        fim = html.find('</button>', m.end())
        corpo = html[m.end():fim if fim > 0 else m.end()]
        if '<svg' in corpo and 'aria-hidden="true"' not in corpo:
            line = html.count('\n', 0, m.start()) + 1
            problems.append(f'linha {line}: svg do X sem aria-hidden - o nome vive '
                            f'no botao, anunciar os dois e ruido duplicado')

    if checked == 0:
        return None, ['nenhum .al-tag no HTML - o componente entra no site na etapa 7 '
                      '(playground); ate la este portao fica pendente']
    return checked, problems


def write_report(rows, checked, targets, path_html):
    out = {
        'component': 'tag',
        'criterion': 'WCAG 1.4.3 texto (rotulo) + 1.4.11 nao-textual (anel de foco)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path_html, ROOT),
        'markupChecked': checked,
        'markupPending': checked is None,
        'fails': sum(1 for r in rows if r[6] is not None and not r[7]),
        'targets': [{'size': s, 'box': b, 'meetsMinimum': b >= 24} for s, b in targets],
        'rows': [{'group': g, 'theme': t, 'label': l, 'fg': fg, 'bg': bg,
                  'ratio': round(ratio, 2), 'floor': floor,
                  'pass': ok, 'exempt': floor is None}
                 for g, t, l, fg, bg, ratio, floor, ok in rows],
    }
    p = os.path.join(HERE, 'a11y.json')
    json.dump(out, open(p, 'w'), indent=2, ensure_ascii=False)
    return p


def run(path_html):
    rows, failures = [], []

    # ---- 1. rotulo contra o fundo efetivo (1.4.3, 4,5:1) ----
    for theme in THEMES:
        for tipo in TYPES:
            for status in STATUSES:
                fg = tok(f'{tipo}-{status}-label', theme)
                for under in UNDERS:
                    bg = effective_bg(tipo, status, theme, under)
                    ratio = cr(fg, bg)
                    ok = ratio >= TEXT_FLOOR
                    rows.append(('rotulo', theme, f'{tipo} {status} · sobre {under}',
                                 fg, bg, ratio, TEXT_FLOOR, ok))
                    if not ok:
                        failures.append((theme, tipo, status, under, ratio, TEXT_FLOOR))
                    if tipo == 'filled':
                        break   # o preenchimento cobre o fundo: medir uma vez basta

    # ---- 2. limite do pill: medido, ISENTO, nunca portao ----
    # Ver o cabecalho: quem carrega o sentido e o texto, entao o contorno e
    # decoracao e o 1.4.11 nao se aplica. O neutral em 1,32 e o caso conhecido.
    for theme in THEMES:
        for tipo in TYPES:
            for status in STATUSES:
                key = f'{tipo}-{status}-bg' if tipo == 'filled' else f'{tipo}-{status}-border'
                edge = tok(key, theme)
                if edge == 'transparent':
                    continue
                for under in UNDERS:
                    rows.append(('limite', theme, f'{tipo} {status} · sobre {under}',
                                 edge, sem(under, theme), cr(edge, sem(under, theme)),
                                 None, True))

    # ---- 3. anel de foco do X contra o fundo (1.4.11, 3:1) ----
    # O anel e composto: 2px de bg-canvas como respiro, depois 4px na cor do
    # foco. Quem precisa se destacar do fundo e a cor externa.
    for theme in THEMES:
        fg = sem('shadow-focus-default', theme)
        for under in UNDERS:
            bg = sem(under, theme)
            ratio = cr(fg, bg)
            ok = ratio >= NON_TEXT_FLOOR
            rows.append(('foco', theme, f'anel do X · sobre {under}',
                         fg, bg, ratio, NON_TEXT_FLOOR, ok))
            if not ok:
                failures.append((theme, 'dismiss', 'ring', under, ratio, NON_TEXT_FLOOR))

    # ---- 4. alvo de toque do X ----
    targets = [(s, TAG['resolved'][f'tag-{s}-icon-size']) for s in ('sm', 'md')]

    checked, mk_problems = markup_contract(path_html)

    print('=' * 74)
    print('QA DE ACESSIBILIDADE DO TAG')
    print('=' * 74)
    for group, title in (('rotulo', 'ROTULO contra o fundo efetivo (1.4.3, piso 4,5)'),
                         ('foco', 'ANEL DE FOCO do X contra o fundo (1.4.11, piso 3,0)'),
                         ('limite', 'LIMITE do pill - medido, ISENTO (o texto carrega o sentido)')):
        sel = [r for r in rows if r[0] == group]
        print(f'\n{title}')
        for _, theme, label, fg, bg, ratio, floor, ok in sel:
            mark = '  ' if floor is None else ('ok' if ok else 'XX')
            piso = '  isento' if floor is None else f'piso {floor}'
            print(f'  {mark} {theme:<5} {label:<40} {fg} sobre {bg}  {ratio:5.2f}  {piso}')

    print('\nALVO DE TOQUE do X (WCAG 2.5.8, minimo 24px)')
    for size, box in targets:
        estado = 'ok' if box >= 24 else 'abaixo do minimo - excecao consciente da etapa 3'
        print(f'     {size:<5} {box}x{box}px  {estado}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path_html, ROOT)}')
    if checked is None:
        for p in mk_problems:
            print(f'     pendente: {p}')
    else:
        print(f'     {checked} tag(s) conferida(s)')
        for p in mk_problems:
            print(f'     PROBLEMA: {p}')

    medidas = [r for r in rows if r[6] is not None]
    isentas = [r for r in rows if r[6] is None]
    print('-' * 74)
    print(f'{len(medidas)} combinacoes com piso  |  passam: {len(medidas) - len(failures)}  |  '
          f'reprovam: {len(failures)}  |  isentas medidas: {len(isentas)}')

    path = write_report(rows, checked, targets, path_html)
    print(f'{os.path.relpath(path, ROOT)} escrito')

    if failures:
        print('-' * 74)
        print(f'{len(failures)} COMBINACAO(OES) REPROVAM:')
        for theme, tipo, status, under, ratio, floor in failures:
            print(f'   {theme} {tipo} {status} sobre {under}: {ratio:.2f} < {floor}')
        return 1
    if checked is not None and mk_problems:
        print('-' * 74)
        print(f'{len(mk_problems)} PROBLEMA(S) DE MARCACAO - portao reprova')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else SITE))
