"""
CSS gate for the Toast.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Toast stays here.

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
    'one .al-toast-region with popover="manual" and both live regions (status and alert) from load (rules 22 and 23)',
    'each toast in a <template>, one status modifier, title and optional description (rules 11 and 13)',
    'status icon with role="img" + aria-label; the X with its fixed name (rules 14 and 24)',
    'queue, time on screen, pause, Esc and focus: toast.js (rules 15 to 21)',
]


if __name__ == '__main__':
    sys.exit(gate('toast', outside_css=OUTSIDE_CSS))
