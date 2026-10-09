"""
Portao do CSS do Select.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Select.

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
    '<label for> ligado ao id do <select> - sem aria-label havendo rotulo visivel',
    'erro: aria-invalid="true" + aria-describedby apontando para o id da mensagem',
    'placeholder e a primeira <option value="" disabled selected>, nao um atributo',
    'a marca "(Opcional)" marca o OPCIONAL - ausencia da marca e o obrigatorio',
    'a lista aberta e do navegador: nao estilizar <option>, altura de item nem scroll',
]


if __name__ == '__main__':
    sys.exit(gate('select', outside_css=FORA_DO_CSS))
