"""
Portao do CSS do Divider.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Divider.

Rodar: python3 check.py (ou o build completo: python3 build.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from cssgate import gate  # noqa: E402

# O que este portao NAO alcanca: marcacao so existe na saida renderizada.
# O a11y.py da etapa 6 cobra estas regras no HTML que o site emite.
FORA_DO_CSS = [
    'padrao anunciado: <hr class="al-divider"> sem aria-hidden (regra 12)',
    'decorativo: aria-hidden="true" (regra 13)',
    'vertical anunciada: aria-orientation="vertical" (regra 14)',
    'em <ul>/menu: <li role="separator">, nunca <hr> solto (regra 15)',
    'nunca focavel nem clicavel: sem tabindex, sem onclick (regra 16)',
    'a linha nunca e a unica pista do agrupamento (regra 8) - sem portao possivel',
]


if __name__ == '__main__':
    sys.exit(gate('divider', outside_css=FORA_DO_CSS))
