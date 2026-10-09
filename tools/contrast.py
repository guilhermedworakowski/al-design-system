"""
Contraste WCAG, num lugar so.

Antes desta pasta, a mesma conta estava copiada no foundation/color.py e nos 23
a11y.py. Agora todos importam daqui. A formula e a do WCAG 2.x: luminancia
relativa do sRGB e (L1 + 0.05) / (L2 + 0.05), com L1 a mais clara.

    cr(a, b)          razao sem arredondar (o que os portoes comparam)
    cr2(a, b)         a mesma razao arredondada em 2 casas (como o relatorio mostra)
    composite(c, bg)  cor com transparencia (#RRGGBBAA) pintada sobre um fundo opaco

Hex com 8 digitos (#RRGGBBAA) tem a transparencia ignorada em lum() e cr():
quem precisa dela compoe antes, com composite().
"""


def lin(c):
    """Canal de 0 a 255 -> linear."""
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    """Luminancia relativa de um hex (#RRGGBB ou #RRGGBBAA)."""
    h = h.lstrip('#')[:6]
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def cr(a, b):
    l1, l2 = sorted((lum(a), lum(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def cr2(a, b):
    return round(cr(a, b), 2)


def composite(hex8, base):
    h = hex8.lstrip('#')
    a = int(h[6:8], 16) / 255
    f = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(base.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02X%02X%02X' % tuple(round(f[i] * a + b[i] * (1 - a)) for i in range(3))
