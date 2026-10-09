"""
Portao do CSS do Icon.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Icon.

--al-icon-box e o ponto de ajuste publico do Icon (tamanho fora da escala,
no style do <svg>). O proprio icon.css declara, entao nao conta como inventado.

Rodar: python3 check.py (ou o build completo: python3 build.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from cssgate import gate  # noqa: E402


if __name__ == '__main__':
    sys.exit(gate('icon'))
