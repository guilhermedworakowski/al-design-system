"""
CSS gate for the Icon.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Icon stays here.

--al-icon-box is the Icon's public adjustment point (a size off the scale, in
the <svg> style). icon.css itself declares it, so it doesn't count as invented.

Run: python3 check.py (or the full build: python3 build.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from cssgate import gate  # noqa: E402


if __name__ == '__main__':
    sys.exit(gate('icon'))
