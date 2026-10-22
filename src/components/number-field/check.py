"""
CSS gate for the Number field.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Number field stays here.

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
    'native <input type="number"> with min, max and step; never a div with role (rule 20)',
    '<label for> linked to the <input> id',
    'steppers: <button type="button" tabindex="-1" aria-controls aria-label>, born hidden (rules 13 and 21)',
    'stepper icons with aria-hidden="true" focusable="false" (Icon contract)',
    'error: aria-invalid="true" + aria-describedby pointing to the message (rule 16)',
    'the field is born with a value; no placeholder (rule 9)',
]


if __name__ == '__main__':
    sys.exit(gate('number-field', outside_css=OUTSIDE_CSS))
