"""AL Design System - gerador de escalas de cor em OKLCH com gamut mapping sRGB."""
import math, json

# ---------- conversao ----------
def _lin(c): return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def _gam(c): return 12.92*c if c <= 0.0031308 else 1.055*(c**(1/2.4)) - 0.055

def oklch_to_lrgb(L, C, H):
    a = C*math.cos(math.radians(H)); b = C*math.sin(math.radians(H))
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l, m, s = l_**3, m_**3, s_**3
    r = +4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    bl= -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    return (r, g, bl)

def in_gamut(L, C, H, eps=1e-4):
    return all(-eps <= c <= 1+eps for c in oklch_to_lrgb(L, C, H))

def oklch_to_hex(L, C, H):
    """Reduz chroma por busca binaria ate caber no sRGB (preserva L e H)."""
    if not in_gamut(L, C, H):
        lo, hi = 0.0, C
        for _ in range(40):
            mid = (lo+hi)/2
            if in_gamut(L, mid, H): lo = mid
            else: hi = mid
        C = lo
    r, g, b = oklch_to_lrgb(L, C, H)
    out = []
    for c in (r, g, b):
        v = round(_gam(min(1.0, max(0.0, c)))*255)
        out.append(max(0, min(255, v)))
    return '#%02X%02X%02X' % tuple(out), C

def hex_to_oklch(h):
    h = h.lstrip('#')
    r, g, b = [_lin(int(h[i:i+2],16)/255) for i in (0,2,4)]
    l = (0.4122214708*r + 0.5363325363*g + 0.0514459929*b)**(1/3)
    m = (0.2119034982*r + 0.6806995451*g + 0.1073969566*b)**(1/3)
    s = (0.0883024619*r + 0.2817188376*g + 0.6299787005*b)**(1/3)
    L = 0.2104542553*l + 0.7936177850*m - 0.0040720468*s
    A = 1.9779984951*l - 2.4285922050*m + 0.4505937099*s
    B = 0.0259040371*l + 0.7827717662*m - 0.8086757660*s
    return L, math.hypot(A,B), math.degrees(math.atan2(B,A)) % 360

def lum(h):
    h = h.lstrip('#')
    r, g, b = [_lin(int(h[i:i+2],16)/255) for i in (0,2,4)]
    return 0.2126*r + 0.7152*g + 0.0722*b

def cr(a, b):
    l1, l2 = lum(a), lum(b)
    if l1 < l2: l1, l2 = l2, l1
    return (l1+0.05)/(l2+0.05)

def dE_ok(h1, h2):
    """Distancia OKLab entre duas cores (perceptual)."""
    def lab(h):
        L, C, H = hex_to_oklch(h)
        return L, C*math.cos(math.radians(H)), C*math.sin(math.radians(H))
    a, b = lab(h1), lab(h2)
    return math.dist(a, b)

# ---------- a escada de lightness compartilhada ----------
STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
# passo extra da marca: a janela de luminancia do label escuro so comporta 1 estado de hover
BRAND_HOVER = '#EA4900'
L_LADDER = {
    50: 0.977, 100: 0.950, 200: 0.908, 300: 0.852, 400: 0.768,
    500: 0.666, 600: 0.552, 700: 0.452, 800: 0.362, 900: 0.282, 950: 0.208,
}
# curva de chroma relativa ao pico da familia
C_REL = {
    50: 0.09, 100: 0.19, 200: 0.36, 300: 0.57, 400: 0.80, 500: 1.00,
    600: 0.95, 700: 0.85, 800: 0.72, 900: 0.57, 950: 0.42,
}

FAMILIES = {
    # nome:      (hue, chroma pico, drift de hue por step)
    'orange':  dict(hue=37.9, peak=0.219, drift={50: 14, 100: 12, 200: 9, 300: 7, 400: 4, 500: 0, 600: -1, 700: -2, 800: 2, 900: 5, 950: 8}),
    'red':     dict(hue=20.0, peak=0.205, drift={50: -5, 100: -4, 200: -3, 300: -2, 400: -1, 500: 0, 600: 0, 700: 1, 800: 3, 900: 5, 950: 7}),
    'amber':   dict(hue=85.0, peak=0.180, drift={50: 8, 100: 6, 200: 4, 300: 2, 400: 1, 500: 0, 600: -2, 700: -4, 800: -5, 900: -6, 950: -6}),
    'green':   dict(hue=148.0, peak=0.185, drift={50: 6, 100: 5, 200: 3, 300: 1, 400: 0, 500: 0, 600: -2, 700: -4, 800: -5, 900: -6, 950: -6}),
    'blue':    dict(hue=252.0, peak=0.200, drift={50: -6, 100: -5, 200: -3, 300: -2, 400: -1, 500: 0, 600: 1, 700: 2, 800: 3, 900: 4, 950: 5}),
}
# neutro frio: chroma baixa e quase constante (nao segue C_REL)
NEUTRAL_HUE = 264.0
NEUTRAL_C = {50: 0.004, 100: 0.006, 200: 0.008, 300: 0.010, 400: 0.012, 500: 0.013,
             600: 0.014, 700: 0.014, 800: 0.014, 900: 0.014, 950: 0.014}

def build():
    scales = {}
    n = {}
    for s in STEPS:
        hexv, cused = oklch_to_hex(L_LADDER[s], NEUTRAL_C[s], NEUTRAL_HUE)
        n[s] = hexv
    scales['neutral'] = n
    for name, cfg in FAMILIES.items():
        fam = {}
        for s in STEPS:
            L = L_LADDER[s]
            C = cfg['peak'] * C_REL[s]
            H = cfg['hue'] + cfg['drift'][s]
            hexv, cused = oklch_to_hex(L, C, H)
            fam[s] = hexv
        scales[name] = fam
    return scales

if __name__ == '__main__':
    sc = build()
    for fam, vals in sc.items():
        print(f"\n--- {fam} ---")
        for s in STEPS:
            h = vals[s]
            L, C, H = hex_to_oklch(h)
            print(f"  {fam}-{s:<4} {h}  L {L:.3f}  C {C:.3f}  H {H:6.1f}   vs#FFF {cr(h,'#FFFFFF'):5.2f}  vs {vals[950]} {cr(h,vals[950]):5.2f}")
    print("\n=== ancora da marca ===")
    print("  orange-500 =", sc['orange'][500], "(alvo #FC5000)", "OK" if sc['orange'][500]=='#FC5000' else "DIVERGE")
