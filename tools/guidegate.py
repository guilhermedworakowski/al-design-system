"""
Guidelines gate: src/components/<c>/guidelines.md.

guidelines.md is the source of each component's usage rules. This gate fails
the build if a rule goes missing, if the numbering skips or repeats, or if the
total doesn't match what was approved. It also checks that the file points to
the right page of the site and that the Icon still has no guidelines.

Did a component's number of approved rules change? Update APPROVED in the same
commit that changes the guidelines.md. A new component goes in here together
with paths.COMPONENTS.

Uses only the Python standard library (3.9 or newer).
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import COMPONENTS, comp_src, rel  # noqa: E402

SITE = 'https://al.guilhermedesignd.com'

# Total of approved rules per component.
APPROVED = {
    'button': 10, 'icon-button': 13, 'tag': 26, 'avatar': 12, 'select': 27,
    'checkbox': 24, 'radio': 27, 'switch': 25, 'input': 31, 'textarea': 29,
    'password': 30, 'divider': 17, 'card': 24, 'tab': 26, 'accordion': 28,
    'modal': 29, 'drawer': 30, 'sidebar': 33, 'breadcrumb': 28, 'tooltip': 28,
    'toast': 27, 'alert': 29,
}

# The Icon gets no guidelines: only the Foundation icons page.
NO_GUIDELINES = {'icon'}

# A rule is a line that starts with "**<n>. ", the bold title.
RULE = re.compile(r'^\*\*(\d+)\. ', re.M)


def problems(c):
    path = comp_src(c, 'guidelines.md')
    if c in NO_GUIDELINES:
        return [f'{rel(path)} should not exist'] if os.path.exists(path) else []
    if c not in APPROVED:
        return [f'{c} is in paths.COMPONENTS but not in APPROVED']
    if not os.path.exists(path):
        return [f'{rel(path)} does not exist']
    text = open(path, encoding='utf-8').read()
    out = []
    nums = [int(n) for n in RULE.findall(text)]
    expected = list(range(1, APPROVED[c] + 1))
    if nums != expected:
        missing = sorted(set(expected) - set(nums))
        extra = sorted(set(nums) - set(expected))
        repeated = sorted({n for n in nums if nums.count(n) > 1})
        detail = []
        if missing:
            detail.append(f'missing {missing}')
        if extra:
            detail.append(f'extra {extra}')
        if repeated:
            detail.append(f'repeated {repeated}')
        if not detail:
            detail.append('out of order')
        out.append(f'{rel(path)}: {len(nums)} rules, approved {APPROVED[c]} '
                   f'({"; ".join(detail)})')
    if f'{SITE}/#{c})' not in text:
        out.append(f'{rel(path)}: missing the link to {SITE}/#{c}')
    return out


def main():
    errors = []
    for c in COMPONENTS:
        errors += problems(c)
    for c in sorted(set(APPROVED) - set(COMPONENTS)):
        errors.append(f'{c} is in APPROVED but not in paths.COMPONENTS')
    total = sum(APPROVED.values())
    if errors:
        print('Guidelines failed:')
        for e in errors:
            print(f'  - {e}')
        return 1
    print(f'{len(APPROVED)} guidelines.md, {total} rules, numbering and totals checked.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
