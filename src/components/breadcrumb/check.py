"""
CSS gate for the Breadcrumb.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Breadcrumb stays here.

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
    '<nav aria-label> with an <ol>; one breadcrumb per page (rules 7 and 19)',
    'last item = <span aria-current="page">, never <a>, no separator (rules 15 and 20)',
    'separator <svg> aria-hidden + focusable="false" (rule 21)',
    '`…` = a named <button> with aria-expanded and aria-controls; only in Large, 5+ levels (rules 5 and 22)',
    'menu = a <ul> of Tab Square links, never role="menu" (rule 17)',
    'open/close, Esc returns focus, click outside, focus leaves: breadcrumb.js (rule 16)',
]


if __name__ == '__main__':
    sys.exit(gate('breadcrumb', outside_css=OUTSIDE_CSS))
