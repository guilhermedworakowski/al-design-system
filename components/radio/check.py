"""
Portao do CSS do Radio.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Radio.

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
    '<label class="al-radio"> envolvendo o input - rotulo visivel, sem aria-label',
    'input nativo type="radio" - nunca <div role="radio">',
    'mesmo `name` em todos os radios da pergunta, dentro de <fieldset> + <legend>',
    'ponto com aria-hidden="true"',
    'erro: aria-invalid="true" + aria-describedby no FIELDSET (nunca no radio) para a mensagem QUE O FORMULARIO mostra',
]


if __name__ == '__main__':
    sys.exit(gate('radio', fora_do_css=FORA_DO_CSS))
