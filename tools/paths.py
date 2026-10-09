"""
Where everything lives in the repo. Every script reads and writes through here.

  src/    what is written by hand: Foundation, CSS, JS, icons, gates
  build/  what the build generates for internal use (tokens, a11y.json, the
          site); out of git
  dist/   the package published to npm, assembled by tools/dist.py; out of git

Before this split, source and generated files sat side by side in the same
folder, and git kept both.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
BUILD = os.path.join(ROOT, 'build')
DIST = os.path.join(ROOT, 'dist')

# Order in which the components were created. A new component goes at the end.
# It is also the CSS order in al.css and on the site, so changing it changes
# the cascade.
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
    """Makes sure a generated file's folder exists and returns the same path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def comp_src(c, *p):
    """A component's handwritten file: src/components/<c>/..."""
    return os.path.join(SRC, 'components', c, *p)


def comp_out(c, *p):
    """A component's generated file: build/components/<c>/..."""
    return out(os.path.join(BUILD, 'components', c, *p))


def rel(path):
    """Path relative to the root, for messages and reports."""
    return os.path.relpath(path, ROOT)
