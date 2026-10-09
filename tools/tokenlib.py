"""
O que a camada de tokens de todo componente faz igual.

Cada src/components/<c>/tokens.py diz quais tokens o componente tem e para qual
token da Foundation cada um aponta. As contas abaixo - achar um token pelo
caminho, escrever a referencia CSS, gravar o arquivo - eram copiadas nos 23
arquivos, com pequenas variacoes. Agora moram aqui.

O nome nao e tokens.py de proposito: cada componente ja tem um tokens.py, e o
import acharia o do componente antes deste.
"""
import json
import os

from paths import TOKENS_JSON, comp_out, rel

FOUND = json.load(open(TOKENS_JSON))

TRANSPARENT = 'transparent'   # ausencia de cor, nao uma escolha de cor

# Caminho na Foundation -> nome da custom property. O primeiro prefixo que
# casa vence; o que sobrar do caminho vira o fim do nome.
_PREFIXES = [
    ('focusRing.', '--al-focus-ring-'),
    ('elevation.', '--al-elevation-'),
    ('space.', '--al-space-'),
    ('radius.', '--al-radius-'),
    ('border.width.', '--al-border-width-'),
    ('iconSize.', '--al-icon-size-'),
    ('type.size.', '--al-font-size-'),
    ('type.leading.', '--al-line-height-'),
    ('type.weight.', '--al-font-weight-'),
]


def resolve_foundation(path):
    """Segue um caminho pontuado dentro de tokens.json. Levanta se nao existir.

    Estilo de texto e lista ([nome, tamanho, ...]): o passo procura pelo nome.
    """
    node = FOUND
    for part in path.split('.'):
        if isinstance(node, list):
            match = next((s for s in node if s and s[0] == part), None)
            if match is None:
                raise KeyError(path)
            node = match
            continue
        if not isinstance(node, dict) or part not in node:
            raise KeyError(path)
        node = node[part]
    return node


def css_ref(ref):
    """Caminho da Foundation (ou nome de semantico) -> valor CSS.

    'space.8' -> var(--al-space-8); 'bg-brand' -> var(--al-bg-brand).
    Estilo de texto ('type.styles.body') devolve so o nome: quem chama monta as
    quatro vars do estilo.
    """
    if ref == TRANSPARENT:
        return TRANSPARENT
    for prefix, var in _PREFIXES:
        if ref.startswith(prefix):
            return f'var({var}{ref[len(prefix):]})'
    if ref.startswith('motion.'):
        _, kind, key = ref.split('.')
        return f'var(--al-motion-{kind}-{key})'
    if ref.startswith('type.styles.'):
        return ref.split('.')[2]
    return f'var(--al-{ref})'


def size_key(font_size):
    """Valor de font-size -> chave da escala (16 -> 'md')."""
    for key, v in FOUND['type']['size'].items():
        if v == font_size:
            return key
    raise KeyError(f'type.size com valor {font_size} nao existe na Foundation')


def save_css(c, texto):
    """Grava build/components/<c>/al-<c>-tokens.css."""
    path = comp_out(c, f'al-{c}-tokens.css')
    open(path, 'w').write(texto)
    print(f'{rel(path)} escrito ({os.path.getsize(path)} bytes)')
