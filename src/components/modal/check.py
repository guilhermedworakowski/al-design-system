"""
CSS gate for the Modal.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Modal stays here.

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
    'at least one button in the footer; no X button (rule 16); secondary action before the primary (rule 19)',
    'at most two actions; Danger only as primary (rules 19 and 20)',
    'never .al-modal inside .al-modal (rule 4)',
    'initial focus, scrim click and open/close by attribute: modal.js (rules 14, 26 and 29)',
]


if __name__ == '__main__':
    sys.exit(gate('modal', outside_css=OUTSIDE_CSS))
