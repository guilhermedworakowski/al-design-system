"""
Full build of the AL Design System, in a single command.

Runs every generator and gate in the right order: Foundation, tokens and CSS
for each component, the site and the accessibility QA for each component.
Last, it assembles the package in dist/ - it only gets there if every gate
passed. It stops at the first step that fails and shows its output.

Run (from the repo root):
    python3 build.py            full build
    python3 build.py --check    full build, then checks that the build touched
                                nothing outside build/ and dist/ (this is what
                                GitHub Actions runs on every PR)
    python3 build.py --verbose  shows the output of every step

The order matters in a few places:
  - the Button's a11y.py measures tokens, so it runs before the site; the other
    a11y.py measure the HTML the site emits, so they run after it;
  - the site runs twice: the second run reads the a11y.json files updated by
    the first pass of the gates. The two generations converge; there is no loop;
  - in a clean clone no a11y.json exists yet, and the site can't be built
    without them. So, only in that case, each a11y.py runs once before the site
    (the warm-up): without the HTML it fails the markup contract, but it writes
    the contrast results, and that is what the site needs. A warm-up failure is
    expected and doesn't stop the build; the pass that counts is the one after
    the site.

Where everything lives (see tools/paths.py): what is written by hand lives in
src/; what the build generates goes to build/ and dist/, which stay out of git.

Uses only the Python standard library (3.9 or newer).
"""
import os, subprocess, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from paths import COMPONENTS  # noqa: E402  - the list lives in tools/paths.py

# Extra steps that run before the site, right after the component's check.py.
BEFORE_SITE = {
    'button': ['a11y.py'],   # measures tokens, not HTML
    'icon':   ['icons.py'],  # drawing gate + manifest
}

# Everything the build generates goes to build/ and dist/, out of git. --check
# confirms that, outside those folders, the build changed or created no file:
# a generated file leaking into the repo would be committed without anyone
# noticing.


def steps():
    """List of (folder, script, warmup). A warm-up step may fail."""
    out = [('tools', 'guidegate.py', False),
           ('src/foundation', 'export.py', False), ('src/foundation', 'css.py', False)]
    for c in COMPONENTS:
        d = f'src/components/{c}'
        out += [(d, 'tokens.py', False), (d, 'check.py', False)]
        out += [(d, s, False) for s in BEFORE_SITE.get(c, [])]
    after = [c for c in COMPONENTS if 'a11y.py' not in BEFORE_SITE.get(c, [])]
    for c in after:
        if not os.path.exists(os.path.join(ROOT, 'build', 'components', c, 'a11y.json')):
            out.append((f'src/components/{c}', 'a11y.py', True))
    out.append(('site', 'site.py', False))
    for c in after:
        out.append((f'src/components/{c}', 'a11y.py', False))
    out.append(('site', 'site.py', False))
    out.append(('tools', 'dist.py', False))
    return out


def run(verbose):
    all_steps = steps()
    start = time.time()
    for i, (d, script, warmup) in enumerate(all_steps, 1):
        path = f'{d}/{script}'
        r = subprocess.run([sys.executable, path], cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           universal_newlines=True)
        if r.returncode == 0:
            status = 'ok'
        elif warmup:
            status = 'warm-up (no site yet)'
        else:
            status = f'FAILED (exit {r.returncode})'
        print(f'[{i:2}/{len(all_steps)}] {path:38} {status}')
        if verbose or (r.returncode != 0 and not warmup):
            print(r.stdout.rstrip())
        if r.returncode != 0 and not warmup:
            print(f'\nBuild stopped at step {i}: {path}')
            return False
    print(f'\n{len(all_steps)} steps, 0 failures, {time.time() - start:.1f}s')
    return True


def check():
    r = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=all'],
                       cwd=ROOT,
                       stdout=subprocess.PIPE, universal_newlines=True)
    changed = r.stdout.rstrip()
    if r.returncode != 0:
        print('Could not run git status.')
        return False
    if changed:
        print('\nThe repo changed after the build (outside build/ and dist/):')
        print(changed)
        print('\nEither the build wrote outside build/ and dist/, or there were'
              '\nuncommitted changes before running. --check needs a clean repo.')
        return False
    print('Nothing changed in the repo outside build/ and dist/.')
    return True


if __name__ == '__main__':
    args = sys.argv[1:]
    unknown = [a for a in args if a not in ('--check', '--verbose')]
    if unknown:
        sys.exit(f'Unknown option: {" ".join(unknown)}\n{__doc__}')
    ok = run('--verbose' in args)
    if ok and '--check' in args:
        ok = check()
    sys.exit(0 if ok else 1)
