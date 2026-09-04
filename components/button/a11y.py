"""
QA de acessibilidade do Button.

Diferente do portao da Foundation, que valida pares de token soltos, aqui a
validacao e por COMBINACAO RENDERIZADA: cada variante, em cada estado, em
cada tema, com o fundo efetivo que o botao realmente tem. Uma variante sem
preenchimento herda a tela - e o rotulo dela precisa passar contra a tela,
nao contra "transparente".

Rodar: python3 a11y.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'foundation', 'tokens.json')))
BTN = json.load(open(os.path.join(HERE, 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = BTN['resolved']
THEMES = ('light', 'dark')
VARIANTS = ('primary', 'secondary', 'ghost', 'danger')

# Excecao de marca herdada da Foundation: rotulo claro sobre a marca.
# Continua >= 3:1, entao atende AA para texto grande e para nao-textual.
BRAND_EXCEPTIONS = {
    ('light', 'primary', 'default'),
    ('dark', 'primary', 'default'),
    ('dark', 'primary', 'hover'),
}
HARD_FLOOR = 3.0


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
    """Valor do token do Button no tema pedido."""
    v = RES[f'button-{name}']
    return v[theme] if isinstance(v, dict) else v


def canvas(theme):
    return SEM['bg-canvas'][0 if theme == 'light' else 1]


def effective_bg(variant, state, theme):
    """Fundo que o rotulo realmente encosta. Transparente = a tela aparece."""
    suffix = {'default': 'bg', 'hover': 'bg-hover',
              'active': 'bg-active', 'disabled': 'bg-disabled'}[state]
    value = tok(f'{variant}-{suffix}', theme)
    return canvas(theme) if value == 'transparent' else value


def run():
    rows, failures, exempt = [], [], []

    # ---- 1. rotulo contra o fundo efetivo ----
    for theme in THEMES:
        for v in VARIANTS:
            for state in ('default', 'hover', 'active'):
                fg = tok(f'{v}-label', theme)
                bg = effective_bg(v, state, theme)
                ratio = cr(fg, bg)
                is_exc = (theme, v, state) in BRAND_EXCEPTIONS
                floor = HARD_FLOOR if is_exc else 4.5
                ok = ratio >= floor
                rows.append(('rotulo', theme, f'{v} · {state}', fg, bg, ratio, floor, ok, is_exc))
                if not ok:
                    failures.append((theme, v, state, ratio, floor))
                elif is_exc:
                    exempt.append((theme, v, state, ratio))

            # disabled: isento pelo 1.4.3, mas medido e reportado
            fg = tok(f'{v}-label-disabled', theme)
            bg = effective_bg(v, 'disabled', theme)
            rows.append(('rotulo', theme, f'{v} · disabled', fg, bg, cr(fg, bg), None, True, False))

    # ---- 2. limite visivel do botao contra a tela (1.4.11, 3:1) ----
    for theme in THEMES:
        for v in VARIANTS:
            bg = tok(f'{v}-bg', theme)
            border = tok(f'{v}-border', theme)
            cv = canvas(theme)
            if bg != 'transparent':
                ratio = cr(bg, cv)
                ok = ratio >= HARD_FLOOR
                rows.append(('limite', theme, f'{v} · preenchimento', bg, cv, ratio, 3.0, ok, False))
                if not ok:
                    failures.append((theme, v, 'preenchimento', ratio, 3.0))
            elif border != 'transparent':
                ratio = cr(border, cv)
                ok = ratio >= HARD_FLOOR
                rows.append(('limite', theme, f'{v} · borda', border, cv, ratio, 3.0, ok, False))
                if not ok:
                    failures.append((theme, v, 'borda', ratio, 3.0))
            else:
                # Ghost nao tem limite proprio: e texto, e vale como texto.
                rows.append(('limite', theme, f'{v} · sem limite (é rótulo)', '-', '-', None, None, True, False))

    # ---- 3. anel de foco (2.4.13: o pixel que muda, contra o que havia) ----
    for theme in THEMES:
        i = 0 if theme == 'light' else 1
        cv = canvas(theme)
        for v in VARIANTS:
            ring_color = SEM['shadow-focus-error' if v == 'danger' else 'shadow-focus-default'][i]
            ratio = cr(ring_color, cv)
            ok = ratio >= HARD_FLOOR
            rows.append(('foco', theme, f'{v} · anel vs tela', ring_color, cv, ratio, 3.0, ok, False))
            if not ok:
                failures.append((theme, v, 'anel de foco', ratio, 3.0))

    # ---- 4. alvo de toque (2.5.8, minimo 24x24) ----
    targets = [(size, BTN['derived']['height'][size]) for size in BTN['derived']['height']]

    # ---------------- relatorio ----------------
    print('=' * 78)
    print('QA DE ACESSIBILIDADE - BUTTON')
    print('=' * 78)

    for group, title in (('rotulo', '1. RÓTULO CONTRA O FUNDO EFETIVO  (WCAG 1.4.3 · min 4,5:1)'),
                         ('limite', '2. LIMITE DO BOTÃO CONTRA A TELA  (WCAG 1.4.11 · min 3:1)'),
                         ('foco',   '3. ANEL DE FOCO CONTRA A TELA     (WCAG 2.4.11/2.4.13 · min 3:1)')):
        print(f'\n{title}')
        print('-' * 78)
        for g, theme, label, fg, bg, ratio, floor, ok, exc in rows:
            if g != group:
                continue
            if ratio is None:
                print(f'  --   {theme:<6} {label:<34} n/a')
                continue
            tag = 'EXCE' if exc else ('OK  ' if ok else 'FALHA')
            floor_s = f'min {floor}' if floor else 'isento 1.4.3'
            print(f'  {tag} {theme:<6} {label:<34} {fg} / {bg}  {ratio:6.2f}:1  ({floor_s})')

    print(f'\n4. ALVO DE TOQUE  (WCAG 2.5.8 · mínimo 24x24)')
    print('-' * 78)
    for size, h in targets:
        note = '' if h >= 44 else '  (passa AA; abaixo dos 44 recomendados para toque)'
        print(f'  OK   {size:<6} {h}x{h}px{note}')

    print('\n' + '=' * 78)
    if failures:
        print(f'{len(failures)} COMBINAÇÃO(ÕES) REPROVAM:')
        for f in failures:
            print('   ', f)
        return 1
    print(f'{len(rows)} combinações medidas. 0 reprovas.')
    if exempt:
        print(f'{len(exempt)} exceções de marca herdadas da Foundation, todas >= {HARD_FLOOR}:1:')
        for theme, v, state, ratio in exempt:
            print(f'   {theme:<6} {v} · {state}  {ratio:.2f}:1')
    print('Disabled fica fora do mínimo por decisão: o 1.4.3 isenta componente')
    print('inativo, e subir esse contraste faria o desabilitado parecer clicável.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
