"""
Portao do CSS do Avatar.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Avatar.

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
    'a cadeia Photo -> Iniciais -> Icon e comportamento de quem consome - troca de filho, nao de classe',
    'aria-hidden (decorativo) vs role="img" + aria-label (conteudo) no involucro - medido pelo a11y.py',
    'iniciais: no maximo 2 caracteres, derivadas do nome - regra de conteudo, sem portao possivel',
]


if __name__ == '__main__':
    sys.exit(gate('avatar', outside_css=FORA_DO_CSS))
