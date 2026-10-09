"""
Portao do CSS do Password.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Password.

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
    'erro: aria-invalid="true" + aria-describedby apontando para o id da mensagem (regra 29)',
    'erro exige a mensagem; __help so existe no erro (regras 7 e 8)',
    'olho: <button type="button"> + aria-controls + aria-label alternando, nasce hidden (regra 28)',
    'icones do olho com aria-hidden="true" focusable="false" (contrato do Icon)',
    'campo desabilitado -> botao do olho tambem disabled (regra 20)',
    'autocomplete current-password/new-password, spellcheck=false, autocapitalize=none (regras 25-26)',
    'sem maxlength (regra 12); colar permitido (regra 27)',
]


if __name__ == '__main__':
    sys.exit(gate('password', fora_do_css=FORA_DO_CSS))
