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
    unless      {attr: value | true} - skips elements that match
    tag         list of allowed tag names
    within      selector one of the ancestors must match
    notWithin   selector no ancestor may match
    require     {attr: value | true} - attribute present (with this value)
    forbid      [attr] or {attr: value} - attribute absent (or not this value)
    has         [{sel, min, max, text}] - descendants matching sel, counted;
                text: true means each one needs visible text
    ref         [attr] - every id listed in the attribute exists in the page
    refText     [attr] - and each element it points to has visible text
    uniqueId    true - the element has an id, and no other element shares it
    referencedBy {sel, attr} - some element matching sel lists this id in attr
                (a <label for>, an aria-controls)
    absent      true - no element may match "on" at all (a role the AL never
                uses, a nesting it forbids); every other key is ignored

Selectors are a small subset of CSS, enough for the contracts: a tag, classes
and attributes chained (input.al-switch__input[type=checkbox]), the descendant
combinator (a space) and alternatives separated by commas. No >, + or ~.

    load(component)            the contract dict
    check(component, tree)     (findings, n) - n = elements the rules saw;
                               skip= a selector whose subtree is not checked
    audit(component, path, n)  what an a11y.py calls: (findings, count, html)
    markup_block(component)    the MARKUP CONTRACT block of the CSS, as text
    catalog(components)        what dist/components.json carries
