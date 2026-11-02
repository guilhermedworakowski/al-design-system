"""
Markup contract as data, in one place.

Each component keeps its contract in src/components/<c>/contract.json. The
a11y.py gates read it through this module, and the Node validator shipped in
the package reads the same file, so the rule is written once and checked the
same way on both sides.

A contract has:

    root        the component's root class (the same ROOT_CLASS cssgate uses)
    rules       rules the engine checks on the rendered HTML
    manual      rules that need page logic: checked by the a11y.py in code,
                listed here so a reader (person or AI) knows they exist

A rule is an object with:

    id          stable kebab-case name, unique in the file
    rule        number of the usage rule in guidelines.md (optional)
    why         one sentence: what breaks if the rule is broken
    on          selector of the elements the rule applies to
    when        {attr: value | true} - applies only to elements that match
    tag         list of allowed tag names
    within      selector one of the ancestors must match
    notWithin   selector no ancestor may match
    require     {attr: value | true} - attribute present (with this value)
    forbid      [attr] or {attr: value} - attribute absent (or not this value)
    has         [{sel, min, max, text}] - descendants matching sel, counted;
                text: true means each one needs visible text
    ref         [attr] - every id listed in the attribute exists in the page

Selectors are a small subset of CSS, enough for the contracts: a tag, classes
and attributes chained without spaces (input.al-switch__input[type=checkbox]),
and alternatives separated by commas. No descendant combinator: that is what
within, notWithin and has are for.

    load(component)            the contract dict
    check(component, tree)     (findings, n) - n = elements the rules saw
    markup_block(component)    the MARKUP CONTRACT block of the CSS, as text
    catalog(components)        what dist/components.json carries
"""
import json
import os
import re

from cssgate import CONTRACT_HEAD, CONTRACT_END, ROOT_CLASS
from htmltree import walk, classes, ancestors, text_of
from paths import comp_src

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

RULE_KEYS = {'id', 'rule', 'why', 'on', 'when', 'tag', 'within', 'notWithin',
             'require', 'forbid', 'has', 'ref'}
CONTRACT_KEYS = {'component', 'root', 'rules', 'manual'}

_PART = re.compile(r'([a-zA-Z][a-zA-Z0-9-]*)|\.([a-zA-Z0-9_-]+)|\[([a-zA-Z-]+)(?:="?([^"\]]*)"?)?\]')


def path_of(component):
    return os.path.join(ROOT, 'src', 'components', component, 'contract.json')


def load(component):
    return json.load(open(path_of(component), encoding='utf-8'))


def parse(selector):
    """'input.a[type=checkbox], span.b' -> [(tag, {classes}, {attr: value|None})]"""
    out = []
    for alt in selector.split(','):
        alt = alt.strip()
        tag, cls, attrs, pos = None, set(), {}, 0
        for m in _PART.finditer(alt):
            if m.start() != pos:
                raise ValueError(f'selector not supported: "{alt}"')
            pos = m.end()
            if m.group(1):
                tag = m.group(1).lower()
            elif m.group(2):
                cls.add(m.group(2))
            else:
                attrs[m.group(3)] = m.group(4)
        if pos != len(alt) or not alt:
            raise ValueError(f'selector not supported: "{alt}"')
        out.append((tag, cls, attrs))
    return out


def matches(node, selector):
    for tag, cls, attrs in parse(selector):
        if tag and node['tag'] != tag:
            continue
        if not cls <= set(classes(node)):
            continue
        if any(k not in node['attrs'] or (v is not None and node['attrs'][k] != v)
               for k, v in attrs.items()):
            continue
        return True
    return False


def _attr_ok(node, k, v):
    if k not in node['attrs']:
        return False
    return v is True or node['attrs'][k] == v


def _show(node):
    a = ' '.join(f'{k}="{v}"' if v else k for k, v in node['attrs'].items())
    s = f'<{node["tag"]}{" " + a if a else ""}>'
    return s if len(s) <= 70 else s[:67] + '...'


