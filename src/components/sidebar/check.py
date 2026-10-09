"""
CSS gate for the Sidebar.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Sidebar stays here.

Declared exception: the 1024px breakpoint in the @media rules. CSS doesn't
accept var() inside a media query, so the value stays written and the gate only
accepts it in that exact form.

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
    'a named <aside>; groups and Help inside <nav aria-label>; profile outside the nav (rule 26)',
    'each group <ul> named by its label through aria-labelledby (rule 27)',
    'items are <a> with aria-current="page" on the current one, at most one, never role="tab" (rules 12 and 28)',
    'decorative Avatar (aria-hidden, alt="") and a named profile Icon Button (rules 18 and 19)',
    'no repeated label (rule 16); one Sidebar per screen (rule 4)',
    'modal mode: move into a <dialog>, focus on the current item, closes on the destination and on the scrim, no X: sidebar.js (rule 25)',
]


if __name__ == '__main__':
    sys.exit(gate('sidebar', outside_css=OUTSIDE_CSS, exceptions=[('breakpoint', '1024px', '@media')]))
