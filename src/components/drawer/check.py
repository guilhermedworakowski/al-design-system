"""
CSS gate for the Drawer.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Drawer stays here.

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
    'native <dialog> opened by showModal(), never `open` in the markup nor show() (rule 24)',
    'aria-labelledby pointing to the title (rule 25)',
    'always a visible way out: the X (Icon Button Ghost sm with aria-label) or the footer with a secondary that closes (rules 14 and 26)',
    'at most two actions; secondary before primary; Danger never as primary (rules 20 and 22)',
    'never .al-drawer inside .al-drawer (rule 4)',
    'initial focus, scrim click and open/close by attribute: drawer.js (rules 16 and 27)',
]


if __name__ == '__main__':
    sys.exit(gate('drawer', outside_css=OUTSIDE_CSS))
