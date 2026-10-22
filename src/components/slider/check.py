"""
CSS gate for the Slider.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Slider stays here.

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
    'always a native <input type="range"> named by a visible <label for> - never a div with role="slider"',
    'the value is an <output for="id"> in the header; Show value off only with the value shown elsewhere (rule 7)',
    'with a unit, data-unit on the input so slider.js writes aria-valuetext (rule 18)',
]


if __name__ == '__main__':
    sys.exit(gate('slider', outside_css=OUTSIDE_CSS))
