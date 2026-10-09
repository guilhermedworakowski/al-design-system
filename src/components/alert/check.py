"""
Portao do CSS do Alert.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Alert.

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
    'um .al-alert-slot no topo da pagina, abaixo do header (regra 9)',
    'modificador de status, titulo e descricao em <p>, nunca heading (regras 13 e 26)',
    'icone de status com role="img" + aria-label; X com nome "Fechar aviso" (regras 16 e 27)',
    'sem role no carregamento; status/alert so quando inserido depois (regras 23 e 24): alert.js',
    'fechar, foco seguinte e evento al-alert-close: alert.js (regras 21 e 22)',
]


if __name__ == '__main__':
    sys.exit(gate('alert', outside_css=FORA_DO_CSS))
