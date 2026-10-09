"""
CSS gate for the Input.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Input stays here.

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
    '<label for> linked to the <input> id - no aria-label when there is a visible label',
    'with an affix: aria-labelledby = label + prefix + suffix (rule 29)',
    'error: aria-invalid="true" + aria-describedby pointing to the message id',
    'an error requires help text with the message (rule 17)',
    'counter: aria-live="polite" only with focus; data-over-limit set by the JS (rule 14/30)',
    'the limit doesn\'t block typing: no maxlength (rule 14)',
    'empty read-only shows "—" as the value (rule 22)',
]


if __name__ == '__main__':
    sys.exit(gate('input', outside_css=OUTSIDE_CSS))
