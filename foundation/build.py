from color import *
import json, sys

P = build()   # primitivas
def c(fam, step): return P[fam][step]

# ---------------- camada semantica ----------------
# cada entrada: (light, dark)
SEM = {
  # superficie
  'bg/canvas':          ('#FFFFFF',      c('neutral',950)),
  'bg/surface':         (c('neutral',50),  c('neutral',900)),
  'bg/surface-raised':  ('#FFFFFF',      c('neutral',800)),
  'bg/subtle':          (c('neutral',100), c('neutral',800)),
  'bg/hover':           (c('neutral',100), c('neutral',800)),
  'bg/active':          (c('neutral',200), c('neutral',700)),
  'bg/disabled':        (c('neutral',200), c('neutral',800)),
  'bg/inverse':         (c('neutral',900), c('neutral',50)),
  # marca
  'bg/brand':           (c('orange',500),  c('orange',500)),
  'bg/brand-hover':     (c('orange',600),  BRAND_HOVER),
  'bg/brand-active':    (c('orange',700),  c('orange',600)),
  'bg/brand-subtle':    (c('orange',100),  c('orange',950)),
  'bg/brand-strong':    (c('orange',700),  c('orange',700)),
  # feedback solido
  'bg/danger':          (c('red',700),     c('red',500)),
  'bg/danger-hover':    (c('red',800),     c('red',400)),
  'bg/danger-active':   (c('red',900),     c('red',300)),
  'bg/danger-subtle':   (c('red',100),     c('red',950)),
  'bg/success':         (c('green',700),   c('green',500)),
  'bg/success-hover':   (c('green',800),   c('green',400)),
  'bg/success-subtle':  (c('green',100),   c('green',950)),
  'bg/warning':         (c('amber',700),   c('amber',400)),
  'bg/warning-hover':   (c('amber',800),   c('amber',300)),
  'bg/warning-subtle':  (c('amber',100),   c('amber',950)),
  'bg/info':            (c('blue',700),    c('blue',500)),
  'bg/info-hover':      (c('blue',800),    c('blue',400)),
  'bg/info-subtle':     (c('blue',100),    c('blue',950)),
  # texto
  'text/primary':       (c('neutral',900), c('neutral',50)),
  'text/secondary':     (c('neutral',600), c('neutral',400)),
  'text/placeholder':   (c('neutral',600), c('neutral',400)),
  'text/disabled':      (c('neutral',400), c('neutral',600)),
  'text/inverse':       (c('neutral',50),  c('neutral',900)),
  'text/on-brand':      ('#FFFFFF',        '#FFFFFF'),
  'text/on-solid':      ('#FFFFFF',      c('neutral',950)),
  'text/brand':         (c('orange',700),  c('orange',400)),
  'text/danger':        (c('red',700),     c('red',400)),
  'text/success':       (c('green',700),   c('green',400)),
  'text/warning':       (c('amber',700),   c('amber',300)),
  'text/info':          (c('blue',700),    c('blue',400)),
  # borda
  'border/subtle':      (c('neutral',200), c('neutral',800)),
  'border/default':     (c('neutral',300), c('neutral',700)),
  'border/strong':      (c('neutral',600), c('neutral',600)),
  'border/brand':       (c('orange',500),  c('orange',500)),
  'border/focus':       (c('orange',500),  c('orange',400)),
  'border/danger':      (c('red',600),     c('red',500)),
  'border/success':     (c('green',600),   c('green',500)),
  'border/warning':     (c('amber',600),   c('amber',400)),
  'border/info':        (c('blue',600),    c('blue',500)),
}

