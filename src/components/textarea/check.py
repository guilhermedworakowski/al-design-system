"""
CSS gate for the Textarea.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Textarea stays here.

Extra check: the CSS line floor (min-height = line-height x N) and ROWS in
tokens.py are the same number written in two places. If one changes without
the other, the min-height stops matching the derived height.

Run: python3 check.py (or the full build: python3 build.py)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import comp_out  # noqa: E402
from cssgate import gate  # noqa: E402

# What this gate does NOT reach: markup only exists in the rendered output.
# a11y.py enforces these rules on the HTML the site emits.
OUTSIDE_CSS = [
    'native <textarea>, never contenteditable (rule 26)',
    '<label for> linked to the <textarea> id - no aria-label when there is a visible label (rule 27)',
    'rows >= 3 in the markup (rules 9 and 10)',
    'error: aria-invalid="true" + aria-describedby pointing to the message id (rule 28)',
    'an error requires help text with the message (rule 19)',
    'counter: aria-live="polite" only with focus; data-over-limit set by the JS (rules 16/28)',
    'the limit doesn\'t block typing: no maxlength (rule 16)',
    'empty read-only shows "—" as the value (rule 24)',
]


def line_floor(body):
    rows_tokens = json.load(open(comp_out('textarea', 'tokens.json')))['derived']['rows']
    m = re.search(r'min-height:\s*calc\(\s*var\(--al-textarea-line-height\)\s*\*\s*(\d+)', body)
    rows_css = int(m.group(1)) if m else None
    if rows_css != rows_tokens:
        return False, [f'LINE FLOOR OUT OF SYNC: textarea.css uses {rows_css}, tokens.py uses {rows_tokens}']
    return True, [f'line floor: {rows_css} in the CSS = ROWS {rows_tokens} in tokens.py', '-' * 70]


if __name__ == '__main__':
    sys.exit(gate('textarea', outside_css=OUTSIDE_CSS, extra=line_floor))
