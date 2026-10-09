from color import *
import json, sys

P = build()   # primitives
def c(fam, step): return P[fam][step]

# ---------------- semantic layer ----------------
# naming: group-role-variant, always separated by hyphens.
# each entry: (light, dark)
SEM = {
  # surface
  'bg-canvas':          ('#FFFFFF',        c('neutral',950)),
  'bg-surface':         (c('neutral',50),  c('neutral',900)),
  'bg-surface-raised':  ('#FFFFFF',        c('neutral',800)),
  'bg-subtle':          (c('neutral',100), c('neutral',800)),
  'bg-hover':           (c('neutral',100), c('neutral',800)),
  'bg-active':          (c('neutral',200), c('neutral',700)),
  'bg-disabled':        (c('neutral',200), c('neutral',800)),
  'bg-inverse':         (c('neutral',900), c('neutral',50)),
  # hover and pressed ON a raised surface (Accordion; also serves the Tab inside
  # a card). bg-hover was calibrated for the canvas: in dark it is the same 800
  # as bg-surface-raised and the hover disappeared (1.00:1). Here dark goes up
  # one step; in light the raised surface is white and the value is the same as
  # bg-hover / bg-active. Decided 2026-10-07.
  'bg-hover-raised':    (c('neutral',100), c('neutral',700)),
  'bg-active-raised':   (c('neutral',200), c('neutral',600)),
  # a piece that slides along a track (Switch; also serves a Slider). Dark is
  # the mirror of light on the ladder, as in text-disabled and border-default.
  # It is not in PAIRS: contrast against the track is a component combination,
  # and the Switch declares the exception in its own gate (decided 2026-09-25).
  'bg-thumb':           (c('neutral',400), c('neutral',600)),
  'bg-thumb-disabled':  (c('neutral',300), c('neutral',700)),
  # the dimmed background behind a modal layer (Modal; also serves the Drawer).
  # It is the only semantic with transparency: #RRGGBBAA, 56% in light and 64%
  # in dark. It stays out of PAIRS because its contrast only exists composited
  # over the page; the component gate measures it (components/modal/tokens.py).
  # In dark, raising the opacity barely changes anything (72% = 1.88:1) - the
  # background is already almost black. Decided 2026-10-07.
  'bg-scrim':           ('#181818' + '8F', '#000000' + 'A3'),
  # brand
  'bg-brand':           (c('orange',500),  c('orange',500)),
  'bg-brand-hover':     (c('orange',600),  BRAND_HOVER),
  'bg-brand-active':    (c('orange',700),  c('orange',600)),
  'bg-brand-subtle':    (c('orange',100),  c('orange',950)),
  'bg-brand-strong':    (c('orange',700),  c('orange',700)),
  # solid feedback
  'bg-danger':          (c('red',700),     c('red',500)),
  'bg-danger-hover':    (c('red',800),     c('red',400)),
  'bg-danger-active':   (c('red',900),     c('red',300)),
  'bg-danger-subtle':   (c('red',100),     c('red',950)),
  'bg-success':         (c('green',700),   c('green',500)),
  'bg-success-hover':   (c('green',800),   c('green',400)),
  'bg-success-subtle':  (c('green',100),   c('green',950)),
  'bg-warning':         (c('amber',700),   c('amber',400)),
  'bg-warning-hover':   (c('amber',800),   c('amber',300)),
  'bg-warning-subtle':  (c('amber',100),   c('amber',950)),
  'bg-info':            (c('blue',700),    c('blue',500)),
  'bg-info-hover':      (c('blue',800),    c('blue',400)),
  'bg-info-subtle':     (c('blue',100),    c('blue',950)),
  # text
  'text-primary':       (c('neutral',900), c('neutral',50)),
  'text-secondary':     (c('neutral',600), c('neutral',400)),
  'text-placeholder':   (c('neutral',600), c('neutral',400)),
  'text-disabled':      (c('neutral',400), c('neutral',600)),
  'text-inverse':       (c('neutral',50),  c('neutral',900)),
  'text-on-brand':      ('#FFFFFF',        '#FFFFFF'),
  'text-on-solid':      ('#FFFFFF',        c('neutral',950)),
  'text-brand':         (c('orange',700),  c('orange',400)),
  'text-danger':        (c('red',700),     c('red',400)),
  'text-success':       (c('green',700),   c('green',400)),
  'text-warning':       (c('amber',700),   c('amber',300)),
  'text-info':          (c('blue',700),    c('blue',400)),
  # border
  'border-subtle':      (c('neutral',200), c('neutral',800)),
  'border-default':     (c('neutral',300), c('neutral',700)),
  # the only token that used the same step in both themes. With the achromatic
  # neutral the 600 got darker and stopped separating from the dark surface
  # (2.98:1), so dark goes up to the 500 - a border gets lighter on a dark
  # background, which is the correct behavior anyway.
  'border-strong':      (c('neutral',600), c('neutral',500)),
  'border-brand':       (c('orange',500),  c('orange',500)),
  'border-focus':       (c('orange',500),  c('orange',400)),
  'border-danger':      (c('red',600),     c('red',500)),
  'border-success':     (c('green',600),   c('green',500)),
  'border-warning':     (c('amber',600),   c('amber',400)),
  'border-info':        (c('blue',600),    c('blue',500)),
  # focus ring color. It lives here, and not with elevation, because it is a
  # content color: it has to pass the contrast gate like any other.
  # The composite shadow that consumes these two is in export.py -> focusRing.
  'shadow-focus-default': (c('orange',500), c('orange',400)),
  'shadow-focus-error':   (c('red',700),    c('red',400)),
}