"""
import json
import os
import re
from functools import lru_cache

from cssgate import CONTRACT_HEAD, CONTRACT_END, ROOT_CLASS
from htmltree import Tree, walk, classes, ancestors, text_of
from paths import comp_src

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

RULE_KEYS = {'id', 'rule', 'why', 'on', 'when', 'unless', 'tag', 'within', 'notWithin',
             'require', 'forbid', 'has', 'ref', 'refText', 'uniqueId', 'referencedBy',
             'absent'}
CHECKS = RULE_KEYS - {'id', 'rule', 'why', 'on', 'when', 'unless'}
CONTRACT_KEYS = {'component', 'root', 'rules', 'manual'}

_PART = re.compile(r'([a-zA-Z][a-zA-Z0-9-]*)|\.([a-zA-Z0-9_-]+)|\[([a-zA-Z-]+)(?:="?([^"\]]*)"?)?\]')


def path_of(component):
    return os.path.join(ROOT, 'src', 'components', component, 'contract.json')


def load(component):
    return json.load(open(path_of(component), encoding='utf-8'))


def _compound(alt):
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
    return (tag, frozenset(cls), tuple(attrs.items()))


@lru_cache(maxsize=None)
def parse(selector):
    """'.a input[type=checkbox], span.b' -> [[compound, ...]] - one chain per
    alternative, ancestors first, the element itself last."""
    return tuple(tuple(_compound(p) for p in alt.split()) for alt in selector.split(','))


def _one(node, compound):
    tag, cls, attrs = compound
    if tag and node['tag'] != tag:
        return False
    if not cls <= set(classes(node)):
        return False
    return not any(k not in node['attrs'] or (v is not None and node['attrs'][k] != v)
                   for k, v in attrs)


def matches(node, selector):
    for chain in parse(selector):
        if not _one(node, chain[-1]):
            continue
        rest = chain[:-1]
        for a in ancestors(node):
            if rest and _one(a, rest[-1]):
                rest = rest[:-1]
        if not rest:
            return True
    return False


def _index(tree):
    """Nodes, ids and a class/tag index, built once per tree."""
    ix = getattr(tree, '_contract_ix', None)
    if ix is None:
        nodes = list(walk(tree.root))
        by_class, by_tag, by_id = {}, {}, {}
        for i, n in enumerate(nodes):
            n['_i'] = i
            for k in classes(n):
                by_class.setdefault(k, []).append(n)
            by_tag.setdefault(n['tag'], []).append(n)
            if n['attrs'].get('id'):
                by_id.setdefault(n['attrs']['id'], []).append(n)
        ix = tree._contract_ix = {'nodes': nodes, 'class': by_class, 'tag': by_tag,
                                  'id': by_id, 'skip': {}}
    return ix


def select(tree, selector):
    """Elements matching the selector, in document order."""
    ix, out = _index(tree), {}
    for chain in parse(selector):
        tag, cls, _ = chain[-1]
        if cls:
            pool = ix['class'].get(min(cls, key=lambda k: len(ix['class'].get(k, ()))), [])
        elif tag:
            pool = ix['tag'].get(tag, [])
        else:
            pool = ix['nodes']
        for n in pool:
            if n['_i'] not in out and matches(n, selector):
                out[n['_i']] = n
    return [out[i] for i in sorted(out)]


def skipped(tree, skip):
    ix = _index(tree)
    if skip not in ix['skip']:
        gone = set()
        for top in select(tree, skip):
            gone.add(top['_i'])
            gone.update(d['_i'] for d in walk(top))
        ix['skip'][skip] = gone
    return ix['skip'][skip]


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
        if 'referencedBy' in r:
            try:
                parse(r['referencedBy']['sel'])
            except (ValueError, KeyError, TypeError) as e:
                errs.append(f'{rid}: referencedBy {e}')
        if not set(r) & CHECKS:
            errs.append(f'{rid}: the rule checks nothing')
    return errs


def check(component, tree, contract=None, skip='[inert]'):
    contract = contract or load(component)
    errs = validate(contract, component)
    if errs:
        return ([f'contract.json: {e}' for e in errs], 0)

    ix = _index(tree)
    by_id = ix['id']
    ids = set(by_id)
    gone = skipped(tree, skip) if skip else set()
    findings, seen = [], set()

    for r in contract['rules']:
        tagline = f'[{r["id"]}{", rule " + str(r["rule"]) if r.get("rule") else ""}]'
        for n in select(tree, r['on']):
            if n['_i'] in gone:
                continue
            if any(not _attr_ok(n, k, v) for k, v in r.get('when', {}).items()):
                continue
            if r.get('unless') and all(_attr_ok(n, k, v) for k, v in r['unless'].items()):
                continue
            seen.add(id(n))
            where = f'line {n["line"]}: {_show(n)}'

            def fail(what):
                findings.append(f'{where} {what} {tagline}')

            if r.get('absent'):
                fail('must not exist')
                continue
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
                found = [d for d in walk(n) if matches(d, h['sel'])]  # subtree only
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
            for k in r.get('refText', []):
                refs = n['attrs'].get(k, '').split()
                if not refs:
                    fail(f'without {k}')
                for ref in refs:
                    if ref not in ids:
                        fail(f'{k}="{ref}" points to no element')
                    elif not text_of(by_id[ref][0]):
                        fail(f'{k}="{ref}" points to an element without text')
            if r.get('uniqueId'):
                i = n['attrs'].get('id')
                if not i:
                    fail('without id')
                elif len(by_id[i]) > 1:
                    fail(f'id "{i}" appears {len(by_id[i])} times')
            if 'referencedBy' in r:
                rb, i = r['referencedBy'], n['attrs'].get('id')
                if not i or not any(i in x['attrs'].get(rb['attr'], '').split()
                                    for x in select(tree, rb['sel'])):
                    fail(f'no {rb["sel"]} points to it through {rb["attr"]}')
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
    """One entry per component: title and summary (the guidelines header, as
    in llms.txt), where its files are in dist/, the markup to write and the
    rules. dist/mcp reads this file."""
    from llms import name_and_summary
    out = {}
    for c in components:
        data = load(c)
        title, summary = name_and_summary(c)
        out[c] = {
            'title': title,
            'summary': summary,
            'root': data['root'],
            'css': f'components/{c}.css',
            'js': f'components/{c}.js' if os.path.exists(comp_src(c, f'{c}.js')) else None,
            'guidelines': f'guidelines/{c}.md' if os.path.exists(comp_src(c, 'guidelines.md')) else None,
            'markup': markup_block(c),
            'rules': data.get('rules', []),
            'manual': data.get('manual', []),
        }
    return out


def audit(component, path, count, skip=None):
    """For an a11y.py: reads the page, checks the contract and counts the
    component's elements (selector `count`). Returns (findings, n, html).
    The a11y.py adds its `manual` checks on top, from the same html."""
    if not os.path.exists(path):
        return ([f'HTML not found at {path} - markup contract NOT measured'], 0, '')
    html = open(path, encoding='utf-8').read()
    tree = Tree()
    tree.feed(html)
    findings, _ = check(component, tree, skip=skip)
    gone = skipped(tree, skip) if skip else set()
    n = len([x for x in select(tree, count) if x['_i'] not in gone])
    return (findings, n, html)


def whys(component):
    """One line per rule, checked and manual - what a11y.json lists."""
    data = load(component)
    return [r.get('why', '') for r in data.get('rules', []) + data.get('manual', [])]
