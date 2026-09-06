"""
QA de acessibilidade do Icon.

Como no Button, a validacao e por COMBINACAO RENDERIZADA, nao por par de token
solto. Mas o Icon tem duas particularidades que mudam o que se mede:

1. O criterio e outro. Icone nao e texto: o piso e o 3:1 do 1.4.11 (nao-textual),
   nao o 4,5:1 do 1.4.3. Um par que reprovaria como rotulo pode passar como
   icone - e o contrario nunca acontece.

2. A cor padrao nao e um token, e `currentColor`. Entao existem DUAS familias de
   combinacao, e as duas precisam ser medidas:
     - tinta explicita  -> os quatro `--al-icon-ink-*` contra as superficies
                           onde cada um faz sentido;
     - tinta herdada    -> o icone dentro do Button, onde ele veste a cor do
                           rotulo. Aqui vale a mesma logica da variante sem
                           preenchimento: Ghost e Secondary nao tem fundo, entao
                           o icone encosta na TELA, nao em "transparente".

E ha um terceiro portao que nao e de contraste: o CONTRATO DE MARCACAO. A regra
de icone decorativo versus icone com sentido nao virou documento por decisao do
Guilherme - icone do AL vive dentro de acionavel e quem carrega o sentido e o
rotulo. Entao ela e verificada aqui, no HTML que o site realmente emite, em vez
de ser lida numa pagina que ninguem abre.

Rodar: python3 a11y.py   (exige site/index.html gerado)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
ICON = json.load(open(os.path.join(HERE, 'tokens.json')))
BTN = json.load(open(os.path.join(ROOT, 'components', 'button', 'tokens.json')))
MANIFEST = json.load(open(os.path.join(HERE, 'icons.json')))

SEM = FOUND['color']['semantic']
THEMES = ('light', 'dark')
NON_TEXT_FLOOR = 3.0

SITE = os.path.join(ROOT, 'site', 'index.html')

# Onde cada tinta explicita faz sentido. Medir `on-brand` contra a tela seria
# inventar um cenario que o design system nao produz.
INK_SURFACES = {
    'default':  ['bg-canvas', 'bg-surface', 'bg-subtle'],
    'on-brand': ['bg-brand', 'bg-brand-hover', 'bg-brand-active'],
    'on-solid': ['bg-danger', 'bg-danger-hover', 'bg-danger-active'],
    'disabled': ['bg-canvas', 'bg-disabled'],
}

# Excecao de marca herdada da Foundation. Branco sobre a marca da 3,34:1 - abaixo
# do texto normal, acima do piso nao-textual. Para icone isso NAO e excecao: e
# aprovacao com folga. Fica nomeado para ninguem "corrigir" o valor.
BRAND_PAIRS = {('light', 'on-brand', 'bg-brand'), ('dark', 'on-brand', 'bg-brand')}

VARIANTS = ('primary', 'secondary', 'ghost', 'danger')


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


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def ink(mode, theme):
    return ICON['resolved'][f'icon-ink-{mode}'][theme]


def btn(name, theme):
    v = BTN['resolved'][f'button-{name}']
    return v[theme] if isinstance(v, dict) else v


def effective_bg(variant, state, theme):
    """O fundo que o icone realmente encosta. Transparente = a tela aparece."""
    suffix = {'default': 'bg', 'hover': 'bg-hover', 'active': 'bg-active'}[state]
    value = btn(f'{variant}-{suffix}', theme)
    return sem('bg-canvas', theme) if value == 'transparent' else value


# ─────────────────────────────────────────────── contrato de marcacao
SVG_TAG = re.compile(r'<svg\b[^>]*>')


def markup_contract():
    """Le o HTML que o site emite e cobra o contrato de cada .al-icon.

    Decorativo  -> aria-hidden="true" E focusable="false"
    Com sentido -> role="img" E aria-label nao vazio
    E nunca os dois ao mesmo tempo: um icone escondido do leitor de tela que
    tambem carrega rotulo e uma contradicao, e o rotulo perde.
    """
    if not os.path.exists(SITE):
        return None, ['site/index.html nao existe - rode site/site.py antes deste portao']

    html = open(SITE).read()

    # Só marcação. <style> e <script> carregam exemplos em comentário - o
    # cabeçalho do proprio icon.css tem dois - e um exemplo em comentario nao e
    # um elemento renderizado. Medir ali seria reprovar documentacao.
    html = re.sub(r'<style\b.*?</style>', lambda m: '\n' * m.group(0).count('\n'),
                  html, flags=re.S)
    html = re.sub(r'<script\b.*?</script>', lambda m: '\n' * m.group(0).count('\n'),
                  html, flags=re.S)
    html = re.sub(r'<!--.*?-->', lambda m: '\n' * m.group(0).count('\n'), html, flags=re.S)

    checked, problems = 0, []

    for m in SVG_TAG.finditer(html):
        tag = m.group(0)
        if not re.search(r'class="[^"]*\bal-icon\b', tag):
            continue
        checked += 1
        line = html.count('\n', 0, m.start()) + 1

        hidden = 'aria-hidden="true"' in tag
        focusable_off = 'focusable="false"' in tag
        role_img = 'role="img"' in tag
        label = re.search(r'aria-label="([^"]*)"', tag)

        if hidden and (role_img or (label and label.group(1).strip())):
            problems.append(f'linha {line}: aria-hidden junto de rotulo - o rotulo nunca sera lido')
        elif hidden:
            if not focusable_off:
                problems.append(f'linha {line}: decorativo sem focusable="false" - '
                                f'entra na ordem de tabulacao em alguns navegadores')
        elif role_img:
            if not (label and label.group(1).strip()):
                problems.append(f'linha {line}: role="img" sem aria-label - '
                                f'anunciado como imagem sem nome')
        else:
            problems.append(f'linha {line}: sem contrato - nem decorativo '
                            f'(aria-hidden) nem com sentido (role="img")')

    return checked, problems


def write_report(rows, checked, failures, notes):
    """O relatorio vira dado, nao so log.

    O site le este arquivo para montar a aba de acessibilidade. Sem isso a
    pagina teria que recalcular os mesmos contrastes por conta propria - e uma
    segunda implementacao do mesmo criterio e uma divergencia esperando
    acontecer.
    """
    out = {
        'component': 'icon',
        'criterion': 'WCAG 1.4.11 nao-textual',
        'floor': NON_TEXT_FLOOR,
        'markupChecked': checked,
        'fails': len(failures),
        'brandPairs': [{'theme': t, 'label': l, 'ratio': round(r, 2)} for t, l, r in notes],
        'rows': [{'group': g, 'theme': t, 'label': l, 'fg': fg, 'bg': bg,
                  'ratio': round(ratio, 2), 'floor': floor, 'pass': ok, 'exempt': floor is None}
                 for g, t, l, fg, bg, ratio, floor, ok in rows],
    }
    path = os.path.join(HERE, 'a11y.json')
    json.dump(out, open(path, 'w'), indent=2, ensure_ascii=False)
    return path


def run():
    rows, failures, notes = [], [], []

    # ---- 1. tinta explicita contra a superficie (1.4.11, 3:1) ----
    for theme in THEMES:
        for mode, surfaces in INK_SURFACES.items():
            for surface in surfaces:
                fg, bg = ink(mode, theme), sem(surface, theme)
                ratio = cr(fg, bg)
                if mode == 'disabled':
                    # 1.4.3 e 1.4.11 isentam componente inativo. Medido e
                    # reportado, nunca reprovado - subir isso faz o
                    # desabilitado parecer ativo.
                    rows.append(('tinta', theme, f'{mode} · {surface}', fg, bg, ratio, None, True))
                    continue
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('tinta', theme, f'{mode} · {surface}', fg, bg,
                             ratio, NON_TEXT_FLOOR, ok))
                if not ok:
                    failures.append((theme, f'{mode} sobre {surface}', ratio))
                elif (theme, mode, surface) in BRAND_PAIRS:
                    notes.append((theme, f'{mode} sobre {surface}', ratio))

    # ---- 2. tinta herdada dentro do Button (currentColor) ----
    for theme in THEMES:
        for v in VARIANTS:
            for state in ('default', 'hover', 'active'):
                fg = btn(f'{v}-label', theme)          # o icone veste esta cor
                bg = effective_bg(v, state, theme)
                ratio = cr(fg, bg)
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('herda', theme, f'{v} · {state}', fg, bg,
                             ratio, NON_TEXT_FLOOR, ok))
                if not ok:
                    failures.append((theme, f'{v} {state} (herdado)', ratio))

    # ---- 3. contrato de marcacao no HTML renderizado ----
    checked, markup_problems = markup_contract()

    # ---------------- relatorio ----------------
    print('=' * 78)
    print('QA DE ACESSIBILIDADE - ICON')
    print('=' * 78)
    print('Icone nao e texto: o piso e 3:1 (WCAG 1.4.11 nao-textual), nao 4,5:1.')

    titles = {
        'tinta': '1. TINTA EXPLÍCITA CONTRA A SUPERFÍCIE   (WCAG 1.4.11 · min 3:1)',
        'herda': '2. TINTA HERDADA DENTRO DO BUTTON        (currentColor · min 3:1)',
    }
    for group in ('tinta', 'herda'):
        print(f'\n{titles[group]}')
        print('-' * 78)
        for g, theme, label, fg, bg, ratio, floor, ok in rows:
            if g != group:
                continue
            if floor is None:
                tag = 'ISENTO'
                extra = '(componente inativo)'
            else:
                tag = 'OK  ' if ok else 'FALHA'
                extra = f'(min {floor})'
            print(f'  {tag} {theme:<6} {label:<24} {fg} / {bg}  {ratio:5.2f}:1  {extra}')

    print(f'\n3. CONTRATO DE MARCAÇÃO                  (no HTML que o site emite)')
    print('-' * 78)
    if checked is None:
        for p in markup_problems:
            print(f'  FALHA {p}')
    else:
        print(f'  {checked} elementos .al-icon inspecionados em site/index.html')
        print(f'  decorativo  -> aria-hidden="true" + focusable="false"')
        print(f'  com sentido -> role="img" + aria-label')
        if markup_problems:
            for p in markup_problems:
                print(f'  FALHA {p}')
        else:
            print(f'  0 fora do contrato.')

    print(f'\n4. FAMÍLIA DO DESENHO')
    print('-' * 78)
    print(f'  {MANIFEST["count"]} ícones · grid {MANIFEST["grid"]} · traço {MANIFEST["strokeWidth"]} '
          f'· {MANIFEST["family"]} · {MANIFEST["license"]}')
    print(f'  Menor caixa em uso: {ICON["resolved"]["icon-box-16"]}px. O WCAG não define tamanho')
    print(f'  mínimo para ícone; o 2.5.8 mede o ALVO, e alvo é do acionável que o contém.')

    n_fail = len(failures) + (len(markup_problems) if markup_problems else 0)
    total = len([r for r in rows if r[6] is not None]) + (checked or 0)

    print('\n' + '=' * 78)
    print(f'{total} verificações. {n_fail} reprovas.')
    if notes:
        print(f'{len(notes)} par(es) de marca, todos acima do piso não-textual:')
        for theme, label, ratio in notes:
            print(f'   {theme:<6} {label:<28} {ratio:.2f}:1')
        print('Branco sobre a marca reprova como texto normal e passa como ícone —')
        print('é a mesma cor, critério diferente. Não é exceção aqui, é aprovação.')
    print('Disabled fica fora do mínimo por decisão: o WCAG isenta componente')
    print('inativo, e subir esse contraste faria o desabilitado parecer clicável.')

    if failures:
        print('\nREPROVAS:')
        for theme, label, ratio in failures:
            print(f'   {theme:<6} {label:<28} {ratio:.2f}:1  (min {NON_TEXT_FLOOR})')
    if markup_problems:
        print('\nCONTRATO DE MARCAÇÃO:')
        for p in markup_problems:
            print(f'   {p}')

    if not n_fail:
        write_report(rows, checked, failures, notes)
        print('\ncomponents/icon/a11y.json escrito')

    return 1 if n_fail else 0


if __name__ == '__main__':
    sys.exit(run())
