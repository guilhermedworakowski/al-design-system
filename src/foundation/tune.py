from color import *

# Calibracao da rampa neutra. O neutro e acromatico (chroma 0), entao o unico
# grau de liberdade e o L - e cada degrau que serve de texto ou de borda tem
# um piso de contraste para respeitar.
def solve_L_for_contrast(target, against='#FFFFFF', chroma=0.0, hue=NEUTRAL_HUE):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo+hi)/2
        h, _c = oklch_to_hex(mid, chroma, hue)
        if cr(h, against) > target: lo = mid   # mais escuro = mais contraste
        else: hi = mid
    return lo

n50, _ = oklch_to_hex(L_LADDER[50], 0.0, NEUTRAL_HUE)
for against, rotulo in (('#FFFFFF', 'branco'), (n50, f'neutral-50 {n50}')):
    print(f"-- contra {rotulo} --")
    for tgt in (3.0, 4.5, 7.0):
        L = solve_L_for_contrast(tgt, against)
        h, _ = oklch_to_hex(L, 0.0, NEUTRAL_HUE)
        print(f"   {tgt}:1 -> L {L:.4f}  {h}  (real {cr(h, against):.2f})")

print()
print(f"L(500) fixado pela marca = 0.666 -> neutro {oklch_to_hex(0.666,0.0,NEUTRAL_HUE)[0]}"
      f" = {cr(oklch_to_hex(0.666,0.0,NEUTRAL_HUE)[0],'#FFFFFF'):.2f}:1")
print(f"L(600) usado = {L_LADDER[600]} -> {oklch_to_hex(L_LADDER[600],0.0,NEUTRAL_HUE)[0]}"
      f"  vs neutral-50 {cr(oklch_to_hex(L_LADDER[600],0.0,NEUTRAL_HUE)[0], n50):.3f}:1"
      f"  (o pior caso de text-secondary; por isso 0.550 e nao 0.552)")

# distancias de colisao entre familias no mesmo step
sc = build()
print("\n=== colisao: distancia OKLab (dE) entre familias ===")
pairs = [('orange',500,'red',500), ('orange',500,'red',600), ('orange',500,'red',700),
         ('orange',500,'amber',500), ('orange',500,'amber',400),
         ('orange',700,'red',700), ('orange',300,'red',300), ('orange',100,'red',100)]
for f1,s1,f2,s2 in pairs:
    a, b = sc[f1][s1], sc[f2][s2]
    print(f"  {f1}-{s1} {a}  x  {f2}-{s2} {b}   dE {dE_ok(a,b):.4f}   dHue {abs(hex_to_oklch(a)[2]-hex_to_oklch(b)[2]):.1f}deg")
