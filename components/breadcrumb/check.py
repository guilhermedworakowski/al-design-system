"""
Portao do CSS do Breadcrumb.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Breadcrumb.

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
    '<nav aria-label> com <ol>; um breadcrumb por pagina (regras 7 e 19)',
    'ultimo item = <span aria-current="page">, nunca <a>, sem separador (regras 15 e 20)',
    'separador <svg> aria-hidden + focusable="false" (regra 21)',
    '`…` = <button> com nome, aria-expanded e aria-controls; so na Large, 5+ niveis (regras 5 e 22)',
    'menu = <ul> de links Tab Square, nunca role="menu" (regra 17)',
    'abrir/fechar, Esc devolve foco, clique fora, foco sai: breadcrumb.js (regra 16, decisao B)',
]


if __name__ == '__main__':
    sys.exit(gate('breadcrumb', fora_do_css=FORA_DO_CSS))
