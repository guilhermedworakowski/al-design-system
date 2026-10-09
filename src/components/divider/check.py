"""
CSS gate for the Divider.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Divider stays here.

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
    'announced default: <hr class="al-divider"> without aria-hidden (rule 12)',
    'decorative: aria-hidden="true" (rule 13)',
    'announced vertical: aria-orientation="vertical" (rule 14)',
    'in a <ul>/menu: <li role="separator">, never a loose <hr> (rule 15)',
    'never focusable or clickable: no tabindex, no onclick (rule 16)',
    'the line is never the only clue of the grouping (rule 8) - no gate possible',
]


if __name__ == '__main__':
    sys.exit(gate('divider', outside_css=OUTSIDE_CSS))
