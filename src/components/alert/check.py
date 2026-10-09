"""
CSS gate for the Alert.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Alert stays here.

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
    'one .al-alert-slot at the top of the page, below the header (rule 9)',
    'status modifier, title and description in <p>, never a heading (rules 13 and 26)',
    'status icon with role="img" + aria-label; the X with its fixed name (rules 16 and 27)',
    'no role on load; status/alert only when inserted later (rules 23 and 24): alert.js',
    'close, next focus and the al-alert-close event: alert.js (rules 21 and 22)',
]


if __name__ == '__main__':
    sys.exit(gate('alert', outside_css=OUTSIDE_CSS))
