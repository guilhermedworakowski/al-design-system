"""
Emite a Foundation como custom properties CSS.

O truque que faz a arquitetura funcionar em CSS: custom property resolve
preguicosamente, no ponto de uso. Entao os semanticos sao declarados uma vez
por tema, e tudo que aponta para eles - inclusive o anel de foco composto -
e declarado UMA vez so, no :root, e acompanha a troca de tema sozinho.

Rodar: python3 css.py     (escreve al-foundation.css, nao redirecionar stdout)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
T = json.load(open('tokens.json'))

OUT = 'al-foundation.css'
L = []
w = L.append


def block(title):
    w('')
    w(f'  /* {title} */')


w('/* AL Design System - Foundation')
w(f' * v{T["meta"]["version"]} - {T["meta"]["license"]}')
w(' * GERADO por foundation/css.py. Nao editar a mao: rode o script.')
w(' */')
w('')
w(':root {')
w('  color-scheme: light dark;')

# ---------------- primitivas ----------------
block('primitivas de cor - a rampa crua. Nao consumir direto num componente.')
for fam, steps in T['color']['primitive'].items():
    for step, hexv in steps.items():
        w(f'  --al-color-{fam}-{step}: {hexv};')

# ---------------- semanticos (claro) ----------------
block('semanticos de cor - TEMA CLARO. E aqui que o tema e resolvido.')
for name, pair in T['color']['semantic'].items():
    if pair is None:
        continue
    w(f'  --al-{name}: {pair[0]};')

# ---------------- tipografia ----------------
block('tipografia')
w(f'  --al-font-sans: {T["type"]["family"]["sans"]};')
w(f'  --al-font-mono: {T["type"]["family"]["mono"]};')
for k, v in T['type']['weight'].items():
    w(f'  --al-font-weight-{k}: {v};')
for k, v in T['type']['size'].items():
    w(f'  --al-font-size-{k}: {v}px;')
for k, v in T['type']['leading'].items():
    w(f'  --al-line-height-{k}: {v}px;')

# ---------------- espaco, raio, borda ----------------
block('espacamento')
for k, v in T['space'].items():
    w(f'  --al-space-{k}: {v}px;')

block('raio')
for k, v in T['radius'].items():
    w(f'  --al-radius-{k}: {v}px;')

block('borda')
for k, v in T['border']['width'].items():
    w(f'  --al-border-width-{k}: {v}px;')
w(f'  --al-border-focus-offset: {T["border"]["focusOffset"]}px;')

# ---------------- elevacao ----------------
block('elevacao - TEMA CLARO')
for k, v in T['elevation'].items():
    if k.startswith('_'):
        continue
    w(f'  --al-elevation-{k}: {v["light"]};')

# ---------------- anel de foco ----------------
block('anel de foco - composto uma vez, acompanha o tema sozinho.\n     Duas camadas: respiro na cor do fundo, depois o anel na cor do foco.')
ring_total = 'calc(var(--al-border-focus-offset) + var(--al-border-width-focus))'
for kind, tok in (('default', 'shadow-focus-default'), ('error', 'shadow-focus-error')):
    w(f'  --al-focus-ring-{kind}:')
    w(f'    0 0 0 var(--al-border-focus-offset) var(--al-bg-canvas),')
    w(f'    0 0 0 {ring_total} var(--al-{tok});')
w('}')


# ---------------- tema escuro ----------------
def dark_body(indent):
    out = []
    for name, pair in T['color']['semantic'].items():
        if pair is None:
            continue
        out.append(f'{indent}--al-{name}: {pair[1]};')
    for k, v in T['elevation'].items():
        if k.startswith('_'):
            continue
        out.append(f'{indent}--al-elevation-{k}: {v["dark"]};')
    return out


w('')
w('/* TEMA ESCURO. Tres estados, nao dois: sem carimbo no root, so o')
w(' * prefers-color-scheme separa; com carimbo, a escolha explicita vence. */')
w('@media (prefers-color-scheme: dark) {')
w('  :root:not([data-theme="light"]) {')
L.extend(dark_body('    '))
w('  }')
w('}')
w('')
w(':root[data-theme="dark"] {')
L.extend(dark_body('  '))
w('}')
w('')

open(OUT, 'w').write('\n'.join(L))

n_prim = sum(len(v) for v in T['color']['primitive'].values())
n_sem = sum(1 for v in T['color']['semantic'].values() if v is not None)
print(f'{OUT} escrito')
print(f'  primitivas de cor : {n_prim}')
print(f'  semanticos de cor : {n_sem} x 2 temas')
print(f'  aneis de foco     : 2 (compostos, resolvem sozinhos no tema)')
print(f'  bytes             : {os.path.getsize(OUT)}')
