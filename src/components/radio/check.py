"""
CSS gate for the Radio.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Radio stays here.

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
    '<label class="al-radio"> wrapping the input - visible label, no aria-label',
    'native input type="radio" - never <div role="radio">',
    'the same `name` on every radio of the question, inside <fieldset> + <legend>',
    'dot with aria-hidden="true"',
    'error: aria-invalid="true" + aria-describedby on the FIELDSET (never on the radio) to the message THE FORM shows',
]


if __name__ == '__main__':
    sys.exit(gate('radio', outside_css=OUTSIDE_CSS))
