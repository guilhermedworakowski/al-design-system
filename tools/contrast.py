"""
WCAG contrast, in one place.

Before this folder, the same math was copied into foundation/color.py and the
23 a11y.py files. Now they all import from here. The formula is WCAG 2.x:
relative sRGB luminance and (L1 + 0.05) / (L2 + 0.05), with L1 the lighter.

    cr(a, b)          unrounded ratio (what the gates compare)
    cr2(a, b)         the same ratio rounded to 2 places (as the report shows)
    composite(c, bg)  a color with transparency (#RRGGBBAA) painted on an opaque
                      background

An 8-digit hex (#RRGGBBAA) has its transparency ignored in lum() and cr():
whoever needs it composites first, with composite().
"""


def lin(c):
    """Channel from 0 to 255 -> linear."""
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    """Relative luminance of a hex (#RRGGBB or #RRGGBBAA)."""
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
