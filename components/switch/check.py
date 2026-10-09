"""
Portao do CSS do Switch.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Switch.

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
    '<label class="al-switch"> envolvendo o input - rotulo visivel, sem aria-label',
    'input nativo type="checkbox" com role="switch" - nunca <div>/<button> com ARIA',
    'bolinha com aria-hidden="true"',
    'sem aria-invalid nem required: o switch nao tem erro (regra 20)',
]


if __name__ == '__main__':
    sys.exit(gate('switch', fora_do_css=FORA_DO_CSS))
