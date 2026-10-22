"""
CSS gate for the Menu.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Menu stays here.

Run: python3 check.py (or the full build: python3 build.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from cssgate import gate  # noqa: E402

# What this gate does NOT reach: markup only exists in the rendered output.
# a11y.py enforces these rules on the HTML the site emits.
OUTSIDE_CSS = [
    'the trigger is an Icon Button with aria-haspopup="menu", aria-expanded, aria-controls and a name',
    'the list is role="menu"; each item a <button role="menuitem" tabindex="-1">, its <li> role="none"',
    'disabled is aria-disabled="true", never `disabled` (stays focusable); separators are <li class="al-divider" role="separator">',
    'the icon and the shortcut are aria-hidden; the shortcut is announced by aria-keyshortcuts',
]


if __name__ == '__main__':
    sys.exit(gate('menu', outside_css=OUTSIDE_CSS))
