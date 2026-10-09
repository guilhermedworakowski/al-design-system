"""
Portao do CSS do Modal.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Modal.

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
    '<dialog> nativo aberto por showModal(), nunca `open` na marcacao nem show() (regra 24)',
    'aria-labelledby apontando para o titulo (regra 25)',
    'pelo menos um botao no rodape; sem botao X (regra 16); acao secundaria antes da principal (regra 19)',
    'no maximo duas acoes; Danger so como principal (regras 19 e 20)',
    'nunca .al-modal dentro de .al-modal (regra 4)',
    'foco inicial, clique no scrim e abrir/fechar por atributo: modal.js (regras 14, 26 e 29)',
]


if __name__ == '__main__':
    sys.exit(gate('modal', fora_do_css=FORA_DO_CSS))
