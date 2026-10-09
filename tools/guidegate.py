"""
Portao das diretrizes: src/components/<c>/guidelines.md.

O guidelines.md e a fonte das regras de uso de cada componente. Este portao
reprova o build se uma regra sumir, se a numeracao pular ou repetir, ou se o
total nao bater com o que foi aprovado na etapa 4. Confere tambem que o arquivo
aponta para a pagina certa do site e que o Icon continua sem diretrizes.

Mudou o numero de regras aprovadas de um componente? Atualize APPROVED no mesmo
commit em que o guidelines.md muda. Componente novo entra aqui junto com o
paths.COMPONENTS.

So usa a biblioteca padrao do Python (3.9 ou mais novo).
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import COMPONENTS, comp_src, rel  # noqa: E402

SITE = 'https://al.guilhermedesignd.com'

# Total de regras aprovadas por componente (etapa 4).
APPROVED = {
    'button': 10, 'icon-button': 13, 'tag': 26, 'avatar': 12, 'select': 27,
    'checkbox': 24, 'radio': 27, 'switch': 25, 'input': 31, 'textarea': 29,
    'password': 30, 'divider': 17, 'card': 24, 'tab': 26, 'accordion': 28,
    'modal': 29, 'drawer': 30, 'sidebar': 33, 'breadcrumb': 28, 'tooltip': 28,
    'toast': 27, 'alert': 29,
}

# O Icon nao ganha diretrizes: fica so a pagina de icones da Foundation.
SEM_DIRETRIZES = {'icon'}

# Uma regra e uma linha que comeca com "**<n>. ", o titulo em negrito.
REGRA = re.compile(r'^\*\*(\d+)\. ', re.M)


def problemas(c):
    path = comp_src(c, 'guidelines.md')
    if c in SEM_DIRETRIZES:
        return [f'{rel(path)} nao devia existir'] if os.path.exists(path) else []
    if c not in APPROVED:
        return [f'{c} esta em paths.COMPONENTS mas nao em APPROVED']
    if not os.path.exists(path):
        return [f'{rel(path)} nao existe']
    texto = open(path, encoding='utf-8').read()
    out = []
    nums = [int(n) for n in REGRA.findall(texto)]
    esperado = list(range(1, APPROVED[c] + 1))
    if nums != esperado:
        faltam = sorted(set(esperado) - set(nums))
        sobram = sorted(set(nums) - set(esperado))
        repetidas = sorted({n for n in nums if nums.count(n) > 1})
        detalhe = []
        if faltam:
            detalhe.append(f'faltam {faltam}')
        if sobram:
            detalhe.append(f'sobram {sobram}')
        if repetidas:
            detalhe.append(f'repetidas {repetidas}')
        if not detalhe:
            detalhe.append('fora de ordem')
        out.append(f'{rel(path)}: {len(nums)} regras, aprovadas {APPROVED[c]} '
                   f'({"; ".join(detalhe)})')
    if f'{SITE}/#{c})' not in texto:
        out.append(f'{rel(path)}: sem o link para {SITE}/#{c}')
    return out


def main():
    erros = []
    for c in COMPONENTS:
        erros += problemas(c)
    for c in sorted(set(APPROVED) - set(COMPONENTS)):
        erros.append(f'{c} esta em APPROVED mas nao em paths.COMPONENTS')
    total = sum(APPROVED.values())
    if erros:
        print('Diretrizes reprovadas:')
        for e in erros:
            print(f'  - {e}')
        return 1
    print(f'{len(APPROVED)} guidelines.md, {total} regras, numeracao e totais conferidos.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
