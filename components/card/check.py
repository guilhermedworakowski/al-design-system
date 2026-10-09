"""
Portao do CSS do Card.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Card.

Rodar: python3 check.py (ou o build completo: python3 build.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from cssgate import gate  # noqa: E402

# O que este portao NAO alcanca: marcacao so existe na saida renderizada.
# O a11y.py da etapa 6 cobra estas regras no HTML que o site emite.
FORA_DO_CSS = [
    'titulo e heading real (h2/h3...), nunca paragrafo em negrito (regra 11)',
    'card clicavel: um unico .al-card__link, dentro do titulo (regras 13 e 16)',
    'nada clicavel alem do link dentro do card clicavel (regra 15)',
    'lista de cards em <ul>/<li> (regra 22)',
    'Filled so sobre bg-surface (regra 2) - decisao de layout, sem portao possivel',
]


if __name__ == '__main__':
    sys.exit(gate('card', fora_do_css=FORA_DO_CSS))
