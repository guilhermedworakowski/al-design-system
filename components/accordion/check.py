"""
Portao do CSS do Accordion.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Accordion.

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
    'marcacao nativa <details>/<summary>, sem role nem aria-expanded manual (regra 24)',
    'nada de <h1>-<h6> nem elemento clicavel dentro do <summary> (regras 17 e 25)',
    'icone e chevron com aria-hidden="true" (regras 18 e 19)',
    'nunca .al-accordion dentro de .al-accordion (regra 5)',
    'sobre bg-surface, nunca na tela nem dentro de card (regra 14) - layout, sem portao possivel',
]


if __name__ == '__main__':
    sys.exit(gate('accordion', fora_do_css=FORA_DO_CSS))
