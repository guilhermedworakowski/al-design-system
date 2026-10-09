"""
CSS gate for the Avatar.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Avatar stays here.

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
    'the Photo -> Initials -> Icon chain is the consumer\'s behavior - a child swap, not a class swap',
    'aria-hidden (decorative) vs role="img" + aria-label (content) on the wrapper - measured by a11y.py',
    'initials: at most 2 characters, derived from the name - a content rule, no gate possible',
]


if __name__ == '__main__':
    sys.exit(gate('avatar', outside_css=OUTSIDE_CSS))
