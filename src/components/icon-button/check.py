"""
CSS gate for the Icon Button.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Icon Button stays here.

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
    'aria-label required on the <button> - measured by a11y.py, not here',
]


if __name__ == '__main__':
    sys.exit(gate('icon-button', outside_css=OUTSIDE_CSS))
