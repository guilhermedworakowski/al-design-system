"""
CSS gate for the Password.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Password stays here.

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
    'error: aria-invalid="true" + aria-describedby pointing to the message id (rule 29)',
    'an error requires the message; __help only exists in error (rules 7 and 8)',
    'eye: <button type="button"> + aria-controls + toggling aria-label, starts hidden (rule 28)',
    'eye icons with aria-hidden="true" focusable="false" (Icon contract)',
    'disabled field -> the eye button is disabled too (rule 20)',
    'autocomplete current-password/new-password, spellcheck=false, autocapitalize=none (rules 25-26)',
    'no maxlength (rule 12); pasting allowed (rule 27)',
]


if __name__ == '__main__':
    sys.exit(gate('password', outside_css=OUTSIDE_CSS))
