"""
QA de acessibilidade do Avatar.

Como no Button, Icon Button, Icon e Tag, a validacao e por COMBINACAO
RENDERIZADA - cada papel de cor contra o fundo efetivo, nao par de token solto.
Mas o fundo do Avatar nunca varia: e sempre `avatar-bg`, solido, nos tres tipos
(inclusive no Photo, onde ele e o chao enquanto a imagem carrega). Entao a
medicao de contraste aqui e a mais curta do sistema ate agora - dois papeis,
dois temas, quatro linhas - porque nao ha combinacao de tipo x status a
multiplicar.

DOIS PISOS, NO MESMO PAR DE COR

  `label` (iniciais) e texto: piso 4,5:1 do 1.4.3.
  `icon` (glifo do tipo Icon) e nao-textual: piso 3:1 do 1.4.11.
  Os dois resolvem no mesmo hex hoje (os dois apontam para `text-primary`), mas
  cada um e medido contra o piso que e dele - nao contra o mais facil, mesma
  regra que o Tag fixou para o rotulo dele.

O QUE NAO EXISTE AQUI, E POR QUE

  Sem secao de ANEL DE FOCO: o Avatar nunca recebe foco (achado 8 da etapa 1),
  entao nao ha anel para medir. Omissao deliberada, nao esquecida.
  Sem secao de ALVO DE TOQUE: o Avatar nao e acionavel, entao o piso do 2.5.8
  (area minima de toque) nao se aplica - ele nao e um controle.

O CONTRATO DE MARCACAO E O CORACAO DESTA ETAPA

  Tres regras, todas da etapa 4 (regra 12):

    a) o involucro `.al-avatar` e SEMPRE decorativo (aria-hidden="true") OU
       carrega o sentido (role="img" + aria-label nao vazio) - nunca nenhum
       dos dois, nunca os dois ao mesmo tempo;
    b) a foto (`.al-avatar__photo`) tem `alt=""` SEMPRE, porque o nome mora no
       involucro - um alt preenchido duplicaria o anuncio;
    c) o icone (`.al-icon` dentro do Avatar) e SEMPRE decorativo na propria
       tag, porque o sentido do tipo Icon (se houver) mora no involucro, nunca
       no glifo - mesmo contrato que o icon.css ja documenta para dentro de
       qualquer acionavel.

  Isso e verificavel de verdade no HTML emitido, e e o que esta secao faz.

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
AVATAR = json.load(open(os.path.join(HERE, 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = AVATAR['resolved']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5          # 1.4.3 - as iniciais sao texto
NON_TEXT_FLOOR = 3.0      # 1.4.11 - o icone e elemento grafico

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
    v = RES[f'avatar-{name}']
    return v[theme] if isinstance(v, dict) else v


# ─────────────────────────────────────────────── contrato de marcacao
OPEN_AVATAR = re.compile(r'<(\w+)\b([^>]*\bclass="[^"]*\bal-avatar\b[^"]*"[^>]*)>')
IMG_TAG = re.compile(r'<img\b[^>]*\bclass="[^"]*\bal-avatar__photo\b[^"]*"[^>]*/?>')
SVG_TAG = re.compile(r'<svg\b[^>]*\bclass="[^"]*\bal-icon\b[^"]*"[^>]*>')
ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')


def attrs_of(tag_str):
    return dict(ATTR.findall(tag_str))


def find_matching_close(html, start, elem):
    """Acha o </elem> que fecha a tag aberta em `start`, respeitando
    aninhamento do MESMO elemento (o involucro e um <span>, e as Iniciais
    tambem sao um <span> - fechar no primeiro </span> pegaria o filho)."""
    open_re = re.compile(rf'<{elem}\b')
    close_re = re.compile(rf'</{elem}>')
    depth, pos = 1, start
    while depth > 0:
        cm = close_re.search(html, pos)
        if not cm:
            return None
        om = open_re.search(html, pos, cm.start())
        if om:
            depth += 1
            pos = om.end()
        else:
            depth -= 1
            pos = cm.end()
    return cm.start(), cm.end()


def markup_contract(path):
    """Cobra o contrato de cada .al-avatar no HTML. Ver docstring do modulo
    para as tres regras (a, b, c).

    Retorna (checked, problems). checked = None quando o HTML ainda nao emite
    o componente - o caso ate a etapa 7 montar o playground. PENDENTE, nao
    reprova: o portao passa a valer sozinho quando o HTML aparecer.
    """
    if not os.path.exists(path):
        return None, [f'{path} nao existe']

    html = open(path).read()
    for pat in (r'<style\b.*?</style>', r'<script\b.*?</script>', r'<!--.*?-->'):
        html = re.sub(pat, lambda m: '\n' * m.group(0).count('\n'), html, flags=re.S)

    checked, problems = 0, []

    for m in OPEN_AVATAR.finditer(html):
        elem, attr_str = m.group(1), m.group(2)
        attrs = attrs_of(attr_str)
        line = html.count('\n', 0, m.start()) + 1
        checked += 1

        # (a) decorativo XOR carrega o sentido - nunca nenhum, nunca os dois
        hidden = attrs.get('aria-hidden') == 'true'
        role_img = attrs.get('role') == 'img'
        label = attrs.get('aria-label', '').strip()

        if elem.lower() == 'button':
            problems.append(f'linha {line}: .al-avatar e <button> - ele e conteudo, '
                            f'nao controle; avatar clicavel embrulha um acionavel POR FORA')
        if 'role="button"' in attr_str:
            problems.append(f'linha {line}: role="button" no avatar - ele nunca e '
                            f'acionavel por conta propria')
        if re.search(r'\btabindex="0"', attr_str):
            problems.append(f'linha {line}: tabindex="0" no avatar - ele fica fora '
                            f'da ordem de tabulacao por decisao (achado 8 da etapa 1)')

        if hidden and role_img:
            problems.append(f'linha {line}: aria-hidden="true" e role="img" juntos - '
                            f'contraditorio, o leitor de tela nao sabe qual seguir')
        elif not hidden and not role_img:
            problems.append(f'linha {line}: nem aria-hidden nem role="img" - o '
                            f'contrato exige um dos dois, nunca nenhum')
        elif role_img and not label:
            problems.append(f'linha {line}: role="img" sem aria-label (ou vazio) - '
                            f'avatar sozinho sem nome acessivel')

        close = find_matching_close(html, m.end(), elem)
        inner = html[m.end():close[0]] if close else html[m.end():]

        img_m = IMG_TAG.search(inner)
        if img_m:
            img_attrs = attrs_of(img_m.group(0))
            if 'alt' not in img_attrs:
                problems.append(f'linha {line}: .al-avatar__photo sem atributo alt - '
                                f'precisa existir e ser vazio, o nome mora no involucro')
            elif img_attrs['alt'] != '':
                problems.append(f'linha {line}: .al-avatar__photo com alt="'
                                f'{img_attrs["alt"]}" - precisa ser vazio, ou o nome '
                                f'e anunciado duas vezes (regra 12, etapa 4)')

        svg_m = SVG_TAG.search(inner)
        if svg_m:
            svg_attrs = attrs_of(svg_m.group(0))
            if svg_attrs.get('aria-hidden') != 'true':
                problems.append(f'linha {line}: .al-icon dentro do avatar sem '
                                f'aria-hidden="true" - o sentido mora no involucro, '
                                f'nunca no glifo')
            if svg_attrs.get('focusable') != 'false':
                problems.append(f'linha {line}: .al-icon dentro do avatar sem '
                                f'focusable="false" - SVG inline entra na ordem de '
                                f'tabulacao sozinho em alguns navegadores')

    if checked == 0:
        return None, ['nenhum .al-avatar no HTML - o componente entra no site na '
                      'etapa 7 (playground); ate la este portao fica pendente']
    return checked, problems


def write_report(rows, checked, path_html):
    out = {
        'component': 'avatar',
        'criterion': 'WCAG 1.4.3 texto (iniciais) + 1.4.11 nao-textual (icone)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path_html, ROOT),
        'markupChecked': checked,
        'markupPending': checked is None,
        'fails': sum(1 for r in rows if not r[5]),
        'noFocusRing': 'o avatar nunca recebe foco (achado 8, etapa 1) - sem secao de anel',
        'noTouchTarget': 'o avatar nao e acionavel - o piso do 2.5.8 nao se aplica',
        'rows': [{'theme': t, 'what': w, 'fg': fg, 'bg': bg,
                  'ratio': round(ratio, 2), 'floor': floor, 'pass': ok}
                 for t, w, fg, bg, ratio, ok, floor in rows],
    }
    p = os.path.join(HERE, 'a11y.json')
    json.dump(out, open(p, 'w'), indent=2, ensure_ascii=False)
    return p


def run(path_html):
    rows, failures = [], []
    floors = {'label': TEXT_FLOOR, 'icon': NON_TEXT_FLOOR}

    for theme in THEMES:
        bg = tok('bg', theme)
        for what, floor in floors.items():
            fg = tok(what, theme)
            ratio = cr(fg, bg)
            ok = ratio >= floor
            rows.append((theme, what, fg, bg, ratio, ok, floor))
            if not ok:
                failures.append((theme, what, ratio, floor))

    checked, mk_problems = markup_contract(path_html)

    print('=' * 74)
    print('QA DE ACESSIBILIDADE DO AVATAR')
    print('=' * 74)
    print('\nCOR contra o fundo efetivo (avatar-bg, o mesmo nos tres tipos)')
    for theme, what, fg, bg, ratio, ok, floor in rows:
        mark = 'ok' if ok else 'XX'
        criterio = '1.4.3 texto' if what == 'label' else '1.4.11 nao-textual'
        print(f'  {mark} {theme:<5} {what:<6} {fg} sobre {bg}  {ratio:5.2f}  '
              f'piso {floor} ({criterio})')

    print('\nANEL DE FOCO')
    print('     n/a - o avatar nunca recebe foco (achado 8 da etapa 1)')
    print('\nALVO DE TOQUE')
    print('     n/a - o avatar nao e acionavel, 2.5.8 nao se aplica')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path_html, ROOT)}')
    if checked is None:
        for p in mk_problems:
            print(f'     pendente: {p}')
    else:
        print(f'     {checked} avatar(es) conferido(s)')
        for p in mk_problems:
            print(f'     PROBLEMA: {p}')

    print('-' * 74)
    print(f'{len(rows)} combinacoes  |  passam: {len(rows) - len(failures)}  |  '
          f'reprovam: {len(failures)}  |  excecoes: 0')

    path = write_report(rows, checked, path_html)
    print(f'{os.path.relpath(path, ROOT)} escrito')

    if failures:
        print('-' * 74)
        print(f'{len(failures)} COMBINACAO(OES) REPROVAM:')
        for theme, what, ratio, floor in failures:
            print(f'   {theme} {what}: {ratio:.2f} < {floor}')
        return 1
    if checked is not None and mk_problems:
        print('-' * 74)
        print(f'{len(mk_problems)} PROBLEMA(S) DE MARCACAO - portao reprova')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else SITE))