def validate(contract, component):
    """Shape errors in the contract itself - the file is data, so it gets a gate."""
    errs = []
    extra = set(contract) - CONTRACT_KEYS
    if extra:
        errs.append(f'unknown keys: {sorted(extra)}')
    if contract.get('component') != component:
        errs.append(f'"component" must be "{component}"')
    root = ROOT_CLASS.get(component, f'al-{component}')
    if contract.get('root') != root:
        errs.append(f'"root" must be "{root}" - the root class cssgate uses')
    seen = set()
    for r in contract.get('rules', []) + contract.get('manual', []):
        rid = r.get('id', '?')
        if rid in seen:
            errs.append(f'id "{rid}" repeated')
        seen.add(rid)
        if not r.get('why'):
            errs.append(f'{rid}: no "why"')
    for r in contract.get('rules', []):
        rid = r.get('id', '?')
        extra = set(r) - RULE_KEYS
        if extra:
            errs.append(f'{rid}: unknown keys {sorted(extra)}')
        if 'on' not in r:
            errs.append(f'{rid}: no "on"')
        for key in ('on', 'within', 'notWithin'):
            if key in r:
                try:
                    parse(r[key])
                except ValueError as e:
                    errs.append(f'{rid}: {e}')
        if not set(r) & {'tag', 'within', 'notWithin', 'require', 'forbid', 'has', 'ref'}:
            errs.append(f'{rid}: the rule checks nothing')
    return errs


def check(component, tree, contract=None):
    contract = contract or load(component)
    errs = validate(contract, component)
    if errs:
        return ([f'contract.json: {e}' for e in errs], 0)

    nodes = list(walk(tree.root))
    ids = {n['attrs']['id'] for n in nodes if n['attrs'].get('id')}
    findings, seen = [], set()

    for r in contract['rules']:
        tagline = f'[{r["id"]}{", rule " + str(r["rule"]) if r.get("rule") else ""}]'
        for n in nodes:
            if not matches(n, r['on']):
                continue
            if any(not _attr_ok(n, k, v) for k, v in r.get('when', {}).items()):
                continue
            seen.add(id(n))
            where = f'line {n["line"]}: {_show(n)}'

            def fail(what):
                findings.append(f'{where} {what} {tagline}')

            if 'tag' in r and n['tag'] not in r['tag']:
                fail(f'is a <{n["tag"]}>, must be {" or ".join("<" + t + ">" for t in r["tag"])}')
            if 'within' in r and not any(matches(a, r['within']) for a in ancestors(n)):
                fail(f'outside {r["within"]}')
            if 'notWithin' in r and any(matches(a, r['notWithin']) for a in ancestors(n)):
                fail(f'inside {r["notWithin"]}')
            for k, v in r.get('require', {}).items():
                if not _attr_ok(n, k, v):
                    fail(f'without {k}' + ('' if v is True else f'="{v}"'))
            forbid = r.get('forbid', [])
            for k, v in (forbid.items() if isinstance(forbid, dict) else ((k, True) for k in forbid)):
                if _attr_ok(n, k, v):
                    fail(f'with {k}' + ('' if v is True else f'="{v}"'))
            for h in r.get('has', []):
                found = [d for d in walk(n) if matches(d, h['sel'])]
                lo, hi = h.get('min', 1), h.get('max')
                if len(found) < lo or (hi is not None and len(found) > hi):
                    want = f'{lo}' if hi == lo else (f'{lo} to {hi}' if hi is not None else f'at least {lo}')
                    fail(f'has {len(found)} {h["sel"]}, expected {want}')
                if h.get('text'):
                    for d in found:
                        if not text_of(d):
                            fail(f'{h["sel"]} without visible text')
            for k in r.get('ref', []):
                for ref in n['attrs'].get(k, '').split():
                    if ref not in ids:
                        fail(f'{k}="{ref}" points to no element')
    return (findings, len(seen))


def markup_block(component):
    """The HTML example lives in the CSS (one source): this reads it back, with
    the comment's ' * ' gutter removed, for the catalog."""
    text = open(comp_src(component, f'{component}.css'), encoding='utf-8').read()
    header = text[:text.find('*/')]
    head = CONTRACT_HEAD.search(header)
    block = header[head.end():]
    end = CONTRACT_END.search(block)
    block = block[:end.start()] if end else block
    lines = [re.sub(r'^ \*( |$)', '', ln) for ln in block.split('\n')]
    return '\n'.join(lines).strip('\n')


def catalog(components):
    """One entry per component: where its files are, the markup to write and
    the rules. A component without contract.json yet goes in with no rules."""
    out = {}
    for c in components:
        data = load(c) if os.path.exists(path_of(c)) else {'root': ROOT_CLASS.get(c, f'al-{c}')}
        out[c] = {
            'root': data['root'],
            'css': f'components/{c}.css',
            'js': f'components/{c}.js' if os.path.exists(comp_src(c, f'{c}.js')) else None,
            'guidelines': f'https://raw.githubusercontent.com/guilhermedworakowski/al-design-system/main/src/components/{c}/guidelines.md',
            'markup': markup_block(c),
            'rules': data.get('rules', []),
            'manual': data.get('manual', []),
        }
    return out