# ---------------- required contrast pairs ----------------
# (foreground, background, minimum, label)
PAIRS = [
  ('text-primary',    'bg-canvas',         4.5, 'primary text on the canvas'),
  ('text-primary',    'bg-surface',        4.5, 'primary text on the surface'),
  ('text-primary',    'bg-surface-raised', 4.5, 'primary text on a raised card'),
  ('text-primary',    'bg-subtle',         4.5, 'primary text on a subtle background'),
  ('text-primary',    'bg-hover-raised',   4.5, 'primary text on hover over raised'),
  ('text-primary',    'bg-active-raised',  4.5, 'primary text pressed over raised'),
  ('text-secondary',  'bg-canvas',         4.5, 'secondary text on the canvas'),
  ('text-secondary',  'bg-surface',        4.5, 'secondary text on the surface'),
  ('text-placeholder','bg-canvas',         4.5, 'input placeholder'),
  ('text-inverse',    'bg-inverse',        4.5, 'text on an inverse background'),
  ('text-on-brand',   'bg-brand',          4.5, 'light text on the brand'),
  ('text-on-brand',   'bg-brand-hover',    4.5, 'light text on the brand on hover'),
  ('text-on-brand',   'bg-brand-active',   4.5, 'light text on the pressed brand'),
  ('text-on-solid',   'bg-danger-active',  4.5, 'text on the pressed destructive solid'),
  ('bg-brand-hover',  'bg-canvas',         3.0, 'brand on hover against the canvas'),
  ('bg-brand-hover',  'bg-surface',        3.0, 'brand on hover on the surface'),
  ('bg-brand',        'bg-surface',        3.0, 'brand fill on the surface'),
  ('text-on-solid',   'bg-danger',         4.5, 'text on the destructive solid'),
  ('text-on-solid',   'bg-success',        4.5, 'text on the success solid'),
  ('text-on-solid',   'bg-warning',        4.5, 'text on the warning solid'),
  ('text-on-solid',   'bg-info',           4.5, 'text on the info solid'),
  ('text-brand',      'bg-canvas',         4.5, 'brand link/text'),
  ('text-brand',      'bg-brand-subtle',   4.5, 'brand text on a tinted background'),
  ('text-danger',     'bg-canvas',         4.5, 'error text'),
  ('text-danger',     'bg-danger-subtle',  4.5, 'error text in a banner'),
  ('text-success',    'bg-canvas',         4.5, 'success text'),
  ('text-success',    'bg-success-subtle', 4.5, 'success text in a banner'),
  ('text-warning',    'bg-canvas',         4.5, 'warning text'),
  ('text-warning',    'bg-warning-subtle', 4.5, 'warning text in a banner'),
  ('text-info',       'bg-canvas',         4.5, 'info text'),
  ('text-info',       'bg-info-subtle',    4.5, 'info text in a banner'),
  # non-text elements: 3:1 (WCAG 1.4.11)
  ('border-strong',   'bg-canvas',         3.0, 'input border on the canvas'),
  ('border-strong',   'bg-surface',        3.0, 'input border on the surface'),
  ('border-focus',    'bg-canvas',         3.0, 'focus ring on the canvas'),
  ('border-focus',    'bg-surface',        3.0, 'focus ring on the surface'),
  ('border-danger',   'bg-canvas',         3.0, 'input border in error'),
  ('border-brand',    'bg-canvas',         3.0, 'brand border'),
  ('bg-brand',        'bg-canvas',         3.0, 'brand fill against the canvas'),
  # focus ring: the outer ring touches the background, never the component's
  # fill - the inner layer, in the background color, separates the two.
  # That is why the pair measured here is always ring x background.
  ('shadow-focus-default', 'bg-canvas',    3.0, 'default focus ring on the canvas'),
  ('shadow-focus-default', 'bg-surface',   3.0, 'default focus ring on the surface'),
  ('shadow-focus-error',   'bg-canvas',    3.0, 'error focus ring on the canvas'),
  ('shadow-focus-error',   'bg-surface',   3.0, 'error focus ring on the surface'),
]

# exceptions authorized by the brand: light text on the brand. All stay >= 3:1,
# so they meet AA for large text and for non-text elements - never below that.
EXCEPTIONS = {
  ('light', 'text-on-brand', 'bg-brand'),
  ('dark',  'text-on-brand', 'bg-brand'),
  ('dark',  'text-on-brand', 'bg-brand-hover'),
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
        print(f"\n{'='*78}\nTHEME {theme.upper()}\n{'='*78}")
        for t, label, fg, bg, a, b, v, mn, ok, exc in rows:
            if t != theme: continue
            tag = 'EXC ' if exc else ('OK  ' if ok else 'FAIL')
            print(f"  {tag} {label:<{w}}  {a} / {b}  {v:6.2f}:1  (min {mn})")
    print(f"\n{'-'*78}")
    if fails:
        print(f"{len(fails)} PAIR(S) FAIL:")
        for f in fails: print("   ", f)
        return 1
    n_exc = sum(1 for r in rows if r[9])
    print(f"{len(rows) - n_exc} pairs pass full AA.")
    print(f"{n_exc} brand exceptions, all >= {HARD_FLOOR}:1 (AA for large text and non-text):")
    for r in rows:
        if r[9]: print(f"   {r[0]:<6} {r[1]:<38} {r[6]:.2f}:1")
    return 0

if __name__ == '__main__':
    sys.exit(run())
