"""
CSS gate for the Empty state.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Empty state stays here.

Run: python3 check.py (or the full build: python3 build.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from cssgate import gate  # noqa: E402

# What this gate does NOT reach: markup only exists in the rendered output.
OUTSIDE_CSS = [
    'the title is a heading (h2, h3...) whose level follows the page outline',
    'the icon svg is aria-hidden',
    'at most one .al-btn--primary; a second action is a Link in the description',
    'after a search or filter it renders inside role="status"; static on first load',
]


if __name__ == '__main__':
    sys.exit(gate('empty-state', outside_css=OUTSIDE_CSS))
