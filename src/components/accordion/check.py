"""
CSS gate for the Accordion.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Accordion stays here.

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
    'native <details>/<summary> markup, no role and no manual aria-expanded (rule 24)',
    'no <h1>-<h6> and no clickable element inside the <summary> (rules 17 and 25)',
    'icon and chevron with aria-hidden="true" (rules 18 and 19)',
    'never .al-accordion inside .al-accordion (rule 5)',
    'on bg-surface, never on the canvas or inside a card (rule 14) - layout, no gate possible',
]


if __name__ == '__main__':
    sys.exit(gate('accordion', outside_css=OUTSIDE_CSS))
