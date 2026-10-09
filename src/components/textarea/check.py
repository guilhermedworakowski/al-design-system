"""
Portao do CSS do Textarea.

A regra e a mesma para todos os componentes e mora em tools/cssgate.py: nada
de valor literal (cor, comprimento, peso, duracao), nenhum token orfao e
nenhum token inventado. Aqui fica so o que e proprio do Textarea.

Conferencia extra: o piso de linhas do CSS (min-height = line-height x N) e o
ROWS do tokens.py sao o mesmo numero escrito em dois lugares. Se um mudar sem o
outro, o min-height deixa de bater com a altura derivada.

Rodar: python3 check.py (ou o build completo: python3 build.py)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import comp_out  # noqa: E402
from cssgate import gate  # noqa: E402

# O que este portao NAO alcanca: marcacao so existe na saida renderizada.
# O a11y.py da etapa 6 cobra estas regras no HTML que o site emite.
FORA_DO_CSS = [
    '<textarea> nativo, nunca contenteditable (regra 26)',
    '<label for> ligado ao id da <textarea> - sem aria-label havendo rotulo visivel (regra 27)',
    'rows >= 3 na marcacao (regras 9 e 10)',
    'erro: aria-invalid="true" + aria-describedby apontando para o id da mensagem (regra 28)',
    'erro exige texto de apoio com a mensagem (regra 19)',
    'contador: aria-live="polite" so com foco; data-over-limit ligado pelo JS (regras 16/28)',
    'limite nao trava a digitacao: sem maxlength (regra 16)',
    'read-only vazio mostra "—" como valor (regra 24)',
]


def piso_de_linhas(body):
    rows_tokens = json.load(open(comp_out('textarea', 'tokens.json')))['derived']['rows']
    m = re.search(r'min-height:\s*calc\(\s*var\(--al-textarea-line-height\)\s*\*\s*(\d+)', body)
    rows_css = int(m.group(1)) if m else None
    if rows_css != rows_tokens:
        return False, [f'PISO DE LINHAS DESSINCRONIZADO: textarea.css usa {rows_css}, tokens.py usa {rows_tokens}']
    return True, [f'piso de linhas: {rows_css} no CSS = ROWS {rows_tokens} no tokens.py', '-' * 70]


if __name__ == '__main__':
    sys.exit(gate('textarea', outside_css=FORA_DO_CSS, extra=piso_de_linhas))
