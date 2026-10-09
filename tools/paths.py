"""
Onde cada coisa mora no repo. Todo script le e escreve por aqui.

  src/    o que se escreve a mao: Foundation, CSS, JS, icones, portoes
  build/  o que o build gera para uso interno (tokens, a11y.json, o site);
          fora do git
  dist/   o pacote publicado no npm, montado por tools/dist.py; fora do git

Antes desta divisao, fonte e gerado ficavam lado a lado na mesma pasta, e o
git guardava os dois.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
BUILD = os.path.join(ROOT, 'build')
DIST = os.path.join(ROOT, 'dist')

# Ordem de criacao dos componentes. Componente novo entra no fim. E tambem a
# ordem do CSS no al.css e no site, entao mexer nela muda a cascata.
COMPONENTS = [
    'button', 'icon', 'icon-button', 'tag', 'avatar', 'select', 'checkbox',
    'radio', 'switch', 'input', 'textarea', 'password', 'divider', 'card',
    'tab', 'accordion', 'modal', 'drawer', 'sidebar', 'breadcrumb', 'tooltip',
    'toast', 'alert',
]

FOUNDATION_SRC = os.path.join(SRC, 'foundation')
TOKENS_JSON = os.path.join(BUILD, 'tokens.json')
FOUNDATION_CSS = os.path.join(BUILD, 'foundation', 'al-foundation.css')
SITE_HTML = os.path.join(BUILD, 'site', 'index.html')


def out(path):
    """Garante a pasta de um arquivo gerado e devolve o mesmo caminho."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def comp_src(c, *p):
    """Arquivo escrito a mao de um componente: src/components/<c>/..."""
    return os.path.join(SRC, 'components', c, *p)


def comp_out(c, *p):
    """Arquivo gerado de um componente: build/components/<c>/..."""
    return out(os.path.join(BUILD, 'components', c, *p))


def rel(path):
    """Caminho relativo a raiz, para mensagens e relatorios."""
    return os.path.relpath(path, ROOT)
