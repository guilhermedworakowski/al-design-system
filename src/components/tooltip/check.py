"""
Portao do CSS do Tooltip.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Tooltip.

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
    'gatilho focavel, nunca disabled, ligado por aria-labelledby ou aria-describedby (regras 22 a 24)',
    '.al-tooltip com id, role="tooltip" e popover="manual", logo depois do gatilho (regras 24 e 25)',
    'icone <svg> aria-hidden + focusable="false"; nada interativo dentro (regras 10 e 11)',
    'atraso, hover, foco, Esc, um por vez e posicao: tooltip.js (regras 13 a 20)',
]


if __name__ == '__main__':
    sys.exit(gate('tooltip', outside_css=FORA_DO_CSS))
