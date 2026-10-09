"""
CSS gate for the Card.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Card stays here.

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
    'the title is a real heading (h2/h3...), never a bold paragraph (rule 11)',
    'clickable card: a single .al-card__link, inside the title (rules 13 and 16)',
    'nothing clickable besides the link inside a clickable card (rule 15)',
    'a list of cards in <ul>/<li> (rule 22)',
    'Filled only on bg-surface (rule 2) - a layout decision, no gate possible',
]


if __name__ == '__main__':
    sys.exit(gate('card', outside_css=OUTSIDE_CSS))
