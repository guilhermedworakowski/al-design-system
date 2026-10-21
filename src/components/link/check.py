"""
CSS gate for the Link.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Link stays here.

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
    'always a real <a href> - never a span or div with a click handler',
    'the icon is aria-hidden; a new tab is announced in the label, not by the icon',
    'the label names the destination - no gate measures this, it is a usage rule',
]


if __name__ == '__main__':
    sys.exit(gate('link', outside_css=OUTSIDE_CSS))
