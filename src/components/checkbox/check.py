"""
CSS gate for the Checkbox.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Checkbox stays here.

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
    '<label class="al-checkbox"> wrapping the input - visible label, no aria-label',
    'native input type="checkbox" - never <div role="checkbox">',
    'check and minus glyphs with aria-hidden="true" focusable="false"',
    'error: aria-invalid="true" + aria-describedby to the message THE FORM shows',
    'indeterminate only through JS (input.indeterminate = true) - there is no HTML attribute',
]


if __name__ == '__main__':
    sys.exit(gate('checkbox', outside_css=OUTSIDE_CSS))
