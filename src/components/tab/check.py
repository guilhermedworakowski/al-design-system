"""
CSS gate for the Tab.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Tab stays here.

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
    'panel: named tablist, tab with aria-selected/aria-controls, linked tabpanel (rule 21)',
    'panel: only the selected tab at tabindex 0; arrows/Home/End in the script (rule 21)',
    'navigation: named <nav>, links, aria-current on the current one, never role="tab" (rule 22)',
    'exactly one selected per group (rule 7)',
    'one type per group - guaranteed by the class on the group, not on the tab (rule 6)',
    'the open content starts with a heading equal to the label (rule 25)',
]


if __name__ == '__main__':
    sys.exit(gate('tab', outside_css=OUTSIDE_CSS))
