"""
Portao do CSS do Drawer.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Drawer.

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
    'sempre uma saida visivel: o X (Icon Button Ghost sm com aria-label) ou o rodape com secundario que fecha (regras 14 e 26)',
    'no maximo duas acoes; secundaria antes da principal; Danger nunca como principal (regras 20 e 22)',
    'nunca .al-drawer dentro de .al-drawer (regra 4)',
    'foco inicial, clique no scrim e abrir/fechar por atributo: drawer.js (regras 16 e 27)',
]


if __name__ == '__main__':
    sys.exit(gate('drawer', fora_do_css=FORA_DO_CSS))
