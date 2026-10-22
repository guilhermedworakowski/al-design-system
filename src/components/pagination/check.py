"""
CSS gate for the Pagination.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Pagination stays here.

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
    'a <nav aria-label="Pagination"> with the pages in a <ul>',
    'the current page carries aria-current="page" and every page is named "Page N"',
    'the ellipsis is aria-hidden; previous/next/load more are Buttons, rows is the Select',
]


if __name__ == '__main__':
    sys.exit(gate('pagination', outside_css=OUTSIDE_CSS))