# ---------------- pares de contraste obrigatorios ----------------
# (foreground, background, minimo, rotulo)
PAIRS = [
  ('text/primary',   'bg/canvas',        4.5, 'texto principal na tela'),
  ('text/primary',   'bg/surface',       4.5, 'texto principal em superficie'),
  ('text/primary',   'bg/surface-raised',4.5, 'texto principal em card elevado'),
  ('text/primary',   'bg/subtle',        4.5, 'texto principal em fundo sutil'),
  ('text/secondary', 'bg/canvas',        4.5, 'texto secundario na tela'),
  ('text/secondary', 'bg/surface',       4.5, 'texto secundario em superficie'),
  ('text/placeholder','bg/canvas',       4.5, 'placeholder de input'),
  ('text/inverse',   'bg/inverse',       4.5, 'texto em fundo invertido'),
  ('text/on-brand',  'bg/brand',         4.5, 'label do botao primario'),
  ('text/on-brand',  'bg/brand-hover',   4.5, 'label do botao primario em hover'),
  ('text/on-brand',  'bg/brand-active',  4.5, 'label do botao primario pressionado'),
  ('text/on-solid',  'bg/danger-active', 4.5, 'label do botao destrutivo pressionado'),
  ('bg/brand-hover', 'bg/canvas',        3.0, 'botao primario em hover contra a tela'),
  ('bg/brand-hover', 'bg/surface',       3.0, 'botao primario em hover em superficie'),
  ('bg/brand',       'bg/surface',       3.0, 'botao primario em superficie'),
  ('text/on-solid',  'bg/danger',        4.5, 'label do botao destrutivo'),
  ('text/on-solid',  'bg/success',       4.5, 'label do solido de sucesso'),
  ('text/on-solid',  'bg/warning',       4.5, 'label do solido de alerta'),
  ('text/on-solid',  'bg/info',          4.5, 'label do solido de info'),
  ('text/brand',     'bg/canvas',        4.5, 'link/texto de marca'),
  ('text/brand',     'bg/brand-subtle',  4.5, 'texto de marca em fundo tonalizado'),
  ('text/danger',    'bg/canvas',        4.5, 'texto de erro'),
  ('text/danger',    'bg/danger-subtle', 4.5, 'texto de erro em banner'),
  ('text/success',   'bg/canvas',        4.5, 'texto de sucesso'),
  ('text/success',   'bg/success-subtle',4.5, 'texto de sucesso em banner'),
  ('text/warning',   'bg/canvas',        4.5, 'texto de alerta'),
  ('text/warning',   'bg/warning-subtle',4.5, 'texto de alerta em banner'),
  ('text/info',      'bg/canvas',        4.5, 'texto de info'),
  ('text/info',      'bg/info-subtle',   4.5, 'texto de info em banner'),
  # elementos nao-textuais: 3:1 (WCAG 1.4.11)
  ('border/strong',  'bg/canvas',        3.0, 'borda de input na tela'),
  ('border/strong',  'bg/surface',       3.0, 'borda de input em superficie'),
  ('border/focus',   'bg/canvas',        3.0, 'anel de foco na tela'),
  ('border/focus',   'bg/surface',       3.0, 'anel de foco em superficie'),
  ('border/danger',  'bg/canvas',        3.0, 'borda de input em erro'),
  ('border/brand',   'bg/canvas',        3.0, 'borda de marca'),
  ('bg/brand',       'bg/canvas',        3.0, 'botao primario contra a tela'),
]

# excecoes autorizadas pela marca: label claro sobre a marca. Todas continuam >= 3:1,
# entao atendem AA para texto grande e para elemento nao-textual — nunca abaixo disso.
EXCEPTIONS = {
  ('light', 'text/on-brand', 'bg/brand'),
  ('dark',  'text/on-brand', 'bg/brand'),
  ('dark',  'text/on-brand', 'bg/brand-hover'),
}
HARD_FLOOR = 3.0

def run():
    fails, rows = [], []
    for theme_i, theme in enumerate(('light','dark')):
        for fg, bg, mn, label in PAIRS:
            a, b = SEM[fg][theme_i], SEM[bg][theme_i]
            v = cr(a, b)
            exc = (theme, fg, bg) in EXCEPTIONS
            ok = (v >= HARD_FLOOR) if exc else (v >= mn)
            rows.append((theme, label, fg, bg, a, b, v, (HARD_FLOOR if exc else mn), ok, exc))
            if not ok: fails.append((theme, label, fg, bg, a, b, v, mn))
    w = max(len(r[1]) for r in rows)
    for theme in ('light','dark'):
        print(f"\n{'='*78}\nTEMA {theme.upper()}\n{'='*78}")
        for t, label, fg, bg, a, b, v, mn, ok, exc in rows:
            if t != theme: continue
            tag = 'EXCE' if exc else ('OK  ' if ok else 'FALHA')
            print(f"  {tag} {label:<{w}}  {a} / {b}  {v:6.2f}:1  (min {mn})")
    print(f"\n{'-'*78}")
    if fails:
        print(f"{len(fails)} PAR(ES) REPROVAM:")
        for f in fails: print("   ", f)
        return 1
    n_exc = sum(1 for r in rows if r[9])
    print(f"{len(rows) - n_exc} pares passam em AA pleno.")
    print(f"{n_exc} excecoes de marca, todas >= {HARD_FLOOR}:1 (AA para texto grande e nao-textual):")
    for r in rows:
        if r[9]: print(f"   {r[0]:<6} {r[1]:<38} {r[6]:.2f}:1")
    return 0

if __name__ == '__main__':
    sys.exit(run())
