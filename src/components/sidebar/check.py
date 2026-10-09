"""
Portao do CSS do Sidebar.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Sidebar.

Excecao declarada: o ponto de quebra de 1024px nas @media. CSS nao aceita
var() dentro de media query, entao o valor fica escrito e o portao so o aceita
nessa forma exata.

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
    '<aside> com nome; grupos e Ajuda dentro de <nav aria-label>; perfil fora do nav (regra 26)',
    'cada grupo <ul> nomeada pelo rotulo via aria-labelledby (regra 27)',
    'itens sao <a> com aria-current="page" no atual, no maximo um, nunca role="tab" (regras 12 e 28)',
    'Avatar decorativo (aria-hidden, alt="") e Icon Button do perfil com nome (regras 18 e 19)',
    'nenhum rotulo repetido (regra 16); uma Sidebar por tela (regra 4)',
    'modo modal: mover para <dialog>, foco no atual, fecha no destino e no scrim, sem X: sidebar.js (regra 25)',
]


if __name__ == '__main__':
    sys.exit(gate('sidebar', outside_css=FORA_DO_CSS, exceptions=[('ponto-de-quebra', '1024px', '@media')]))
