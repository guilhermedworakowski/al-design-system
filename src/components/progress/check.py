"""
CSS gate for the Progress.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Progress stays here.

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
    'always a native <progress value max> - never a div with a width',
    'Label and Steps name the bar by aria-labelledby on the visible label; Thin by aria-label',
    'no tabindex and no aria-live on the bar - completion is announced by a Toast or an Alert',
]


if __name__ == '__main__':
    sys.exit(gate('progress', outside_css=OUTSIDE_CSS))
