// Markup contract checker, the Node twin of tools/contract.py.
//
// The rules come from components.json (built from each component's
// contract.json), so this file holds no rule of its own: it only knows the
// vocabulary - on, when, unless, tag, within, notWithin, require, forbid,
// has, ref, refText, uniqueId, referencedBy, absent. The build runs both
// checkers on the same pages and fails if they disagree (tools/parity.py).

import { walk, classes, ancestors, textOf } from './html.mjs';

const PART = /([a-zA-Z][a-zA-Z0-9-]*)|\.([a-zA-Z0-9_-]+)|\[([a-zA-Z-]+)(?:="?([^"\]]*)"?)?\]/gy;
const cache = new Map();

function compound(alt) {
  let tag = null;
  const cls = [];
  const attrs = [];
  PART.lastIndex = 0;
  let m;
  while (PART.lastIndex < alt.length && (m = PART.exec(alt))) {
    if (m[1]) tag = m[1].toLowerCase();
    else if (m[2]) cls.push(m[2]);
    else attrs.push([m[3], m[4] ?? null]);
  }
  if (!alt || PART.lastIndex !== alt.length) throw new Error(`selector not supported: "${alt}"`);
  return { tag, cls, attrs };
}

// '.a input[type=checkbox], span.b' -> one chain per alternative, ancestors
// first, the element itself last
export function parseSelector(selector) {
  if (!cache.has(selector)) {
    cache.set(selector, selector.split(',').map((alt) => alt.trim().split(/\s+/).map(compound)));
  }
  return cache.get(selector);
}

function one(node, { tag, cls, attrs }) {
  if (tag && node.tag !== tag) return false;
  const own = classes(node);
  if (!cls.every((c) => own.includes(c))) return false;
  return attrs.every(([k, v]) => k in node.attrs && (v === null || node.attrs[k] === v));
}

export function matches(node, selector) {
  for (const chain of parseSelector(selector)) {
    if (!one(node, chain[chain.length - 1])) continue;
    let rest = chain.length - 1;
    for (const a of ancestors(node)) {
      if (rest && one(a, chain[rest - 1])) rest--;
    }
    if (!rest) return true;
  }
  return false;
}

const attrOk = (node, k, v) => k in node.attrs && (v === true || node.attrs[k] === v);

function show(node) {
  const a = Object.entries(node.attrs).map(([k, v]) => (v ? `${k}="${v}"` : k)).join(' ');
  const s = `<${node.tag}${a ? ' ' + a : ''}>`;
  return s.length <= 70 ? s : s.slice(0, 67) + '...';
}

const split = (s) => (s || '').split(/\s+/).filter(Boolean);

// Checks the rules of one component on a parsed page. Returns
// {findings, seen}: one line per break, and how many elements the rules saw.
export function check(root, rules, { skip = '[inert]' } = {}) {
  const nodes = [...walk(root)];
  const byId = new Map();
  for (const n of nodes) {
    if (n.attrs.id) {
      if (!byId.has(n.attrs.id)) byId.set(n.attrs.id, []);
      byId.get(n.attrs.id).push(n);
    }
  }
  const gone = new Set();
  if (skip) {
    for (const n of nodes) {
      if (!gone.has(n) && matches(n, skip)) {
        gone.add(n);
        for (const d of walk(n)) gone.add(d);
      }
    }
  }
  const findings = [];
  const seen = new Set();

  for (const r of rules) {
    const tagline = `[${r.id}${r.rule ? ', rule ' + r.rule : ''}]`;
    for (const n of nodes) {
      if (gone.has(n) || !matches(n, r.on)) continue;
      if (Object.entries(r.when || {}).some(([k, v]) => !attrOk(n, k, v))) continue;
      if (r.unless && Object.entries(r.unless).every(([k, v]) => attrOk(n, k, v))) continue;
      seen.add(n);
      const where = `line ${n.line}: ${show(n)}`;
      const fail = (what) => findings.push(`${where} ${what} ${tagline}`);

      if (r.absent) { fail('must not exist'); continue; }
      if (r.tag && !r.tag.includes(n.tag)) {
        fail(`is a <${n.tag}>, must be ${r.tag.map((t) => `<${t}>`).join(' or ')}`);
      }
      if (r.within && ![...ancestors(n)].some((a) => matches(a, r.within))) fail(`outside ${r.within}`);
      if (r.notWithin && [...ancestors(n)].some((a) => matches(a, r.notWithin))) fail(`inside ${r.notWithin}`);
      for (const [k, v] of Object.entries(r.require || {})) {
        if (!attrOk(n, k, v)) fail(`without ${k}` + (v === true ? '' : `="${v}"`));
      }
      const forbid = Array.isArray(r.forbid) ? r.forbid.map((k) => [k, true]) : Object.entries(r.forbid || {});
      for (const [k, v] of forbid) {
        if (attrOk(n, k, v)) fail(`with ${k}` + (v === true ? '' : `="${v}"`));
      }
      for (const h of r.has || []) {
        const found = [...walk(n)].filter((d) => matches(d, h.sel));
        const lo = h.min ?? 1;
        const hi = h.max ?? null;
        if (found.length < lo || (hi !== null && found.length > hi)) {
          const want = hi === lo ? `${lo}` : hi !== null ? `${lo} to ${hi}` : `at least ${lo}`;
          fail(`has ${found.length} ${h.sel}, expected ${want}`);
        }
        if (h.text) for (const d of found) if (!textOf(d)) fail(`${h.sel} without visible text`);
      }
      for (const k of r.ref || []) {
        for (const ref of split(n.attrs[k])) if (!byId.has(ref)) fail(`${k}="${ref}" points to no element`);
      }
      for (const k of r.refText || []) {
        const refs = split(n.attrs[k]);
        if (!refs.length) fail(`without ${k}`);
        for (const ref of refs) {
          if (!byId.has(ref)) fail(`${k}="${ref}" points to no element`);
          else if (!textOf(byId.get(ref)[0])) fail(`${k}="${ref}" points to an element without text`);
        }
      }
      if (r.uniqueId) {
        const i = n.attrs.id;
        if (!i) fail('without id');
        else if (byId.get(i).length > 1) fail(`id "${i}" appears ${byId.get(i).length} times`);
      }
      if (r.referencedBy) {
        const { sel, attr } = r.referencedBy;
        const i = n.attrs.id;
        if (!i || !nodes.some((x) => matches(x, sel) && split(x.attrs[attr]).includes(i))) {
          fail(`no ${sel} points to it through ${attr}`);
        }
      }
    }
  }
  return { findings, seen: seen.size };
}

// Every component's rules on one page: [{component, findings, seen}].
export function checkAll(root, catalog, options) {
  return Object.entries(catalog.components).map(([component, entry]) => ({
    component, ...check(root, entry.rules, options),
  }));
}
