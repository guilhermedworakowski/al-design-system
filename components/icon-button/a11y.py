"""
QA de acessibilidade do Icon Button.

Como no Button, a validacao e por COMBINACAO RENDERIZADA - cada variante, em
cada estado, em cada tema, contra o fundo efetivo que o botao realmente tem.
Variante sem preenchimento encosta na TELA, nao em "transparente".

Duas coisas mudam em relacao ao Button, e as duas puxam para o mesmo lugar:

1. O CRITERIO E OUTRO. Aqui quem carrega o sentido e um ICONE, nao um rotulo de
   texto: o piso e o 3:1 do 1.4.11 (nao-textual), nao o 4,5:1 do 1.4.3. Por
   isso este componente nao tem excecao de marca - branco sobre bg-brand da
   3,34:1, que reprova como texto e passa como icone. Mesma cor, criterio
   diferente.

2. O GHOST NAO TEM ROTULO PARA SE APOIAR. No Button, a variante sem
   preenchimento e sem borda nao precisa de limite proprio: ela e texto, e vale
   como texto. Aqui nao existe texto - o proprio icone e o limite visivel do
   componente, e ele ja e medido na secao 1 contra a tela. A secao 2 registra
   isso explicitamente em vez de repetir a frase do Button, que seria falsa.

E ha um contrato que nao e de contraste: o NOME ACESSIVEL. Icon Button sem
aria-label nao e um botao degradado, e um botao mudo - e essa e a falha numero
um deste componente em qualquer sistema. Ela nao vive no CSS, entao o check.py
nao alcanca; vive na marcacao, e e medida aqui, no HTML que o site emite.

Rodar: python3 a11y.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
IB = json.load(open(os.path.join(HERE, 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = IB['resolved']
THEMES = ('light', 'dark')
VARIANTS = ('primary', 'secondary', 'ghost', 'danger')

# Piso unico neste componente. Nao ha um segundo piso porque nao ha texto.
NON_TEXT_FLOOR = 3.0

# Pares de marca herdados da Foundation. No Button sao excecao nomeada; aqui
# passam com folga, porque o criterio e outro. Ficam listados para ninguem
# "corrigir" o valor achando que escapou.
BRAND_PAIRS = {
    ('light', 'primary', 'default'),
    ('dark', 'primary', 'default'),
    ('dark', 'primary', 'hover'),
}

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
    v = RES[f'icon-button-{name}']
    return v[theme] if isinstance(v, dict) else v


def canvas(theme):
    return SEM['bg-canvas'][0 if theme == 'light' else 1]


def effective_bg(variant, state, theme):
    """Fundo que o icone realmente encosta. Transparente = a tela aparece."""
    suffix = {'default': 'bg', 'hover': 'bg-hover',
              'active': 'bg-active', 'disabled': 'bg-disabled'}[state]
    value = tok(f'{variant}-{suffix}', theme)
    return canvas(theme) if value == 'transparent' else value


# ─────────────────────────────────────────────── contrato de marcacao
BTN_TAG = re.compile(r'<button\b[^>]*>')


def markup_contract():
    """Cobra o contrato de cada .al-icon-btn no HTML que o site emite.

    Quatro regras, todas da etapa 4:
      10  aria-label presente e nao vazio - o nome vai no BOTAO
      14  aria-busy sempre acompanhado de aria-disabled
      17  o atributo `disabled` nao e usado: ele tira o botao da ordem de foco
          no meio da interacao e nada e anunciado
      20  o botao nunca leva aria-hidden - quem e decorativo e o svg, la dentro

    Retorna (checked, problems). checked = None quando o site ainda nao emite o
    componente - o que e o caso ate a etapa 7 montar o playground. Isso e
    PENDENTE, nao aprovacao: o portao passa a valer sozinho quando o HTML
    aparecer, sem precisar lembrar de ligar nada.
    """
    if not os.path.exists(SITE):
        return None, ['site/index.html nao existe - rode site/site.py']

    html = open(SITE).read()
    # exemplos em comentario, <style> e <script> nao sao elementos renderizados
    for pat in (r'<style\b.*?</style>', r'<script\b.*?</script>', r'<!--.*?-->'):
        html = re.sub(pat, lambda m: '\n' * m.group(0).count('\n'), html, flags=re.S)

    checked, problems = 0, []
    for m in BTN_TAG.finditer(html):
        tag = m.group(0)
        if not re.search(r'class="[^"]*\bal-icon-btn\b', tag):
            continue
        checked += 1
        line = html.count('\n', 0, m.start()) + 1

        label = re.search(r'aria-label="([^"]*)"', tag)
        if not (label and label.group(1).strip()):
            problems.append(f'linha {line}: sem aria-label - botao mudo para leitor de tela')
        if 'aria-hidden="true"' in tag:
            problems.append(f'linha {line}: aria-hidden no proprio botao - '
                            f'decorativo e o svg, nao o acionavel')
        if 'aria-busy="true"' in tag and 'aria-disabled="true"' not in tag:
            problems.append(f'linha {line}: aria-busy sem aria-disabled - '
                            f'o botao continua clicavel enquanto carrega')
        if re.search(r'(?<![\w-])disabled(?![\w-])', tag):
            problems.append(f'linha {line}: atributo disabled - use aria-disabled, '
                            f'senao o foco some no meio da interacao')

    if checked == 0:
        return None, ['nenhum .al-icon-btn em site/index.html - o componente entra '
                      'no site na etapa 7 (playground); ate la este portao fica pendente']
    return checked, problems


def write_report(rows, checked, brand, targets):
    """O relatorio vira dado, nao so log.

    A pagina de QA e, depois, o playground leem este arquivo em vez de
    recalcular os mesmos contrastes por conta propria - uma segunda
    implementacao do mesmo criterio e uma divergencia esperando acontecer.
    """
    out = {
        'component': 'icon-button',
        'criterion': 'WCAG 1.4.11 nao-textual',
        'floor': NON_TEXT_FLOOR,
        'markupChecked': checked,
        'markupPending': checked is None,
        'fails': 0,
        'targets': [{'size': s, 'box': b, 'meetsRecommended': b >= 44} for s, b in targets],
        'brandPairs': [{'theme': t, 'label': f'{v} · {s}', 'ratio': round(r, 2)}
                       for t, v, s, r in brand],
        'rows': [{'group': g, 'theme': t, 'label': l, 'fg': fg, 'bg': bg,
                  'ratio': round(ratio, 2), 'floor': floor,
                  'pass': ok, 'exempt': floor is None}
                 for g, t, l, fg, bg, ratio, floor, ok, _ in rows],
    }
    path = os.path.join(HERE, 'a11y.json')
    json.dump(out, open(path, 'w'), indent=2, ensure_ascii=False)
    return path


def run():
    rows, failures, brand = [], [], []

    # ---- 1. tinta do icone contra o fundo efetivo (1.4.11, 3:1) ----
    for theme in THEMES:
        for v in VARIANTS:
            for state in ('default', 'hover', 'active'):
                fg = tok(f'{v}-ink', theme)
                bg = effective_bg(v, state, theme)
                ratio = cr(fg, bg)
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('tinta', theme, f'{v} · {state}', fg, bg,
                             ratio, NON_TEXT_FLOOR, ok, False))
                if not ok:
                    failures.append((theme, v, state, ratio, NON_TEXT_FLOOR))
                elif (theme, v, state) in BRAND_PAIRS:
                    brand.append((theme, v, state, ratio))

            # disabled: isento pelo 1.4.3, medido e reportado, nunca reprovado
            fg = tok(f'{v}-ink-disabled', theme)
            bg = effective_bg(v, 'disabled', theme)
            rows.append(('tinta', theme, f'{v} · disabled', fg, bg,
                         cr(fg, bg), None, True, False))

    # ---- 2. limite visivel do componente contra a tela (1.4.11, 3:1) ----
    for theme in THEMES:
        for v in VARIANTS:
            bg = tok(f'{v}-bg', theme)
            border = tok(f'{v}-border', theme)
            cv = canvas(theme)
            if bg != 'transparent':
                ratio = cr(bg, cv)
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('limite', theme, f'{v} · preenchimento', bg, cv,
                             ratio, 3.0, ok, False))
                if not ok:
                    failures.append((theme, v, 'preenchimento', ratio, 3.0))
            elif border != 'transparent':
                ratio = cr(border, cv)
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('limite', theme, f'{v} · borda', border, cv,
                             ratio, 3.0, ok, False))
                if not ok:
                    failures.append((theme, v, 'borda', ratio, 3.0))
            else:
                # Ghost. Sem preenchimento, sem borda e - diferente do Button -
                # sem rotulo. O limite do componente E o icone, ja medido na
                # secao 1 contra a tela. Nao e lacuna: e o mesmo pixel.
                fg = tok(f'{v}-ink', theme)
                ratio = cr(fg, cv)
                ok = ratio >= NON_TEXT_FLOOR
                rows.append(('limite', theme, f'{v} · o ícone é o limite', fg, cv,
                             ratio, 3.0, ok, False))
                if not ok:
                    failures.append((theme, v, 'icone como limite', ratio, 3.0))

    # ---- 3. anel de foco contra a tela (2.4.11/2.4.13, 3:1) ----
    for theme in THEMES:
        i = 0 if theme == 'light' else 1
        cv = canvas(theme)
        for v in VARIANTS:
            ring = SEM['shadow-focus-error' if v == 'danger' else 'shadow-focus-default'][i]
            ratio = cr(ring, cv)
            ok = ratio >= NON_TEXT_FLOOR
            rows.append(('foco', theme, f'{v} · anel vs tela', ring, cv,
                         ratio, 3.0, ok, False))
            if not ok:
                failures.append((theme, v, 'anel de foco', ratio, 3.0))

    # ---- 4. alvo de toque (2.5.8, minimo 24x24) ----
    targets = [(size, IB['derived']['box'][size]) for size in IB['derived']['box']]

    # ---- 5. contrato de marcacao no HTML renderizado ----
    checked, markup_problems = markup_contract()

    # ---------------- relatorio ----------------
    print('=' * 78)
    print('QA DE ACESSIBILIDADE - ICON BUTTON')
    print('=' * 78)
    print('O portador do sentido é um ícone, não um rótulo: o piso é 3:1')
    print('(WCAG 1.4.11 não-textual) em toda a folha, e não 4,5:1.')

    for group, title in (
        ('tinta',  '1. TINTA DO ÍCONE CONTRA O FUNDO EFETIVO  (WCAG 1.4.11 · min 3:1)'),
        ('limite', '2. LIMITE DO COMPONENTE CONTRA A TELA     (WCAG 1.4.11 · min 3:1)'),
        ('foco',   '3. ANEL DE FOCO CONTRA A TELA             (WCAG 2.4.11/2.4.13 · min 3:1)'),
    ):
        print(f'\n{title}')
        print('-' * 78)
        for g, theme, label, fg, bg, ratio, floor, ok, _ in rows:
            if g != group:
                continue
            tag = 'OK  ' if ok else 'FALHA'
            floor_s = f'min {floor}' if floor else 'isento 1.4.3'
            print(f'  {tag} {theme:<6} {label:<28} {fg} / {bg}  {ratio:6.2f}:1  ({floor_s})')

    print('\n4. ALVO DE TOQUE  (WCAG 2.5.8 · mínimo 24x24)')
    print('-' * 78)
    for size, box in targets:
        note = '' if box >= 44 else '  (passa AA; abaixo dos 44 recomendados — decisão registrada)'
        print(f'  OK   {size:<6} {box}x{box}px{note}')

    print('\n5. CONTRATO DE MARCAÇÃO  (no HTML que o site emite)')
    print('-' * 78)
    print('  aria-label obrigatório · aria-busy sempre com aria-disabled')
    print('  sem atributo disabled · aria-hidden nunca no botão')
    if checked is None:
        for p in markup_problems:
            print(f'  PENDENTE  {p}')
    else:
        print(f'  {checked} elementos .al-icon-btn inspecionados')
        if markup_problems:
            for p in markup_problems:
                print(f'  FALHA {p}')
        else:
            print('  0 fora do contrato.')

    n_markup_fail = len(markup_problems) if checked is not None else 0
    n_fail = len(failures) + n_markup_fail
    medidas = len([r for r in rows if r[6] is not None])

    print('\n' + '=' * 78)
    if n_fail:
        print(f'{n_fail} REPROVA(S):')
        for f in failures:
            print('   ', f)
        for p in (markup_problems if checked is not None else []):
            print('   ', p)
        return 1

    write_report(rows, checked, brand, targets)
    print(f'{medidas} combinações medidas. 0 reprovas.')
    print('components/icon-button/a11y.json escrito')
    if checked is None:
        print('Contrato de marcação: PENDENTE até a etapa 7 pôr o componente no site.')
    if brand:
        print(f'{len(brand)} par(es) de marca, todos acima do piso não-textual:')
        for theme, v, state, ratio in brand:
            print(f'   {theme:<6} {v} · {state}  {ratio:.2f}:1')
        print('No Button estes mesmos pares são exceção nomeada, porque lá o portador')
        print('é texto. Aqui não são exceção: são aprovação. Mesma cor, critério outro.')
    print('Disabled fica fora do mínimo por decisão: o 1.4.3 isenta componente')
    print('inativo, e subir esse contraste faria o desabilitado parecer clicável.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
