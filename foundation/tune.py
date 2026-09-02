from color import *

# qual L de neutro atinge exatamente 4.5:1 sobre branco?
def solve_L_for_contrast(target, hue, chroma, against='#FFFFFF'):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo+hi)/2
        h, _c = oklch_to_hex(mid, chroma, hue)
        if cr(h, against) > target: lo = mid   # mais escuro = mais contraste
        else: hi = mid
    return lo

for tgt in (3.0, 4.5, 7.0):
    L = solve_L_for_contrast(tgt, NEUTRAL_HUE, 0.013)
    h, _ = oklch_to_hex(L, 0.013, NEUTRAL_HUE)
    print(f"neutro {tgt}:1 sobre branco -> L {L:.4f}  {h}  (real {cr(h,'#FFFFFF'):.2f})")

print()
print(f"L(500) fixado pela marca = 0.666 -> neutro {oklch_to_hex(0.666,0.013,NEUTRAL_HUE)[0]} = {cr(oklch_to_hex(0.666,0.013,NEUTRAL_HUE)[0],'#FFFFFF'):.2f}:1")

# distancias de colisao entre familias no mesmo step
sc = build()
print("\n=== colisao: distancia OKLab (dE) entre familias ===")
pairs = [('orange',500,'red',500), ('orange',500,'red',600), ('orange',500,'red',700),
         ('orange',500,'amber',500), ('orange',500,'amber',400),
         ('orange',700,'red',700), ('orange',300,'red',300), ('orange',100,'red',100)]
for f1,s1,f2,s2 in pairs:
    a, b = sc[f1][s1], sc[f2][s2]
    print(f"  {f1}-{s1} {a}  x  {f2}-{s2} {b}   dE {dE_ok(a,b):.4f}   dHue {abs(hex_to_oklch(a)[2]-hex_to_oklch(b)[2]):.1f}deg")
