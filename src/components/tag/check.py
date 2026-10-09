"""
Portao do CSS do Tag.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Tag.

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
    'o rotulo carrega o sentido, a cor nao - nenhum portao mede isso, e regra de uso',
    'aria-label obrigatorio no <button> do X, incluindo o rotulo - medido pelo a11y.py',
]


if __name__ == '__main__':
    sys.exit(gate('tag', fora_do_css=FORA_DO_CSS))
