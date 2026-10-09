"""
Portao do CSS do Tab.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Tab.

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
    'painel: tablist com nome, tab com aria-selected/aria-controls, tabpanel ligado (regra 21)',
    'painel: so a selecionada em tabindex 0; setas/Home/End no script (regra 21)',
    'navegacao: <nav> com nome, links, aria-current no atual, nunca role="tab" (regra 22)',
    'exatamente uma selecionada por grupo (regra 7)',
    'um tipo por grupo - garantido pela classe no grupo, nao na aba (regra 6)',
    'conteudo aberto comeca com titulo igual ao rotulo (regra 25)',
]


if __name__ == '__main__':
    sys.exit(gate('tab', fora_do_css=FORA_DO_CSS))
