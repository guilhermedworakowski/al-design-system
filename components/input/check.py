"""
Portao do CSS do Input.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Input.

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
    '<label for> ligado ao id do <input> - sem aria-label havendo rotulo visivel',
    'com afixo: aria-labelledby = rotulo + prefixo + sufixo (regra 29)',
    'erro: aria-invalid="true" + aria-describedby apontando para o id da mensagem',
    'erro exige texto de apoio com a mensagem (regra 17)',
    'contador: aria-live="polite" so com foco; data-over-limit ligado pelo JS (regra 14/30)',
    'limite nao trava a digitacao: sem maxlength (regra 14)',
    'read-only vazio mostra "—" como valor (regra 22)',
]


if __name__ == '__main__':
    sys.exit(gate('input', fora_do_css=FORA_DO_CSS))
