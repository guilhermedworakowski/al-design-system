"""
CSS gate for the Tooltip.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Tooltip stays here.

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
    'a focusable trigger, never disabled, linked by aria-labelledby or aria-describedby (rules 22 to 24)',
    '.al-tooltip with an id, role="tooltip" and popover="manual", right after the trigger (rules 24 and 25)',
    'icon <svg> aria-hidden + focusable="false"; nothing interactive inside (rules 10 and 11)',
    'delay, hover, focus, Esc, one at a time and position: tooltip.js (rules 13 to 20)',
]


if __name__ == '__main__':
    sys.exit(gate('tooltip', outside_css=OUTSIDE_CSS))
