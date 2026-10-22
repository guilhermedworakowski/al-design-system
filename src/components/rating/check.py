"""
CSS gate for the Rating.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Rating stays here.

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
    'a <fieldset> with a <legend>, five native radios named "1 estrela" ... "5 estrelas"; the svg is aria-hidden',
    'read-only is one role="img" with aria-label "N de 5 estrelas" (exact value, H=a) - no radios, no focus',
    'nothing checked at first unless there is a previous rating (rule 8)',
]


if __name__ == '__main__':
    sys.exit(gate('rating', outside_css=OUTSIDE_CSS))
