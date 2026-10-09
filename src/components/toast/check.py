"""
Portao do CSS do Toast.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Toast.

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
    'uma .al-toast-region com popover="manual" e as duas regioes vivas (status e alert) desde o carregamento (regras 22 e 23)',
    'cada toast num <template>, um modificador de status, titulo e descricao opcional (regras 11 e 13)',
    'icone de status com role="img" + aria-label; X com nome "Fechar notificação" (regras 14 e 24)',
    'fila, tempo na tela, pausa, Esc e foco: toast.js (regras 15 a 21)',
]


if __name__ == '__main__':
    sys.exit(gate('toast', outside_css=FORA_DO_CSS))
