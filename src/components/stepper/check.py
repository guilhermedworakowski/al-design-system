"""
CSS gate for the Stepper.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Stepper stays here.

Run: python3 check.py (or the full build: python3 build.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from cssgate import gate  # noqa: E402

# What this gate does NOT reach: markup only exists in the rendered output.
OUTSIDE_CSS = [
    'an <ol> inside <nav aria-label="Progress">',
    'the current step carries aria-current="step"; exactly one per Stepper',
    'every step spells its status in .al-stepper__status; the check svg is aria-hidden',
]


if __name__ == '__main__':
    sys.exit(gate('stepper', outside_css=OUTSIDE_CSS))
