"""
CSS gate for the Select.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Select stays here.

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
    '<label for> linked to the <select> id - no aria-label when there is a visible label',
    'error: aria-invalid="true" + aria-describedby pointing to the message id',
    'the placeholder is the first <option value="" disabled selected>, not an attribute',
    'the "(Optional)" mark marks the OPTIONAL - no mark means required',
    'the open list belongs to the browser: don\'t style <option>, item height or scroll',
]


if __name__ == '__main__':
    sys.exit(gate('select', outside_css=OUTSIDE_CSS))
